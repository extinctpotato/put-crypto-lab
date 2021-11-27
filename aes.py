import logging, hashlib, timeit
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from bbs_generator import bbs_preset

LOGGER_ID = 'aes_logger'
l = logging.getLogger(LOGGER_ID)

def test_lib():
    key = "".join(map(str, bbs_preset(r=32))).encode()
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
