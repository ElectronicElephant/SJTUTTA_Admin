# e-Paper
import os
import logging
from lib.waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

# PN 532
import RPi.GPIO as GPIO
from lib.pn532 import *

logging.basicConfig(level=logging.DEBUG)
picdir = 'pic'

def get_card_id():
    try:
        # pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        #pn532 = PN532_I2C(debug=False, reset=20, req=16)
        pn532 = PN532_UART(debug=False, reset=20)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Waiting for RFID/NFC card...')
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.5)
            print('.', end="")
            # Try again if no card is available.
            if uid is None:
                continue
            print('Found card with UID:', [hex(i) for i in uid])

            return ' '.join([hex(i) for i in uid])

    except Exception as e:
        print(e)
    finally:
        pass
        # GPIO.cleanup()

def main():
    try:
        logging.info("epd2in7 Demo")
        
        epd = epd2in7.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear(0xFF)
        
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        
        # Drawing on the Horizontal image
        logging.info("1.Drawing on the Horizontal image...")
        Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw.text((10, 0), 'SJTUTTA DEMO', font = font24, fill = 0)
        draw.text((150, 30), '® 交大乒协', font = font18, fill = 0)    
        draw.line((20, 50, 70, 100), fill = 0)
        draw.rectangle((20, 50, 70, 100), outline = 0)
        draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
        draw.rectangle((80, 50, 130, 100), fill = 0)
        draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
        epd.display(epd.getbuffer(Himage))
        # time.sleep(2)

        epd.sleep()
        time.sleep(2)
        epd.init()

        # Print a card ID
        logging.info("Priting a card ID...")
        Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw.text((10, 0), 'Getting Card ID...', font = font24, fill = 0)
        draw.text((150, 30), '® 交大乒协', font = font18, fill = 0)    
        epd.display(epd.getbuffer(Himage))
        time.sleep(2)

        # Print a card ID
        for count in range(100):
            logging.info("Priting a card ID...")
            Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(Himage)
            draw.text((10, 0), 'Getting Card ID...', font = font24, fill = 0)
            id_string = get_card_id()
            draw.text((10, 48), f'Got card, count {count}', font = font18, fill = 0)
            draw.text((10, 70), id_string, font = font18, fill = 0)    
            epd.init()
            epd.display(epd.getbuffer(Himage))
            epd.sleep()
        
        # Clear
        logging.info("Clear...")
        epd.Clear(0xFF)
        
        # Sleep
        logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
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
    test_mode = False
    if test_mode:
        test()
    else:
        main()