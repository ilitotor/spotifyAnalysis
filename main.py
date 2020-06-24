import csv
import os
import logging

import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
from decouple import config
import click

# Se algum dia parar na metade, use o comando abaixo para limpar o arquivo
# onde: - 118 é  quantidade de linha que quer apagar de baixo para cimadf.show
# head -$(($(wc -l < top_br.csv) - 118)) top_br.csv > top_br_cut.csv

# Gets or creates a logger
logger = logging.getLogger(__name__)

# Set formatter
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

# set log level
logger.setLevel(logging.DEBUG)

os.environ['SPOTIPY_CLIENT_SECRET'] = config('SPOTIPY_CLIENT_SECRET')
os.environ['SPOTIPY_CLIENT_ID'] = config('SPOTIPY_CLIENT_ID')
os.environ['SPOTIPY_REDIRECT_URI'] = config('SPOTIPY_REDIRECT_URI')

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


@click.command()
@click.option('--regional', '-r')
# @click.option('--missing', '-m') inserir linhas que deram erros
@click.option('--update', '-u')
def main(regional, update):

    # atualiza só uma base
    if regional:
        urls = [f"https://spotifycharts.com/regional/{regional}"]
        arquivos = [f"top_{regional}.csv"]
    else:
        urls = ["https://spotifycharts.com/regional/br", "https://spotifycharts.com/regional/global"]
        arquivos = ['top_br.csv', 'top_global.csv']

    # pegar a lista de datas
    for url, arquivo in zip(urls, arquivos):

        # define file handler
        log_regional_name = url.split("/")[4]
        file_handler = logging.FileHandler('log_'
                                           + datetime.today().strftime('%Y-%m-%d')
                                           + '_' + log_regional_name
                                           + '.log')

        file_handler.setFormatter(formatter)
        # add file handler to logger
        logger.addHandler(file_handler)

        #to not create new header when update file.
        if not update:
            with open(arquivo, mode='a') as csv_file:
                fieldnames = ["track_id", "position", "artist", "name", "streams", "duration_ms",
                              "key", "mode", "time_signature", "acousticness", "danceability", "energy",
                              "instrumentalness", "liveness", "loudness", "speechiness", "valence", "tempo", "date"]
                writer = csv.DictWriter(csv_file, extrasaction='ignore', fieldnames=fieldnames)
                writer.writeheader()

        data = requests.get(url)
        soup = BeautifulSoup(data.content, 'html.parser')

        for divtag in soup.findAll('div', {'data-type': 'date'}):
            for dates in divtag.findAll("li"):
                date = datetime.strptime(dates.attrs.get("data-value", None), "%Y-%m-%d").date()
                if update:
                    date_update = datetime.strptime(update, "%Y-%m-%d").date()
                    if date > date_update:
                        write_csv(date, arquivo, url)
                else:
                    write_csv(date, arquivo, url)
        logger.info('Finalizado ' + arquivo)

    return logger.info('Finalizada atualização')


def write_csv(date_to_save, arquivo, url):
    url = f"{url}/daily/{date_to_save}/download"
    r = requests.get(url)
    data = "\n".join(r.text.split("\n")[1:])
    print(url)
    with open(arquivo, mode='a') as csv_file:
        fieldnames = ["track_id", "position", "artist", "name", "streams", "duration_ms",
                      "key", "mode", "time_signature", "acousticness", "danceability", "energy",
                      "instrumentalness", "liveness", "loudness", "speechiness", "valence", "tempo", "date"]

        writer = csv.DictWriter(csv_file, extrasaction='ignore', fieldnames=fieldnames)

        spotify_data = csv.reader(data.splitlines(), delimiter=',')
        next(spotify_data)  # skip header from spotify file
        
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
    main()

# TO-DO
# RODAR TUDO DENOVO NO GCP
# TRATAR ERROS E MARCAR TRACKS PARA REFAZER
# CRIAR CRON PARA RODAR DIARIAMENTE E SALVAR EM UM BUCKET
