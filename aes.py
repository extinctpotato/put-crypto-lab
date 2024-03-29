import logging, hashlib, timeit
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from bbs_generator import bbs_preset

LOGGER_ID = 'aes_logger'
l = logging.getLogger(LOGGER_ID)

def encrypt_single_block(input, key):
    if len(input) != AES.block_size:
        raise TypeError(f"input must be at least {AES.block_size} bytes long!")

    return AES.new(key=key, mode=AES.MODE_ECB).encrypt(input)

def decrypt_single_block(input, key):
    if len(input) != AES.block_size:
        raise TypeError(f"input must be at least {AES.block_size} bytes long!")

    return AES.new(key=key, mode=AES.MODE_ECB).decrypt(input)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def bytes_xor(a, b):
    assert len(a) == len(b)
    return bytes(x ^ y for x, y in zip(a, b))

def gen_bbs_key(r=32):
    return "".join(map(str, bbs_preset(r=32))).encode()

def test_lib():
    key = gen_bbs_key() 
    modes = [m for m in dir(AES) if m.startswith('MODE_')]
    test_files = ['1m', '10m', '100m']

    l.info(f"key len: {len(key)}")

    for test_file in test_files:
        l.info(f"input file: {test_file}")

        with open(f'samples/{test_file}.bin', 'rb') as f:
            for mode in modes:
                l.info(f"\tmode: {mode}")

                mode_const = eval(f'AES.{mode}')

                cipher = AES.new(
                       key=key,
                       mode=mode_const
                       )

                l.info(f"\t\tobject type: {type(cipher)}")

                data = f.read()
                data_md5 = hashlib.md5(data).hexdigest()
                padded_data = pad(data, AES.block_size)

                encryption_start = timeit.default_timer()

                try:
                    encrypted, tag = cipher.encrypt(padded_data), None
                except TypeError:
                    encrypted, tag = cipher.encrypt_and_digest(padded_data)

                encryption_elapsed = timeit.default_timer() - encryption_start

                dec_args = dict()

                try:
                    l.info(f"\t\tnonce: {cipher.nonce}")
                    dec_args['nonce'] = cipher.nonce
                except:
                    l.info("\t\tno nonce")

                try:
                    l.info(f"\t\tiv: {cipher.iv}")
                    dec_args['iv'] = cipher.iv
                except:
                    l.info("\t\tno iv")

                cipher_dec = AES.new(
                        key=key,
                        mode=mode_const,
                        **dec_args
                        )

                decryption_start = timeit.default_timer()

                if tag is None:
                    decrypted = cipher_dec.decrypt(encrypted)
                else:
                    decrypted = cipher_dec.decrypt_and_verify(encrypted, tag)

                decryption_elapsed = timeit.default_timer() - decryption_start

                try:
                    unpadded = unpad(decrypted, AES.block_size)
                except ValueError:
                    unpadded = decrypted

                decrypted_md5 = hashlib.md5(unpadded).hexdigest()

                l.info(f"\t\tpre-hash:  {data_md5}")
                l.info(f"\t\tpost-hash: {decrypted_md5}")
                l.info(f"\t\tencryption time: {encryption_elapsed}")
                l.info(f"\t\tdecryption time: {decryption_elapsed}")

                if data_md5 != decrypted_md5:
                    l.warning("\t\thash mismatch!")

class aesECB:
    def __init__(self, key=None, iv=None):
        self.key = key or gen_bbs_key()
        # ECB doesn't have the concept of initialization vector.
        self.iv = None

    def encrypt(self, input):
        padded_data = pad(input, AES.block_size)

        for chunk in chunks(padded_data, AES.block_size):
            yield encrypt_single_block(
                    input=chunk,
                    key=self.key
                    )

    def decrypt(self, input):
        for chunk in chunks(input, AES.block_size):
            yield decrypt_single_block(
                    input=chunk,
                    key=self.key
                    )

class aesCBC:
    def __init__(self, key=None, iv=None):
        self.key = key or gen_bbs_key()
        self.iv = iv or bbs_preset(r=AES.block_size)

    def encrypt(self, input):
        padded_data = pad(input, AES.block_size)
        b_xor_input = self.iv 

        for chunk in chunks(padded_data, AES.block_size):
            b_xor_input = encrypt_single_block(
                    input=bytes_xor(chunk, b_xor_input),
                    key=self.key
                    )
            yield b_xor_input

    def decrypt(self, input):
        b_xor_input = self.iv

        for chunk in chunks(input, AES.block_size):
            yield bytes_xor(
                    decrypt_single_block(
                        input=chunk,
                        key=self.key
                        ),
                    b_xor_input
                    )
            b_xor_input = chunk

class aesOFB:
    def __init__(self, key=None, iv=None):
        self.key = key or gen_bbs_key()
        self.iv = bytes(iv or bbs_preset(r=AES.block_size))

    def encrypt(self, input):
        if len(input) % AES.block_size == 0:
            padded_data = input
        else:
            padded_data = pad(input, AES.block_size)
        enc_input = self.iv

        for chunk in chunks(padded_data, AES.block_size):
            enc_data = encrypt_single_block(
                    input=enc_input,
                    key=self.key,
                    )
            yield bytes_xor(enc_data, chunk)
            enc_input = enc_data

    def decrypt(self, input):
        return self.encrypt(input)
