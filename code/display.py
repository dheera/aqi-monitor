import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

is_initialized = False
splash = None

def init(i2c):
    global display, is_initialized, splash

    displayio.release_displays()

    display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
    WIDTH = 128
    HEIGHT = 32
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)
    splash = displayio.Group(max_size=10)
    display.show(splash)
    color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0x000000 # White
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

    splash.append(bg_sprite)
    text = " "
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=3)
    splash.append(text_area)
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=13)
    splash.append(text_area)
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=23)
    splash.append(text_area)
    is_initialized = True

def show(line, text):
    global is_initialized, splash

    if is_initialized:
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=3+10*line)
        splash[1+line] = text_area

