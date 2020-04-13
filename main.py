import csv
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

# export SPOTIPY_CLIENT_ID='710124b846034b4086c2a18b3f5ff1c7'
# export SPOTIPY_CLIENT_SECRET='93ae108e92dc45c0adb71652acd2424a'
# export SPOTIPY_REDIRECT_URI='http://dev.ilito.com/musicperkm/callback.php'


client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_dates():
    url = "https://spotifycharts.com/regional"
    data = requests.get(url)
    soup = BeautifulSoup(data.content, 'html.parser')

    for divtag in soup.findAll('div', {'data-type': 'date'}):
        for dates in divtag.findAll("li"):
            data_limit = datetime.strptime('2018-12-04', "%Y-%m-%d").date()
            data = datetime.strptime(dates.attrs.get("data-value", None), "%Y-%m-%d").date()
            if  data < data_limit:
                write_csv(data)
    return print("Sucesso")


def write_csv(date_to_save):
    url = f"https://spotifycharts.com/regional/global/daily/{date_to_save}/download"
    r = requests.get(url)
    data = "\n".join(r.text.split("\n")[1:])

    with open('top_global.csv', mode='a') as csv_file:
        fieldnames = ['artist', 'name', 'num_samples', 'duration', 'offset_seconds', 'window_seconds',
                      'analysis_sample_rate', 'analysis_channels', 'end_of_fade_in', 'start_of_fade_out', 'loudness', \
                      'tempo', 'tempo_confidence', 'time_signature', 'time_signature_confidence', 'key',
                      'key_confidence', \
                      'mode', 'mode_confidence', 'code_version', 'echoprint_version', 'synch_version', 'rhythm_version', 'date']

        writer = csv.DictWriter(csv_file, extrasaction='ignore', fieldnames=fieldnames)
        # writer.writeheader()
        data2 = csv.reader(data.splitlines(), delimiter=',')
        next(data2)  # skip first line (head)
        for track in data2:
            details_track = sp.audio_analysis(track[4])
            dict_name_track = {'artist': track[2], 'name': track[1], 'date': date_to_save}
            details_track['track'].update(dict_name_track)
            writer.writerow(details_track['track'])

    return print(date_to_save)


if __name__ == "__main__":
     get_dates()
