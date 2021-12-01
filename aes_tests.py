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
    l.info(f'AES implementation: {str(aes_impl)}')

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

        l.info("\t\t{}/{}".format(
            aes_mangle_tests.random_block,
            aes_mangle_tests.blocks_count)
            )

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

        # Floor division, because we assume that input arrives padded.
        self.blocks_count = len(self.input) // AES.block_size
        if not self.blocks_count > 1:
            raise TypeError("input must be at least 2 blocks long!")
        self.random_block = randint(1, self.blocks_count)
        self.random_byte = randint(0, AES.block_size-1)

    def remove_block_test(self):
        # Iterate over chunks with index, starting with index 1
        for idx, chunk in enumerate(chunks(self.input, AES.block_size), 1):
            if idx == self.random_block:
                continue
            else:
                yield chunk

    def duplicate_block_test(self):
        to_repeat = None

        for idx, chunk in enumerate(chunks(self.input, AES.block_size), 1):
            if to_repeat is not None:
                yield to_repeat
                to_repeat = None

            if idx == self.random_block:
                to_repeat = chunk

            yield chunk

    def duplicate_block_append_test(self):
        to_repeat = None

        for idx, chunk in enumerate(chunks(self.input, AES.block_size), 1):
            if idx == self.random_block:
                to_repeat = chunk
            yield chunk
        yield to_repeat

    def duplicate_block_replace_test(self):
        to_repeat = None

        for idx, chunk in enumerate(chunks(self.input, AES.block_size), 1):
            if to_repeat is not None:
                yield to_repeat
                to_repeat = None
                continue

            if idx == self.random_block:
                to_repeat = chunk

            yield chunk

    def swap_block_test(self):
        deferred_chunk = None

        for idx, chunk in enumerate(chunks(self.input, AES.block_size), 1):
            if idx == self.random_block:
                deferred_chunk = chunk
                continue
            yield chunk

            if deferred_chunk is not None:
                yield deferred_chunk
                deferred_chunk = None

    def change_random_byte_test(self):
        for idx, chunk in enumerate(chunks(self.input, AES.block_size), 1):
            if idx == self.random_block:
                mutable_chunk = bytearray(chunk)
                mutable_chunk[self.random_byte] = randint(0, 256)
                yield bytes(mutable_chunk)
            else:
                yield chunk
