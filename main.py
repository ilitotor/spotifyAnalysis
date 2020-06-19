import csv
import os
import logging

import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
from decouple import config

# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level
logger.setLevel(logging.DEBUG)

# define file handler and set formatter
file_handler = logging.FileHandler('log_' + datetime.today().strftime('%Y-%m-%d') + '.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

os.environ['SPOTIPY_CLIENT_SECRET'] = config('SPOTIPY_CLIENT_SECRET')
os.environ['SPOTIPY_CLIENT_ID'] = config('SPOTIPY_CLIENT_ID')
os.environ['SPOTIPY_REDIRECT_URI'] = config('SPOTIPY_REDIRECT_URI')

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def update_files():
    urls = ["https://spotifycharts.com/regional/br", "https://spotifycharts.com/regional/global"]
    arquivos = ['top_brasil.csv', 'top_global.csv']
    # pegar a lista de datas
    for url, arquivo in zip(urls, arquivos):
        with open(arquivo, mode='w+') as csv_file:
            fieldnames = ["track_id", "position", "artist", "name", "streams", "duration_ms",
                          "key", "mode", "time_signature", "acousticness", "danceability", "energy",
                          "instrumentalness", "liveness", "loudness", "speechiness", "valence", "tempo", "date"]
            writer = csv.DictWriter(csv_file, extrasaction='ignore', fieldnames=fieldnames)
            writer.writeheader()
        get_dates(url, arquivo)
    return logger.info('Fim do processo. Todas as bases foram atualizadas')


def get_dates(url, arquivo):
    url = url
    data = requests.get(url)
    soup = BeautifulSoup(data.content, 'html.parser')

    for divtag in soup.findAll('div', {'data-type': 'date'}):
        for dates in divtag.findAll("li"):
            data = datetime.strptime(dates.attrs.get("data-value", None), "%Y-%m-%d").date()
            write_csv(data, arquivo, url)
    return logger.info('Finalizada atualização ' + arquivo)


def write_csv(date_to_save, arquivo, url):
    url = f"{url}/daily/{date_to_save}/download"
    r = requests.get(url)
    data = "\n".join(r.text.split("\n")[1:])
    print(url)
    with open(arquivo, mode='a') as csv_file:
        fieldnames = ["track_id", "position", "artist", "name", "streams", "duration_ms",
                      "key", "mode", "time_signature", "acousticness", "danceability", "energy",
                      "instrumentalness", "liveness", "loudness", "speechiness", "valence", "tempo", "date"]

        # prepara o arquivo para ser escrito
        writer = csv.DictWriter(csv_file, extrasaction='ignore', fieldnames=fieldnames)

        # le o csv que vem do spotify
        spotify_data = csv.reader(data.splitlines(), delimiter=',')
        next(spotify_data)  # skip first line (head)
        for track in spotify_data:
            details_track = sp.audio_features(track[4])

            dict_name_track = {'track_id': track[4].split("track/")[1], 'position': track[0], 'artist': track[2],
                               'name': track[1], 'streams': track[3],
                               'date': date_to_save}
            try:
                details_track[0].update(dict_name_track)
            except:
                details_track[0] = {'track_id': '', 'position': '', 'artist': '', 'name': '', 'streams': '',
                                    'date': date_to_save}
                details_track[0].update(dict_name_track)
                logger.error('Erro na track: ' + track[4])

            writer.writerow(details_track[0])

    logger.info('Finalizado dia ' + str(date_to_save))
    return print(date_to_save)


if __name__ == "__main__":
    logger.info('Início do processo')
    update_files()

# TO-DO
# RODAR TUDO DENOVO NO GCP
# TRATAR ERROS E MARCAR TRACKS PARA REFAZER
# CRIAR CRON PARA RODAR DIARIAMENTE E SALVAR EM UM BUCKET
