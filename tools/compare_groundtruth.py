#! /usr/bin/python3
import os
import argparse
import random
from pprint import pprint


class GroundTruthComparator():
    def __init__(self, args):
        self.look_back_periods = args.look_back_periods
        self.top_k = args.top_k
        self.interval_size = args.interval_size

        self.random_iterations = args.random_iterations
        self.query_per_iteration = args.num_queries

        self.duplicates = args.duplicates
        self.WINDOW_OFFSET = args.window_offset

        self.dataset_path = args.dataset_path
        self.ground_truth_path = args.dataset_path + '/groundtruth'
        self.result_path = args.result_path
        self.random_query = args.random_query
        self.output_path = args.output_path

        self.ground_truths = list()
        self.result_folder = list()
        self.result_folder_full_path = list()

    def get_ground_truth_files(self):
        self.ground_truths = os.listdir(self.ground_truth_path)

    def get_result_folders(self):
        # return all the result folders (equinix-chicago...) in their full path
        self.result_folder_full_path = list()
        self.result_folder = os.listdir(self.result_path)
        for folder in self.result_folder:
            self.result_folder_full_path.append(self.result_path + folder)

    def get_look_back_boundary(self, dataset):
        # get corresponding window file
        window_file = self.dataset_path + '/' + dataset + '.windows'

        # get min, max of the file
        command = 'head -n 1 ' + window_file
        minimum = os.popen(command).read().strip().split(" ")[0]
        minimum = int(minimum)

        command = 'tail -n 1 ' + window_file
        maximum = os.popen(command).read().strip().split(" ")[1]
        maximum = int(maximum)
        return minimum, maximum

    def look_back(self, look_back_files_full_path):
        groundtruth = dict()
        for look_back_file in look_back_files_full_path:
            with open(look_back_file) as f:
                data = f.readline()
                while data:
                    data = data.split(' ')
                    ip = data[0]
                    count = int(data[1])
                    if ip not in groundtruth:
                        groundtruth[ip] = count
                    else:
                        groundtruth[ip] = groundtruth[ip] + count
                    data = f.readline()
        return groundtruth, sorted(groundtruth, key=groundtruth.__getitem__, reverse=True)

    def remove_duplicates(self, temp_result, algorithm):
        temp_result_dict_count = dict()
        temp_result_dict_window_id = dict()
        for temp in temp_result:
            five_tuple, count, window_id = temp

            if five_tuple not in temp_result_dict_count:  # insert
                temp_result_dict_count[five_tuple] = count
                temp_result_dict_window_id[five_tuple] = window_id
            else:  # already has an entry?
                if algorithm == 'HashPipe':
                    temp_result_dict_count[five_tuple] += count
                    temp_result_dict_window_id[five_tuple] = window_id  # this does not really matter in hashpipe

                elif algorithm == 'HashSlide':
                    table_window = temp_result_dict_window_id[five_tuple]  # already in the table
                    if table_window == window_id:  # same window id
                        temp_result_dict_count[five_tuple] += count
                    else:  # diff window id
                        if window_id > table_window:  # if new one is bigger than the one in the table
                            window_diff = abs(window_id - table_window)
                            if window_diff > self.WINDOW_OFFSET:  # too old, keep the new incoming one
                                temp_result_dict_count[five_tuple] = count  # replace the old count
                                temp_result_dict_window_id[five_tuple] = window_id  # keep the new window id
                            else:  # still fresh
                                temp_result_dict_count[five_tuple] += count  # both still fresh, add je lah
                                temp_result_dict_window_id[five_tuple] = window_id  # new one is fresher
                        else:  # table_window > window_id
                            window_diff = abs(window_id - table_window)
                            if window_diff > self.WINDOW_OFFSET:  # incoming too old, keep the new one in the table
                                # do nothing
                                pass
                            else:  # still fresh?
                                temp_result_dict_count[five_tuple] += count  # the one in the table fresher!!

                elif algorithm == 'HashPage':
                    table_window = temp_result_dict_window_id[five_tuple]
                    if table_window == window_id:
                        temp_result_dict_count[five_tuple] += count
                    else:
                        window_diff = abs(window_id - table_window)
                        if window_id > table_window:
                            temp_result_dict_count[five_tuple] = temp_result_dict_count[five_tuple] >> window_diff
                            temp_result_dict_count[five_tuple] += count
                            temp_result_dict_window_id[five_tuple] = window_id
                        else:
                            count = count >> window_diff
                            temp_result_dict_count[five_tuple] += count

        sorted_table = sorted(temp_result_dict_count, key=temp_result_dict_count.__getitem__, reverse=True)
        temp_result = list()
        for k in sorted_table:
            temp_result.append((k, temp_result_dict_count[k], temp_result_dict_window_id[k]))

        return temp_result

    def get_top_k(self, groundtruth, sorted_groundtruth, result_file):
        # extract the maximum first the do the rest later as they are always a subset of the maximum
        maximum = max(self.top_k)
        top_k_sorted = sorted_groundtruth[:maximum]

        temp_result = list()
        with open(result_file) as f:  # result_file is already sorted
            data = f.readline()
            while data:
                data = data.split(" ")

                five_tuple = str(data[0])
                count = int(data[1])
                window_id = int(data[2])

                temp_result.append((five_tuple, count, window_id))
                data = f.readline()

        if 'HashSlide' or 'SpaceSavingSlide' or 'CMSSlide' in result_file:  # sort the temp_result according to the window_id
            if not self.duplicates:
                temp_result = self.remove_duplicates(temp_result, 'HashSlide')

            max_window = max([int(i[2]) for i in temp_result])
            fresh_result = [i for i in temp_result if int(i[2]) >= max_window - 1]
            old_result = [i for i in temp_result if int(i[2]) < max_window - 1]

            fresh_result = sorted(fresh_result, key=lambda tup: tup[1], reverse=True)
            old_result = sorted(old_result, key=lambda tup: (tup[2], tup[1]), reverse=True)

            sorted_temp_result = list()
            sorted_temp_result.extend(fresh_result)
            sorted_temp_result.extend(old_result)
            sorted_temp_result = sorted_temp_result[:maximum]
        elif 'HashPage' or 'SpaceSavingPAge' or 'CMSPAge' in result_file:  # normalize the results according to window_id
            if not self.duplicates:
                temp_result = self.remove_duplicates(temp_result, 'HashPage')

            max_window = max([int(i[2]) for i in temp_result])
            normalized_result = list()
            for temp in temp_result:
                five_tuple, count, window = temp
                count = count >> (max_window - window)
                normalized_result.append((five_tuple, count, window))
            sorted_temp_result = sorted(normalized_result, key=lambda tup: tup[1], reverse=True)
            sorted_temp_result = sorted_temp_result[:maximum]
        else:
            if not self.duplicates:
                temp_result = self.remove_duplicates(temp_result, 'HashPipe')

            sorted_temp_result = temp_result[:maximum]

        # we have the results ready, and the ground truths ready, now time to evaluate the top-ks!
        result_output = list()
        for k in self.top_k:
            count = 0
            temp_groundtruth = top_k_sorted[:k]  # top-k from the ground truth
            temp_result = sorted_temp_result[:k]  # top-k from the results

            for temp in temp_result:
                if temp[0] in temp_groundtruth:
                    count = count + 1
            result = ((count * 1.0) / (k * 1.0)) * 100
            result_output.append((result_file, k, result))
        return result_output

    def get_ground_truth(self, look_back_minimum, query_files, look_back_period):
        result_output = list()
        for i, query_file in enumerate(query_files):
            result_file_name = os.path.basename(query_file)
            result_file_name = result_file_name.split('.')  # remove .result extension
            result_file_name = result_file_name[0]
            result_file_name = int(result_file_name)

            look_back_files = list()

            # get ground truth files to be evaluated against
            for j in range(result_file_name - look_back_period, result_file_name):
                j = str(j)
                if j in self.ground_truths:
                    look_back_files.append(j)
            look_back_files = [str(j) for j in look_back_files if int(j) >= look_back_minimum]
            look_back_files_full_path = [self.ground_truth_path + '/' + j for j in look_back_files]

            # sum up ground truth for the past N seconds according to the look back period
            groundtruth, sorted_groundtruth = self.look_back(look_back_files_full_path)

            # compute results for each top-ks, [20, 50, 150...]
            result_output.extend(self.get_top_k(groundtruth, sorted_groundtruth, query_file))
        return result_output

    def write_output_to_csv(self, output_path, output_file_basename, lookback_period, results_output):
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if not self.random_query:
            output_path += output_file_basename + '.' + str(lookback_period) + '.csv'
        else:
            output_path += output_file_basename + '.' + str(lookback_period) + '.random.csv'

        with open(output_path, 'w') as f:
            f.write('dataset,top_k,accuracy\n')
            for result in results_output:
                f.write(str(result[0]) + "," + str(result[1]) + ',' + str(result[2]) + "\n")

    def evaluate_ground_truth(self):
        output_file_basename = os.path.basename(os.path.dirname(self.result_path))
        self.get_ground_truth_files()  # load ground truth files
        self.get_result_folders()  # get all dataset folders that contains the results i.e. ../results/HashPipe.6.4500/equinix-chicago.dirA.20160317-130000.UTC.anon.pcap.dataset/

        for look_back_period in self.look_back_periods:  # for each look back period 20, 50, 150...
            results = list()
            for folder in self.result_folder:  # for each dataset folder, evaluate the ground truth
                print('Current dataset ==> ' + ' ' + folder)

                # for each dataset folder, get the beginning and ending time as the look back minimum and maximum
                look_back_minimum, look_back_maximum = self.get_look_back_boundary(folder)

                result_files_full_path = list()
                result_files = os.listdir(
                    self.result_path + '/' + folder)  # list all the .result files in the dataset folder
                for result_file in result_files:
                    result_files_full_path.append(self.result_path + '/' + folder + '/' + result_file)

                # generate the query points
                if not self.random_query:  # fixed query
                    query_points = sorted(
                        [i for i in range(look_back_maximum, look_back_minimum, -1 * self.interval_size)])
                    query_files = [i for j in query_points for i in result_files_full_path if str(j) in i]
                else:  # random query
                    query_points = sorted([random.randrange(look_back_minimum + 1, look_back_maximum) for i in
                                           range(self.query_per_iteration * self.random_iterations)])
                    query_files = [i for j in query_points for i in result_files_full_path if str(j) in i]

                # for each query points, perform look back on ground truth and return results
                results.extend(self.get_ground_truth(look_back_minimum, query_files, look_back_period))

            # output results to csv
            self.write_output_to_csv(self.output_path, output_file_basename, look_back_period, results)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--dataset-path', required=True,
        help='dataset path for the windows'
    )

    parser.add_argument(
        '--result-path', required=True,
        help='the directory of the algorithm to be evaluated against the ground truth i.e. ../results/HashPipe.6.4500/'
    )

    parser.add_argument(
        '--output-path', required=True,
        help='the directory to write the results'
    )

    parser.add_argument(
        '--random-query', default=False, action='store_true',
        help='defines the type of experiment'
    )

    parser.add_argument(
        '--top-k', type=int, nargs='+', default=[20, 60, 150, 300, 500, 1000],
        help='top-k results to be computed'
    )

    parser.add_argument(
        '--look-back-periods', type=int, nargs='+', default=[2, 5, 10, 15, 20, 25, 30],
        help='look back periods that are to be checked against the ground truth'
    )

    parser.add_argument(
        '--interval-size', type=int, default=10,
        help='length of an interval (equivalent to the reset interval of HashPipe)'
    )

    parser.add_argument(
        '--random-iterations', type=int, default=10,
        help='number of iterations for random-query'
    )

    parser.add_argument(
        '--num-queries', type=int, default=15,
        help='number of random queries per iteration'
    )

    parser.add_argument(
        '--duplicates', default=False, action='store_true',
        help='allow the data structure to have duplicates?'
    )

    parser.add_argument(
        '--window-offset', type=int, default=1,
        help='applicable for sliding window variants of the algorithms, for the tolerable age of a flow'
    )

    args = parser.parse_args()
    pprint(args)
    comparator = GroundTruthComparator(args)
    comparator.evaluate_ground_truth()


if __name__ == '__main__':
    main()
