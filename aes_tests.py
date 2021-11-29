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

def run_all_tests(aes_impl=aesECB):
    inputs = [
            "a"*AES.block_size*3, 
            ascii_lowercase * 3,
            ARISTOTLE_QUOTE
            ]

    tests = [str(t) for t in dir(AESMangleTests) if t.endswith("_test")]

    for input_idx, input in enumerate(inputs):
        l.info(f'Input {input_idx}')

        # Convert str to bytes.
        input_bytes = input.encode()

        # Initialize AES enc/dec object.
        aes_obj = aes_impl()

        ciphertext = b"".join(
                list(aes_obj.encrypt(input_bytes))
                )

        # Initialize mangler with ciphertext in bytes.
        aes_mangle_tests = AESMangleTests(ciphertext)

        for t in tests:
            l.info(f"\t{t}")

            # Get test function by textual name.
            method_to_call = getattr(aes_mangle_tests, t)

            mangled_ciphertext = b"".join(
                    list(method_to_call())
                    )

            decrypted_mangled_ciphertext = b"".join(
                    list(aes_obj.decrypt(mangled_ciphertext))
                    )

            l.info(f"\t\tmangled:  {mangled_ciphertext}")
            l.info(f"\t\tplaintxt: {input_bytes}")
            l.info(f"\t\tdecrypt:  {decrypted_mangled_ciphertext}")

class AESMangleTests:
    def __init__(self, input):
        self.input = input

    def remove_block_test(self):
        # Floor division, because we assume that input arrives padded.
        blocks = len(self.input) // AES.block_size
        if not blocks > 1:
            raise TypeError("input must be at least 2 blocks long!")

        block_to_skip = randint(1, blocks)

        l.info(f"\t\t{block_to_skip}/{blocks}")

        # Iterate over chunks with index, starting with index 1
        for idx, chunk in enumerate(chunks(self.input, AES.block_size), 1):
            if idx == block_to_skip:
                continue
            else:
                yield chunk

