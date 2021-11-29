from Crypto.Util.Padding import pad, unpad
from random import randint
# In-tree modules
from aes import aesECB, aesCBC, aesOFB, chunks

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

