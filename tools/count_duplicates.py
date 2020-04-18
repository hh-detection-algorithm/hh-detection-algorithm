import sys
import os


def count_duplicates(dirname, memory):
    duplicate_counts = dict()
    dataset_folders = os.listdir(result_path)
    for dataset in dataset_folders:
        dataset_path = dirname + '/' + dataset + '/'
        dataset_result_files = os.listdir(dataset_path)
        for dataset_result in dataset_result_files:
            dataset_result_file_path = dataset_path + dataset_result
            with open(dataset_result_file_path) as f:
                existing_keys = set()
                duplicate_count = 0
                data = f.readline()
                while data:
                    data = data.split(" ")
                    key = data[0]
                    if key not in existing_keys:
                        existing_keys.add(key)
                    else:
                        duplicate_count += 1
                    data = f.readline()
            duplicate_counts[dataset_result] = (duplicate_count / memory) * 100
    duplicate_percentage = [val for key, val in duplicate_counts.items()]
    print(dirname + "," + str(sum(duplicate_percentage) / len(duplicate_percentage)))


# Usage: python3 count_duplicates.py DIRNAME
# i.e. DIRNAME -> results/HashPipe.6.4500/

result_path = sys.argv[1]
memory = int(os.path.dirname(result_path).split(".")[2])
count_duplicates(result_path, memory)
