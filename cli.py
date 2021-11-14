import sys, argparse
from bbs_generator import bbs_preset
from fips import run_all_tests as run_all_fips_tests

def bbs_preset_func(arg):
    run_all_fips_tests(bbs_preset())

def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    bbs_preset_arg = subparsers.add_parser("bbs_preset")
    bbs_preset_arg.set_defaults(func=bbs_preset_func)

    return parser

if __name__ == '__main__':
    parser = get_parser()

    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)
