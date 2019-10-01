# e-Paper
import os
import logging
from lib.waveshare_epd import epd2in7
import time
from PIL import Image, ImageDraw, ImageFont
import traceback

# PN 532
import RPi.GPIO as GPIO
from lib.pn532 import *

version = '191001_0.0.3'

logging.basicConfig(level=logging.DEBUG)
picdir = 'pic'
epd = epd2in7.EPD()
logging.info("init and Clear")
epd.init()
epd.Clear(0xFF)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font10 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 10)
font5 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 5)


def init():
    welcome()


def new_board(color):
    if color == 'w':
        Himage = Image.new('1', (epd.height, epd.width), 255)
        draw = ImageDraw.Draw(Himage)
    elif color == 'b':
        Himage = Image.new('1', (epd.height, epd.width), 0)
        draw = ImageDraw.Draw(Himage)
    else:
        logging.critical(
            'The color of the board must be either w(hite) or b(lack)')
        exit()
    return Himage, draw


def print_board(Himage):
    epd.init()
    epd.display(epd.getbuffer(Himage))
    epd.sleep()


def add_margin(draw):
    draw.text((0, 0), 'CARD', font=font10)
    draw.text((0, 40), 'INFO', font=font10)
    draw.text((0, 80), 'DRAW', font=font10)
    draw.text((0, 120), 'SHUT', font=font10)


def get_card_id():
    try:
        # pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        # pn532 = PN532_I2C(debug=False, reset=20, req=16)
        pn532 = PN532_UART(debug=False, reset=20)

        ic, ver, rev, support = pn532.get_firmware_version()
        logging.info(
            'Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        logging.info('Waiting for RFID/NFC card...')
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=1)
            # print('.', end="")
            # Try again if no card is available.
            if uid is None:
                continue
            logging.info(f'Found card with UID  {[hex(i) for i in uid]}')

            return ''.join([str(hex(i))[2:4] if len(str(hex(i))) == 4 else '0'+str(hex(i))[2] for i in uid]).upper()

    except Exception as e:
        print(e)
    finally:
        pass
        # GPIO.cleanup()


def welcome():
    logging.info("Displaying welcome page")
    Himage, draw = new_board('w')
    draw.text((40, 20), 'SJTUTTA ADMIN', font=font24)
    draw.text((150, 60), '® 交大乒协', font=font18)
    draw.text((40, 140), f'Version {version}', font=font10)

    add_margin(draw)
    print_board(Himage)


def print_card():
    # Print a card ID
    logging.info("Priting a card ID...")
    Himage, draw = new_board('w')
    draw.text((10, 0), 'Getting Card ID...', font=font24, fill=0)
    print_board(Himage)
    
    # Block
    id_string = get_card_id()
    
    if id_string == None:
        logging.critical("NONE string recived")
        return
    draw.text((10, 48), f'Got card', font=font18, fill=0)
    draw.text((10, 70), id_string, font=font18, fill=0)
    print_board(Himage)


def draw_block():
    Himage, draw = new_board('w')
    for i in range(0, 176, 20):
        draw.line(((0, i), (264, i)), width=1)
        draw.text((0, i), f'{i}', font=font10)
    for i in range(0, 264, 20):
        draw.line(((i, 0), (i, 176)), width=1)
        draw.text((i, 0), f'{i}', font=font10)
    print_board(Himage)


def main():
    # Initialize the four keys
    GPIO_PINs = [5, 6, 13, 19]
    # For key 1, 2, 3, 4 respectively
    GPIO.setmode(GPIO.BCM)
    for GPIO_PIN in GPIO_PINs:
        GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    logging.info('Waiting for key press')
    pressed_key = 0
    while True:
        for i, GPIO_PIN in enumerate(GPIO_PINs):
            if(GPIO.input(GPIO_PIN) == 0):
                logging.info(f"{GPIO_PIN} pin {i+1} key pressed")
                pressed_key = i + 1
        if pressed_key:
            break
        time.sleep(0.1)

    try:
        if pressed_key == 1:
            print_card()
        elif pressed_key == 2:
            welcome()
        elif pressed_key == 3:
            draw_block()
        elif pressed_key == 4:
            pass

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        # Clear
        logging.info("Clear...")
        epd.Clear(0xFF)

        # Sleep
        logging.info("Goto Sleep...")
        epd.sleep()
        epd2in7.epdconfig.module_exit()
        exit()


def test():
    epd = epd2in7.EPD()
    epd.init()
    # epd.sleep()
    t1 = time.time()
    epd.Clear(0xFF)
    print(f"{time.time()-t1} secs used")
    t1 = time.time()
    epd.Clear(0x00)
    print(f"{time.time()-t1} secs used")
    epd.sleep()

    epd2 = epd2in7.EPD()
    epd2.init()


if __name__ == '__main__':
    init()
    test_mode = False
    if test_mode:
        test()
    else:
        main()
