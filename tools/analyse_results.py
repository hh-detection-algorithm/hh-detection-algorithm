import csv
import re
import os
import sys


def analyse_results(result_file_name):
    result_by_top_k = dict()
    with open(result_file_name) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            dataset = row["dataset"]
            top_k = int(row["top_k"])
            accuracy = float(row["accuracy"])

            dataset_name = dataset.split('/')[-2]
            # dataset_name = re.findall("/.*equinix.*dataset/", dataset)[0]
            # print(dataset_name)
            if top_k not in result_by_top_k:
                result_by_top_k[top_k] = list()
                result_by_top_k[top_k].append((dataset_name, accuracy))
            else:
                result_by_top_k[top_k].append((dataset_name, accuracy))

    temp = dict()
    for top_k, entries in result_by_top_k.items():
        for entry in entries:
            dataset_name = entry[0]
            accuracy = entry[1]
            if top_k not in temp:
                temp[top_k] = dict()
            if dataset_name not in temp[top_k]:
                temp[top_k][dataset_name] = list()
                temp[top_k][dataset_name].append(accuracy)
            else:
                temp[top_k][dataset_name].append(accuracy)

    result_by_top_k = temp
    for top_k, entries in result_by_top_k.items():
        for dataset, accuracies in entries.items():
            entries[dataset] = sum(accuracies) / len(accuracies)

    for top_k, entries in result_by_top_k.items():
        accuracies = [entries[dataset] for dataset in entries]
        result_by_top_k[top_k] = sum(accuracies) / len(accuracies)

    print(os.path.basename(result_file_name))
    print(result_by_top_k)
    return result_by_top_k


# Usage: python3 analyse_results.py DIRNAME
# DIRNAME -> directory that contains the csv files output from compare_groundtruth.py
results_path = sys.argv[1]
result_files = [i for i in os.listdir(results_path) if 'csv' in i]
result_files.sort()
print(result_files)
for result_file in result_files:
    analyse_results(results_path + '/' + str(result_file))
