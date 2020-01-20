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
font_file = 'wqy-zenhei.ttc'
font24 = ImageFont.truetype(os.path.join(picdir, font_file), 24)
font18 = ImageFont.truetype(os.path.join(picdir, font_file), 18)
font10 = ImageFont.load(os.path.join(picdir, 'wenquanyi_10pt.pil'))
font5 = ImageFont.truetype(os.path.join(picdir, font_file), 5)


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
    draw.text((0, 5), 'CARD', font=font10)
    draw.text((0, 70), 'INFO', font=font10)
    draw.text((0, 130), 'DRAW', font=font10)
    draw.text((0, 160), 'SHUT', font=font10)


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
            uid = pn532.read_passive_target(timeout=0.5)
            key = get_key(timeout=0.6)
            # print('.', end="")
            # Try again if no card is available.
            if key:
                return '', key
            if uid is None:
                continue

            logging.info(f'Found card with UID  {[hex(i) for i in uid]}')
            return ''.join([str(hex(i))[2:4] if len(str(hex(i))) == 4 else '0'+str(hex(i))[2] for i in uid]).upper(), 0

    except Exception as e:
        print(e)
    finally:
        pass
        # GPIO.cleanup()


def get_key(timeout=0, loop_delay = 0.1):
    # timeout=0 stands for waiting untill a key pressed

    # Initialize the four keys
    GPIO_PINs = [5, 6, 13, 19]
    # For key 1, 2, 3, 4 respectively
    GPIO.setmode(GPIO.BCM)
    for GPIO_PIN in GPIO_PINs:
        GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    logging.info('Waiting for key press')
    if timeout == 0:
        while True:
            for i, GPIO_PIN in enumerate(GPIO_PINs):
                if(GPIO.input(GPIO_PIN) == 0):
                    logging.info(f"{GPIO_PIN} pin {i+1} key pressed")
                    return i+1
            time.sleep(loop_delay)
    else:
        for _ in range(int(timeout/loop_delay)):
            for i, GPIO_PIN in enumerate(GPIO_PINs):
                if(GPIO.input(GPIO_PIN) == 0):
                    logging.info(f"{GPIO_PIN} pin {i+1} key pressed")
                    return i+1
            time.sleep(loop_delay)
        return 0 # for no key pressed


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
    add_margin(draw)
    draw.text((40, 0), '请刷卡', font=font24, fill=0)
    print_board(Himage)
    
    # Block
    try:
        id_string, key = get_card_id()
    except Exception as e:
        logging.critical(e)
        return 1

    if key:
        return key

    if id_string == None:
        logging.critical("NONE string recived")
        return 1
    user_name = 1
    valid_date = '永久'
    time_date = '2019-07-07 21:00:13'
    last_date = '2019-07-07 21:00:13'
    Himage, draw = new_board('w')
    add_margin(draw)
    draw.text((40, 0), f'欢迎 {user_name}', font=font24, fill=0)
    draw.text((40, 30), f'有效期 {valid_date}', font =font18)
    draw.text((40, 50), f'入馆时间', font=font18)
    draw.text((40, 70), f'         {time_date}', font=font18)
    draw.text((40, 90), f'上次入馆', font=font18)
    draw.text((40, 110), f'         {last_date}', font=font18)
    draw.text((40, 130), f'请勿重复入馆', font=font18)
    print_board(Himage)
    time.sleep(5)
    return 1

def print_debug_info():
    # Print a card ID
    logging.info("Debug mode...")
    Himage, draw = new_board('w')
    draw.text((40, 20), 'Getting Card ID...', font=font10, fill=0)
    print_board(Himage)
    add_margin(draw)
    # Block
    try:
        id_string, key = get_card_id()
    except Exception as e:
        logging.critical(e)
        return 2
    
    if key:
        return key

    if id_string == None:
        logging.critical("NONE string recived")
        return 2
    draw.text((40, 40), f'Got card {id_string}', font=font10, fill=0)
    print_board(Himage)
    time.sleep(5)
    return 2

def draw_block():
    Himage, draw = new_board('w')
    for i in range(0, 176, 20):
        draw.line(((0, i), (264, i)), width=1)
        draw.text((0, i), f'{i}', font=font10)
    for i in range(0, 264, 20):
        draw.line(((i, 0), (i, 176)), width=1)
        draw.text((i, 0), f'{i}', font=font10)
    print_board(Himage)

    return get_key()


def main(key=0):
    if not key:
        welcome()
        key = get_key()

    if key == 1:
        key = print_card()
    elif key == 2:
        key = print_debug_info()
    elif key == 3:
        key = draw_block()
    elif key == 4:
        key = get_key()

    return key


def test():
    pass


if __name__ == '__main__':
    test_mode = False
    if test_mode:
        test()
    else:
        key = main()
        while True:
            key = main(key)
