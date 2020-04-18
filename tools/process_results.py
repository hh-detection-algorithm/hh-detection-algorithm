#! /usr/bin/python3

import argparse
import pprint
import os


class ResultsExtractor():
    def __init__(self, args):
        self.dataset_path = args.dataset_path  # ~/data/IMC2010DC1/
        self.groundtruth_path = self.dataset_path + '/groundtruth/'
        self.result_path = args.result_path  # ~/data/IMC2010DC1/results/10/CMSPAge.3.1530/
        self.output_path = args.output_path

        self.output_file_basename = os.path.basename(os.path.dirname(self.result_path))  # CMSPAge.3.1530
        self.interval_size = int(os.path.basename(os.path.dirname(os.path.dirname(self.result_path))))  # 10

        self.top_k = args.top_k
        self.look_back_periods = [self.interval_size / 2, self.interval_size, self.interval_size * 2]
        self.look_back_periods = [int(i) for i in self.look_back_periods]

        self.groundtruths = sorted(os.listdir(self.groundtruth_path))
        self.output_files = []

    def debug(self):
        print(self.output_file_basename)
        print(self.interval_size)
        print(self.top_k)
        print(self.look_back_periods)

    def get_dataset_boundaries(self, subdataset):
        subdataset = os.path.join(self.dataset_path, subdataset)
        with open(subdataset) as f:
            entries = f.read().splitlines()
            start = int(float(entries[0].split()[0]))
            end = int(float(entries[-1].split()[0]))
        return start, end

    def look_back(self, look_back_groundtruths):
        groundtruth = dict()
        for look_back_groundtruth in look_back_groundtruths:
            with open(look_back_groundtruth) as f:
                for data in f:
                    data = data.strip()
                    data = data.split()
                    ip = data[0]
                    count = int(data[1])
                    if ip not in groundtruth:
                        groundtruth[ip] = count
                    else:
                        groundtruth[ip] = groundtruth[ip] + count
        return sorted(groundtruth, key=groundtruth.__getitem__, reverse=True)

    def get_top_k(self, groundtruth, snapshot):
        max_k = max(self.top_k)
        max_k = min(max_k, len(groundtruth))
        max_k_entries = groundtruth[:max_k]

        temp_snapshot = []
        with open(snapshot) as f:
            for data in f:
                data = data.strip()
                data = data.split()
                temp_snapshot.append((data[0], int(data[1]), int(data[2])))

        # normalize snapshot data for aging-factor variants
        if 'HashPage' or 'CMSPAge' in self.output_file_basename:
            max_window = max(i[2] for i in temp_snapshot)
            normalized_snapshot = []
            for temp in temp_snapshot:
                ip, count, win = temp
                count = count >> (max_window - win)
                normalized_snapshot.append((ip, count, win))
            temp_snapshot = sorted(normalized_snapshot, key=lambda tup:tup[1], reverse=True)

        # remove all the duplicates
        temp_snapshot_dict = dict()
        for temp in temp_snapshot:
            ip, count, win = temp
            if ip not in temp_snapshot_dict:
                temp_snapshot_dict[ip] = count
            else:
                temp_snapshot_dict[ip] += count
        temp_snapshot = sorted(temp_snapshot_dict, key=temp_snapshot_dict.__getitem__, reverse=True)

        sorted_snapshot = temp_snapshot[:max_k]

        results_output = []
        for k in self.top_k:
            current_k = k
            if k >= len(groundtruth):
                k = len(groundtruth)

            if k == 0:
                continue

            count = 0
            temp_groundtruth = max_k_entries[:k]
            temp_snapshot = sorted_snapshot[:k]
            for s in temp_snapshot:
                if s in temp_groundtruth:
                    count = count + 1
            recall = ((count * 1.0) / (k * 1.0)) * 100
            results_output.append(
                (os.path.basename(os.path.dirname(snapshot)), os.path.basename(snapshot), current_k, recall))
        return results_output

    def compare_groundtruth(self, start, snapshots, look_back):
        results_output = []
        for snapshot in snapshots:
            current_snapshot = os.path.basename(snapshot)

            look_back_groundtruths = []
            for i in range(int(current_snapshot) - look_back, int(current_snapshot)):
                if i >= start and str(i) in self.groundtruths:
                    look_back_groundtruths.append(str(i))

            look_back_groundtruths = [os.path.join(self.groundtruth_path, i) for i in look_back_groundtruths]
            groundtruth = self.look_back(look_back_groundtruths)
            results_output.extend(self.get_top_k(groundtruth, snapshot))
        return results_output

    def output_to_csv(self, look_back, results):
        output_file_basename = os.path.basename(os.path.dirname(self.result_path))

        output_path = self.output_path + '/' + str(self.interval_size) + '/'
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        output_path = output_path + output_file_basename + '.' + str(look_back) + '.csv'

        with open(output_path, 'w') as f:
            f.write('subdataset,snapshot,top_k,recall\n')
            for result in results:
                f.write(str(result[0]) + ',' + str(result[1]) + ',' + str(result[2]) + ',' + str(result[3]) + '\n')
        self.output_files.append(output_path)
        print('Wrote file', output_path)

    def extract_results(self):
        self.subdatasets = [os.path.join(self.result_path, i + '/') for i in os.listdir(self.result_path)]
        for look_back in self.look_back_periods:
            results = []

            for subdataset in self.subdatasets:
                subdataset_name = os.path.basename(os.path.dirname(subdataset))
                print('LBT = ' + str(look_back) + ', Current subdataset ==> ' + subdataset_name)

                start, end = self.get_dataset_boundaries(subdataset_name)

                snapshots = sorted(os.listdir(subdataset))
                snapshots = [os.path.join(subdataset, i) for i in snapshots]

                results.extend(self.compare_groundtruth(start, snapshots, look_back))
            self.output_to_csv(look_back, results)
        return self.output_files


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset-path', required=True)
    parser.add_argument('--result-path', required=True)
    parser.add_argument('--output-path', required=True)
    parser.add_argument('--top-k', type=int, nargs='+', default=[20, 60, 150, 300, 500, 1000])

    args = parser.parse_args()
    pprint.pprint(args)

    results_extractor = ResultsExtractor(args)
    output_files = results_extractor.extract_results()
    print(output_files)


if __name__ == '__main__':
    main()
