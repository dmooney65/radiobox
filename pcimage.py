# text-content-to-pc.py  
from time import sleep
from PIL import Image, ImageDraw, ImageFont, ImageShow
# Import Luma.OLED libraries  
from luma.core.interface.serial import spi  
from luma.core.render import canvas
from luma.oled.device import ssd1309 #, sh1106
# Configure the serial port  
serial = spi(port=0, device=1, gpio_RST=6, bus_speed_hz=1000000)
#serial = spi(device=0, port=0)  device = ssd1309(serial)  
frameSize = (128, 64)    
device = ssd1309(serial)

def main():      
    image = Image.new('1', (frameSize), 'white')      
    font = ImageFont.truetype("LiberationSans-Regular.ttf", 12, encoding="unic")      
    draw = ImageDraw.Draw(image)            
    draw.rectangle([(1,1), (frameSize[0]-2,frameSize[1]-2)], 'black', 'white')      
    draw.text((5, 5), 'Hello World', fill='white', font=font) 
    # Output to OLED/LCD display  
    #device.display(image)   
    # Output to PC image viewer      
    image.save('./image.png')
    image.show(title='hello')            
    #ImageShow.show(image)
    sleep(5)        

if __name__ == "__main__":      
    main()
