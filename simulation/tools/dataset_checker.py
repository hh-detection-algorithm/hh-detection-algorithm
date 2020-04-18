import argparse
import os
from pprint import pprint

# COLOR CODES
RED = '\x1b[6;30;91m'
GREEN = '\x1b[6;30;92m'
NORMAL = '\x1b[0m'


def check_dataset(filename):
    try:
        with open(filename) as f:
            entries = f.readlines()

        start = entries[0].split()[0]

        for entry in entries:
            current = entry.split()[0]
            assert (current >= start)
            start = current
    except AssertionError:
        return False
    return True


def output_result(filename):
    if check_dataset(filename=filename):
        print(os.path.basename(filename) + ' --- ' + GREEN + 'PASS' + NORMAL)
    else:
        print(os.path.basename(filename) + ' --- ' + RED + 'FAIL' + NORMAL)


parser = argparse.ArgumentParser(
    description='This script checks and verifies dataset files by iterating through their timestamps'
)

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--input-file', help='filename e.g. 01.dataset')
group.add_argument('--input-folder', help='folder name e.g. ../dataset/IMC2010/')

args = parser.parse_args()
# pprint(args)

if args.input_file:
    output_result(args.input_file)
else:
    if os.path.exists(args.input_folder):
        input_files = sorted([(args.input_folder + '/' + i) for i in os.listdir(args.input_folder)])
        for input_file in input_files:
            output_result(input_file)
    else:
        print('ERROR: The specified folder does not exist!')
