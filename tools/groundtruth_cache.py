import sys
import os
import argparse
import math

LBTs = [2, 5, 10, 15, 20, 25, 30]

parser = argparse.ArgumentParser()
parser.add_argument('--dataset-path')

args = parser.parse_args()
dataset_path = args.dataset_path
groundtruth_path = dataset_path + '/groundtruth/'
groundtruth_cache_path = dataset_path + '/groundtruth_cache/'

if not os.path.exists(groundtruth_cache_path):
    os.mkdir(groundtruth_cache_path)

datasets = os.listdir(dataset_path)
datasets = [(dataset_path + '/' + dataset) for dataset in datasets if 'dataset' in dataset]
print(datasets)

for dataset in datasets:
    with open(dataset) as f:
        entries = f.readlines()
    lower_bound = int(math.floor(float(entries[0].split()[0])))
    upper_bound = int(math.ceil(float(entries[-1].split()[0])))

    temp = [i for i in range(lower_bound, upper_bound+1)]
    for LBT in LBTs:
        QATs = [t for t in temp if lower_bound + LBT <= t <= upper_bound]
        for QAT in QATs:
            look_backs = [t for t in range(QAT-LBT, QAT)]
            look_backs = [groundtruth_path + str(t) for t in look_backs]

            true_counts = dict()
            for look_back in look_backs:
                if not os.path.exists(look_back):
                    continue

                with open(look_back) as f:
                    entries = f.readlines()

                for entry in entries:
                    entry = entry.strip().split()
                    key = entry[0]
                    val = int(entry[1])
                    if not key in true_counts:
                        true_counts[key] = val
                    else:
                        true_counts[key] += val

            true_counts_sorted = sorted(true_counts, key=true_counts.__getitem__, reverse=True)
            true_counts_sorted = true_counts_sorted[:1000]  # top-1000 only

            cache_file = groundtruth_cache_path + str(QAT) + '.' + str(LBT)
            with open(cache_file, 'w') as f:
                for key in true_counts_sorted:
                    f.write(str(key) + " " + str(true_counts[key]) + "\n")

    # groundtruths = sorted(os.listdir(groundtruth_path))
    # groundtruths = [groundtruth for groundtruth in groundtruths if lower_bound <= int(groundtruth) < upper_bound]
    #
    # for LBT in LBTs:
    #     gts = [groundtruth for groundtruth in groundtruths if lower_bound + LBT <=int(groundtruth) < upper_bound] # TBD
    #     for gt in gts:
    #         gt = int(gt)
    #         # look back is not inclusive of the point of query. e.g. query at 7th second, only includes 5, 6th second if LBt = 2
    #         lookbacks = [groundtruth_path + str(i) for i in range(gt-LBT, gt)]
    #
    #         true_counts = dict()
    #         for lookback in lookbacks:
    #             with open(lookback) as f:
    #                 entries = f.readlines()
    #
    #             for entry in entries:
    #                 entry = entry.strip().split()
    #                 key = entry[0]
    #                 val = entry[1]
    #                 if not key in true_counts:
    #                     true_counts[key] = val
    #                 else:
    #                     true_counts[key] += val
    #
    #         # print(len(true_counts))
    #         true_counts_sorted = sorted(true_counts, key=true_counts.__getitem__, reverse=True)
    #         true_counts_sorted = true_counts_sorted[:1000] # top-1000 only
    #
    #         cache_file = groundtruth_cache_path + str(gt) + '.' + str(LBT)
    #         with open(cache_file, 'w') as f:
    #             for key in true_counts_sorted:
    #                 # print(str(key) + " " + str(true_counts[key]))
    #                 f.write(str(key) + " " + str(true_counts[key]) + "\n")
    #         print(cache_file, len(true_counts_sorted))