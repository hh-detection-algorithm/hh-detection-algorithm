#! /usr/bin/python3
import os
import math
import argparse


def write_groundtruth_to_file(timestamp, groundtruth_table, dataset_directory):
    output_path = dataset_directory + '/groundtruth/'

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    timestamp = int(timestamp)

    output_path = dataset_directory + '/groundtruth/' + str(timestamp)
    final_table = generate_output(groundtruth_table)
    with open(output_path, 'w') as f:
        for k in final_table:
            f.write(str(k[0]) + " " + str(k[1]) + "\n")


def generate_output(groundtruth_table):
    sorted_table = sorted(groundtruth_table, key=groundtruth_table.__getitem__, reverse=True)
    final_table = []
    for k in sorted_table:
        final_table.append((k, groundtruth_table[k]))
    return final_table


def preprocess_input(data):
    if not data:
        return None

    data = data.strip()
    data = data.split()

    timestamp = data[0].strip()
    data = data[1:]
    data = ','.join(data)
    return timestamp, data


def replay_dataset(start_time, dataset_directory):
    command = 'for i in `ls -d ' + dataset_directory + "/* | grep .dataset | grep -v windows | grep -v groundtruth | sort --version-sort`; do realpath $i; done"
    datasets = os.popen(command).read().strip().split("\n")

    current = start_time
    groundtruth_table = dict()

    for dataset in datasets:
        print(dataset, 'loaded!')

        with open(dataset) as f:
            data = f.readline().strip()
            data = preprocess_input(data)
            while data:
                timestamp = math.floor(float(data[0]))
                data = data[1]

                if timestamp == current:
                    if data not in groundtruth_table:
                        groundtruth_table[data] = 1
                    else:
                        groundtruth_table[data] = groundtruth_table[data] + 1
                else:
                    write_groundtruth_to_file(current, groundtruth_table, dataset_directory)
                    current = timestamp
                    groundtruth_table = dict()
                    groundtruth_table[data] = 1

                data = f.readline().strip()
                data = preprocess_input(data)

    write_groundtruth_to_file(current, groundtruth_table, dataset_directory)


def get_start_time(dataset_directory):
    # Get all files in sorted order
    command = "for i in `ls -d " + dataset_directory + "* | grep dataset | grep -v windows | sort --version-sort`; do realpath $i; done"
    command = os.popen(command).read().strip()
    files = command.split("\n")

    # Get starting time
    head = os.popen("head -n 1 " + files[0]).read().strip().split()[0]
    head = int(math.floor(float(head)))

    start_time = int(float(head))
    return start_time


def main():
    parser = argparse.ArgumentParser(
        "This script goes through all the dataset files and produces groundtruth files for every second"
    )

    parser.add_argument(
        '--dataset-path', required=True,
        help='load dataset to be fed in to extract the ground truth'
    )

    args = parser.parse_args()
    dataset_directory = args.dataset_path

    start_time = get_start_time(dataset_directory)
    replay_dataset(start_time, dataset_directory)


if __name__ == '__main__':
    main()
