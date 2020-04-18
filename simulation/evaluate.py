#! /usr/bin/python3

from pprint import pprint
from algorithms import get_algorithm
import argparse


def main():
    parser = argparse.ArgumentParser()

    # available algorithms
    parser.add_argument(
        '--algorithm', type=str, default='hashpipe',
        choices=['hashpipe', 'ss', 'cms'],
        help='select algorithm to be evaluated'
    )

    # algorithm variants
    parser.add_argument(
        '--aging-factor', default=False, action='store_true',
        help='use the aging factor variant of the algorithm'
    )

    parser.add_argument(
        '--sliding-window', default=False, action='store_true',
        help='use the sliding window variant of the algorithm'
    )

    # algorithm specifications
    parser.add_argument(
        '--num-counters', type=int, default=4890,
        help='total number of counters to be used (default:4890)'
    )
    parser.add_argument(
        '--num-stages', type=int, default=6,
        help='total number of stages/ rows, applicable for HashPipe/ CMS (default:6)'
    )

    # interval/ window specifications
    parser.add_argument(
        '--interval-size', type=int, default=10,
        help='interval size for hashpipe'
    )

    parser.add_argument(
        '--window-size', type=int, default=10,
        help='window size'
    )

    # window offset for sliding window
    parser.add_argument(
        '--window-offset', type=int, default=1,
        help='window offset applicable for the sliding window variant of the algorithm'
    )

    # file-paths
    parser.add_argument(
        '--dataset-path', required=True,
        help='load dataset to be fed in and evaluated against ground truth'
    )

    args = parser.parse_args()
    pprint(args)
    hh_algorithm = get_algorithm.get_algorithm(args)
    hh_algorithm.replay_dataset()


if __name__ == '__main__':
    main()
