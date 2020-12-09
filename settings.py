from configparser import ConfigParser
from dotenv import load_dotenv
import os
import logging
from re import sub, search
from decimal import Decimal

load_dotenv()

API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')

assert API_ID and API_HASH

configur = ConfigParser()
configur.read('config.ini')

forwards = configur.sections()

def parse_message(message: str) -> tuple:
    """docstring for parse_message"""
    '0811 !新華文軒 買入訊號 @4.98(1.4%) 成交額 $4.3M 目標價 $5.24 止蝕價 $4.72 目標升幅 5.2% 止損 5.2% 一手 $4980 命中率 2020 0/1, 2019 1/1, 歷史 16/24(67%) [9/12/2020]'
    
    _splits = message.split(' ')
    instrument = _splits[0]
    tp = Decimal( sub(r'[^\d.]', '', _splits[_splits.index('目標價') + 1]) )
    sl = Decimal( sub(r'[^\d.]', '', _splits[_splits.index('止蝕價') + 1]) )
    signal_date = search(r'\[.*\]', message).group(0)
    return instrument, tp, sl, signal_date


def get_forward(forward: str) -> tuple:
    try:
        from_chat = configur.get(forward, 'from')
        to_chat = configur.get(forward, 'to')
        offset = configur.getint(forward, 'offset')
        return from_chat, to_chat, offset
    except Exception as err:
        logging.exception(
            'The content of %s does not follow format. See the README.md file for more details. \n\n %s', forward, str(err))
        quit()


def update_offset(forward: str, new_offset: str) -> None:
    try:
        configur.set(forward, 'offset', new_offset)
        with open('config.ini', 'w') as cfg:
            configur.write(cfg)
    except Exception as err:
        logging.exception(
            'Problem occured while updating offset of %s \n\n %s', forward, str(err))


if __name__ == "__main__":
    # testing
    for forward in forwards:
        print(forward, get_forward(forward))
