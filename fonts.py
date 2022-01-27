import os
from math import ceil, floor
from PIL import ImageFont

def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)

font_default = "LiberationSans-Regular.ttf"
font_bold = "LiberationSans-Bold.ttf"
font_italic = "LiberationSans-Italic.ttf"
font_icon = font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', "MaterialDesignIconsDesktop.ttf"))
font_tiny = font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', 'C&C Red Alert [INET].ttf'))
font_fixed = "LiberationMono-Regular.ttf"

size_default = 14

star = chr(0xF04CE)
play_pause = chr(0xF040E) #"󰐎"
play = chr(0xF040A) #"󰐊"
pause = chr(0xF03E4) #"󰏤"
stop = chr(0xF04DB) #"󰓛"
skip_next = chr(0xF04AD) #"󰒭"
skip_previous = chr(0xF04AE) #"󰒮"
fast_forward = chr(0xF0211)
rewind = chr(0xF045F)

bluetooth = chr(0xF00AF) #"󰂯"
bluetooth_audio = chr(0xF00B0) #"󰂰"
bluetooth_connect = chr(0xF00B1) #"󰂱"
bluetooth_off = chr(0xF00B2) #"󰂲"

home = chr(0xF02DC) #"󰋜"
menu = chr(0xF035C) #"󰍜"
menu_swap = chr(0xF0A64) #"󰩤"
menu_up = chr(0xF0360) #"󰍠"
menu_down = chr(0xF035D) #"󰍝"
menu_right = chr(0xF035F) #"󰍟"
menu_left = chr(0xF035E) #"󰍞"
menu_open = chr(0xF0BAB) #"󰮫"

radio = chr(0xF0439) #"󰐹"
radio_off = chr(0xF121C) #"󱈜"
radio_fm = chr(0xF0CBF) #"󰲿"

raspberry_pi = chr(0xF043F) #"󰐿"
hammer_wrench = chr(0xF1323)
ip = chr(0xF0A5F)
music = chr(0xF075A) #"󰝚"
music_off = chr(0xF075B) #"󰝛"
google_downasaur = chr(0xF1362)
reload_icon = chr(0xF0453)
temperature_celsius = chr(0xF0504)
coolant_temp = chr(0xF03C8)

playlist_edit = chr(0xF0900)
playlist_play = chr(0xF0411) #"󰐑"
playlist_plus = chr(0xF0412) #"󰐒"
playlist_minus = chr(0xF0410) #"󰐐"
playlist_remove = chr(0xF0413) #"󰐓"
playlist_music = chr(0xF0CB8) #"󰲸"
playlist_star = chr(0xF0DF2)
shuffle = chr(0xF049D)
shuffle_disabled = chr(0xF049E)

text_search = chr(0xF13B8) #"󱎸"
layers_search = chr(0xF1206) #"󱈆"

plus = chr(0xF0415)# "󰐕"
minus = chr(0xF0374) #"󰍴"
lightning = chr(0xF140B)

face_profile = chr(0xF0644) #"󰙄"
face = chr(0xF0643) #"󰙃"
album = chr(0xF0025) #"󰀥"
account_artist = chr(0xF0004) #"󰀄"
account_music = chr(0xF0803) #"󰠃"
file_music = chr(0xF0223) #"󰈣"
folder_music = chr(0xF1359) #"󱍙"
tag = chr(0xF04F9) #"󰓹"

volume_off = chr(0xF0581) #"󰖁"
volume_high = chr(0xF057E) #"󰕾"

brightness = chr(0xF00DF) #"󰃟"
ip_network = chr(0xF0A60) #"󰩠"
wifi = chr(0xF05A9) #"󰖩"
access_point = chr(0xF0003) #"󰀃"
access_point_network = chr(0xF0002) #"󰀂"
access_point_network_off = chr(0xF0BE1) #"󰯡"

def getHeightAndWrap(font, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    width, height = font.getsize(text)

    f_width = ceil(width/len(text)) 
    if width > 0:
        wrap = floor(126//(f_width))# - 1 #usable display width / width per char avg rounding up
    return (height, wrap)
