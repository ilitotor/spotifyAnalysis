import csv
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#https://open.spotify.com/playlist/37i9dQZF1DX0FOF1IUWK1W?si=CLr6RI78SmmE2fuzCQfOdg
tracks = sp.playlist_tracks('37i9dQZF1DX0FOF1IUWK1W')

#r = requests.get("https://spotifycharts.com/regional/global/daily/latest/download")
r = requests.get("https://spotifycharts.com/regional/br/daily/latest/download")
# print (r.text)
data = "\n".join(r.text.split("\n")[1:])

with open('top200_br.csv', mode='w') as csv_file:
    fieldnames = ['artist', 'name', 'num_samples', 'duration', 'offset_seconds', 'window_seconds',
                  'analysis_sample_rate', 'analysis_channels', 'end_of_fade_in', 'start_of_fade_out', 'loudness', \
                  'tempo', 'tempo_confidence', 'time_signature', 'time_signature_confidence', 'key', 'key_confidence', \
                  'mode', 'mode_confidence', 'code_version', 'echoprint_version', 'synch_version', 'rhythm_version']

    writer = csv.DictWriter(csv_file, extrasaction='ignore', fieldnames=fieldnames)
    writer.writeheader()
    data2 = csv.reader(data.splitlines(), delimiter=',')
    next(data2) #skip first line (head)
    for track in data2:
        details_track = sp.audio_analysis(track[4])
        print (details_track)
        break
        dict_name_track = {'artist': track[2], 'name': track[1]}
        details_track['track'].update(dict_name_track)
        writer.writerow(details_track['track'])




