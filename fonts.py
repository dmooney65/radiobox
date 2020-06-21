import os
import math
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
#font_icon = "MaterialDesignIconsDesktop.ttf"

size_default = 14

play_pause = chr(0xF040E) #"󰐎"
play = chr(0xF040A) #"󰐊"
pause = chr(0xF03E4) #"󰏤"
stop = chr(0xF04DB) #"󰓛"
skip_next = chr(0xF04AD) #"󰒭"
skip_previous = chr(0xF04AE) #"󰒮"
fast_forward = chr(0xF0211)
rewind = chr(0xF045F)

bluetooth = "󰂯"
bluetooth_audio = "󰂰"
bluetooth_connect = "󰂱"
bluetooth_off = "󰂲"

home = "󰋜"
menu = "󰍜"
menu_swap = "󰩤"
menu_up = "󰍠"
menu_down = "󰍝"
menu_right = "󰍟"
menu_left = "󰍞"
menu_open = "󰮫"

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

playlist_play = "󰐑"
playlist_plus = "󰐒"
playlist_minus = "󰐐"
playlist_remove = "󰐓"
playlist_music = "󰲸"

text_search = "󱎸"
layers_search = "󱈆"

plus = "󰐕"
minus = "󰍴"

face_profile = "󰙄"
face = "󰙃"
album = "󰀥"
account_artist = "󰀄"
account_music = "󰠃"
file_music = "󰈣"
folder_music = "󱍙"
tag = "󰓹"

volume_off = "󰖁"
volume_high = "󰕾"

brightness = "󰃟"
ip_network = "󰩠"
wifi = "󰖩"
access_point = "󰀃"
access_point_network = "󰀂"
access_point_network_off = "󰯡"

def getHeightAndWrap(font, text='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    width, height = font.getsize(text)

    f_width = math.ceil(width/len(text)) 
    if width > 0:
        wrap = 162//(f_width)  #usable display width / width per char avg rounding up
    return (height, wrap)

#text = "Journalist and author Ella Whelan asks if contemporary feminism is - well - dead."
#font = ImageFont.truetype(font_default, size=10)
#width, height = font.getsize(text)
#print(width, height)
#f_width = width/len(text)
#wrap = 20 #default value
#print(f_width)
#if width > 0:
#wrap = 162//(f_width) - (width % f_width > 0) #usable display width / width per char avg rounding up
#print(wrap)
