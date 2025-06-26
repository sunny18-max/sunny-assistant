import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="cda0f86462644b37ad14b705f9b6aa12",
    client_secret="455eedef520d4d4a9381ee838f1ba210",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-playback-state user-modify-playback-state"
))

# List devices to test permissions
print(sp.devices())