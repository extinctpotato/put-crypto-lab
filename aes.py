from Crypto.Cipher import AES
from bbs_generator import bbs_preset

def test_lib():
    key = "".join(map(str, bbs_preset(n=128))).encode()
    modes = [m for m in dir(AES) if m.startswith('MODE_')]
    test_files = ['1m', '10m', '100m']

    for test_file in test_files:
        with open(f'samples/{test_file}.bin', 'r') as f:

        for mode in modes:
            cipher = AES.new(
                   key=key,
                   mode=eval(f'AES.{mode}')
                   )

