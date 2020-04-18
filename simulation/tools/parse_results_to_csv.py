#!/usr/bin/python
import argparse
import os

# COLORIZING - which probably will not be used :D
none = '\033[0m'
bold = '\033[01m'
disable = '\033[02m'
underline = '\033[04m'
reverse = '\033[07m'
strikethrough = '\033[09m'
invisible = '\033[08m'

black = '\033[30m'
red = '\033[31m'
green = '\033[32m'
orange = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'
cyan = '\033[36m'
lightgrey = '\033[37m'
darkgrey = '\033[90m'
lightred = '\033[91m'
lightgreen = '\033[92m'
yellow = '\033[93m'
lightblue = '\033[94m'
pink = '\033[95m'
lightcyan = '\033[96m'
CBLINK = '\33[5m'
CBLINK2 = '\33[6m'


# ------ =================================== -----


def analyze(filename):
    if not os.path.isfile(filename):
        print("{}Cannot load {}! Check path{}!".format(red, filename, none))
        exit(-1)
    # for the results: dict(dict())
    # e.g., one result will be found as hashpipe.10 : {20: 89, 50: 85}
    results = dict()
    # reading the file
    with open(filename, 'r') as lines:
        line_num = 1  # we might need the number of lines later
        res_name = ""
        for line in lines:
            # remove blank spaces
            line = line.strip()
            # remove blank lines
            if line:
                if (line.startswith("[", 0,
                                    1)):  # if line starts with '[' -> don't care (khoois output has this first line)
                    continue
                # OTHERWISE, two outputs are possible
                # check the first line: if it is starting with '/' then we parse out the scenario's name
                if ".csv" in line:
                    l = line.split('/')
                    # if len(l) > 1: #the line is the path for the res file
                    # e.g., /mnt/c/Users/khooi/Desktop/nov08_results_0510/hashpage.10.csv
                    res_name = l[-1]  # get the last element after the last '/'
                    res_name = res_name[:-4]  # remove '.csv'
                    # print(res_name)
                    results[res_name] = dict()  # create a key in the main dict()
                else:  # Otherwise, the corresponding results are being read
                    # example: {20: 84.2777777777778, 60: 79.0925925925926, 150: 74.52592592592593, 300: 72.71481481481482, 500: 72.67555555555556, 1000: 64.37555555555554}
                    l = line[1:]  # get rid of the first curly bracket
                    l = l[:-1]  # get rid of the last curly bracket
                    l = l.split(',')  # make a list of key-value pairs
                    for i in l:
                        a = i.split(':')  # (20: 84.2777777777778)
                        # store the key-values in the sub-dict()
                        results[res_name][int(a[0].strip())] = a[1].strip()

    # --------  This is just for somewhat ordered results from the dict --------
    keys = list()
    # get a key from the dictionary to get the top-k numbers
    tmp_key = next(iter(results))
    for i in results[tmp_key].keys():
        keys.append(i)
    keys.sort()
    # print keys

    # get the algorithms name sorted, otherwise walking through the results dict() is "full random"
    algorithms = list()
    for alg in results.keys():
        algorithms.append(alg)
    algorithms.sort()
    # print algorithms

    len_res = len(results)
    # print(len_res)
    i = 0
    print("k,", end=""),
    for alg in algorithms:
        if (i < len_res - 1):
            print("{},".format(alg), end=""),
        else:
            print("{}".format(alg), end="\n")
        i += 1
    # print("")
    # ==========================================================================

    # Finally, the somewhat ordered resuls
    for k in keys:
        print("{},".format(k), end=""),
        len_res = len(results)
        # print(len_keys)
        i = 0
        for res in algorithms:
            if (i < len_res - 1):
                print("{},".format(results[res][k]), end=""),
            else:
                print("{}".format(results[res][k]), end="\n")
            i += 1
    # -------------------------------------


"""------------------------------------------"""
""" End of functions, execution starts here: """
"""------------------------------------------"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Usage:  python3 parse_results_to_csv.py -i final.random.results")
    parser.add_argument(
        '-i', '--input', nargs=1,
        help="Specify the name of the file containing the results ",
        required=True
    )

    args = parser.parse_args()
    input = args.input[0]

    # Start analyzation
    analyze(input)
