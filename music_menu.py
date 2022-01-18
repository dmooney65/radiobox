from luma.core.render import canvas
import fonts
import top_menu
import menu
import playing_menu
import artist_menu
import album_menu
import files_menu
import playlist_menu
import controls
from MPD2_Client import Client
from display import Oled

device = Oled().get_device()
client = Client()

items = [(fonts.menu_up, 'Back'), (fonts.playlist_music, 'Queue'), (fonts.account_music, 'Artists'),
         (fonts.album, 'Albums'), (fonts.folder_music, 'Files'), (fonts.playlist_music, 'Saved Playlists'), 
         (fonts.playlist_plus, 'Random playlist')]

def menu_operation(index):
    if index == 1:
        #controls.state.timer.cancel()
        playing_menu.init(1)
    elif index == 2:
        artists = client.get_list('artist')
        artist_menu.init(2, __name__, artists)
    elif index == 3:
        albums = client.get_list('album')
        album_menu.init(3, __name__, albums)
    elif index == 4:
        files_menu.init(4, __name__, ['file:///mnt/music'])
    elif index == 5:
        playlists = client.list_playlists()
        playlist_menu.init(5, __name__, playlists)
    elif index == 6:
        client.random_playlist(250)
        playing_menu.init(3)
    else:
        top_menu.init(0)

def draw_menu(val):
    with canvas(device) as draw:
        menu.draw_menu(device, draw, items, val % len(items), font_size = 11, icon_size = 12)

def cb_rotate(val):
    draw_menu(val)


def cb_switch(val):
    menu_operation(val % len(items))


def open(val):
    init(val)


def init(val):
    #client.replayGain('none')
    draw_menu(val)
    controls.init(__name__, val)
