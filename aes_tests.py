import logging
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from random import randint
from string import ascii_lowercase
# In-tree modules
from aes import aesECB, aesCBC, aesOFB, chunks

LOGGER_ID = 'aes_tests'
l = logging.getLogger(LOGGER_ID)

ARISTOTLE_QUOTE = """\
We should venture on the study of every kind of animal without distaste; \
for each and all will reveal to us something natural and something beautiful.
"""

def run_all_tests():
    inputs = [
            "a"*AES.block_size*3, 
            ascii_lowercase * 3,
            ARISTOTLE_QUOTE
            ]

    for input in inputs:
        l.info(input)

class AESMangleTests:
    def __init__(self, input, mode=None):
        if len(input) % AES.block_size == 0:
            self.input = input
        else:
            self.input = pad(input, AES.block_size)
        self.mode = mode or aesCBC

    def remove_block(self):
        # Floor division, because we assume that input has already been padded.
        blocks = len(self.input) // AES.block_size
        if not blocks > 1:
            raise TypeError("input must be at least 2 blocks long!")

        block_to_skip = randint(1, blocks)

        # Iterate over chunks with index, starting with index 1
        for idx, chunk in enumerate(chunks(self.input, AES.block_size), 1):
            if idx == block_to_skip:
                continue
            else:
                yield chunk

