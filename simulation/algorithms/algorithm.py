import os
import math
import mmh3


class Algorithm:
    def __init__(self, args):
        self.NUM_COUNTERS = args.num_counters
        self.NUM_STAGES = args.num_stages
        self.WINDOW_OFFSET = args.window_offset
        self.STAGE_SIZE = int(self.NUM_COUNTERS / self.NUM_STAGES)

        self.DATASET_PATH = args.dataset_path

        self.ALGORITHM = args.algorithm
        self.SLIDING_WINDOW = args.sliding_window
        self.AGING_FACTOR = args.aging_factor

        self.INTERVAL_SIZE = args.interval_size  # defines the interval size of HashPipe
        self.WINDOW_SIZE = args.window_size
        self.WINDOW_NUM = self.INTERVAL_SIZE / self.WINDOW_SIZE  # number of windows within an interval

        self.table = None
        self.heavy_hitters = dict()

        self.current_dataset = None
        self.current_timestamp = None

        self.relative_timestamp = 0
        self.window_id_max = 0
        self.current_window_id = 1
        self.windows = dict()  # tuple (X, Y) where X and Y are a period of time, as key, and window_id as val

        self.output_path = None

        self.init_table()

    def get_index(self, ip, stage):
        data = ip + str(stage)
        return mmh3.hash(data.encode(encoding='UTF-8')) % self.STAGE_SIZE

    def preprocess_input(self, data):
        if not data:
            return

        data = data.strip()
        data = data.split()

        timestamp = data[0].strip()
        data = data[1:]
        data = ','.join(data)
        return timestamp, data

    def init_table(self):
        pass

    def flush_table(self):
        pass

    def reset_variables(self):
        self.relative_timestamp = 0
        self.window_id_max = 0
        self.current_window_id = 1

    def compute_windows(self):
        dataset_directory = self.DATASET_PATH
        window_interval = self.WINDOW_SIZE

        # Get all file in sorted order
        command = "for i in `ls -d " + dataset_directory + "* | grep dataset | grep -v windows | grep -v groundtruth | grep -v results | grep -v junk | sort --version-sort`; do realpath $i; done"
        command = os.popen(command).read().strip()
        files = command.split("\n")

        # Get starting/ ending time for each file
        timestamps = list()
        intervals = list()
        for i in files:
            head = os.popen("head -n 1 " + i).read().strip().split()[0]
            head = int(math.floor(float(head)))
            tail = os.popen("tail -n 1 " + i).read().strip().split()[0]
            tail = int(math.ceil(float(tail)))

            timestamps.append(head)
            timestamps.append(tail)
            intervals.append((head, tail))

        assert (timestamps == sorted(timestamps))

        minimum = min(timestamps)
        maximum = max(timestamps)

        # Generate the intervals
        gen_intervals = []
        previous = minimum
        current = minimum
        while current < maximum:
            previous = current
            current = current + window_interval
            gen_intervals.append((previous, current))

        final = []
        for i, interval in enumerate(intervals):
            start = interval[0]
            end = interval[1]
            final.append(list())
            for gen_interval in gen_intervals:
                if start <= gen_interval[0] < end:
                    (final[i]).append(gen_interval)

        assert (len(intervals) == len(final) == len(command.split("\n")))

        for i, ff in enumerate(files):
            ff += '.windows'
            with open(ff, 'w') as f:
                for j in final[i]:
                    f.write(str(j[0]) + " " + str(j[1]) + "\n")
        print('Window files generated successfully, window size = ' + str(window_interval))

    def get_current_window_id(self, timestamp):
        timestamp = float(timestamp)
        timestamp = int(timestamp)

        # write results for every second
        if not self.current_timestamp == timestamp:
            self.current_timestamp = timestamp
            self.write_results_to_file(timestamp)

        for period, window_id in self.windows.items():
            start = int(period[0])
            end = int(period[1])
            if start <= timestamp < end:
                if window_id != self.current_window_id:
                    self.relative_timestamp = self.relative_timestamp + 1
                    self.current_window_id = window_id
                    if self.relative_timestamp == self.WINDOW_NUM:  # reached HashPipe's reset interval
                        self.flush_table()
                        self.relative_timestamp = 0
                return window_id
        return -1

    def load_windows_from_file(self, dataset_path):
        windows = dataset_path + '.windows'
        minimum = 2 << 31
        maximum = 0
        with open(windows) as f:
            window = f.readline().strip()
            while window:
                start_end = window.split(" ")
                start = start_end[0]
                start = int(start)
                end = start_end[1]
                end = int(end)
                minimum = start if start < minimum else minimum
                maximum = end if end > maximum else maximum
                if not (start, end) in self.windows:
                    self.window_id_max = self.window_id_max + 1
                    self.windows[(start, end)] = self.window_id_max
                window = f.readline().strip()
        return minimum, maximum

    def replay_dataset(self):
        command = 'for i in `ls -d ' + self.DATASET_PATH + "/* | grep .dataset | grep -v windows | grep -v groundtruth | grep -v results | grep -v junk | sort --version-sort`; do realpath $i; done"
        datasets = os.popen(command).read().strip().split("\n")

        # Compute windows
        self.compute_windows()

        for dataset in datasets:
            print(dataset, 'loaded!')

            # init all values for each dataset loaded
            self.reset_variables()
            self.windows.clear()
            self.init_table()

            self.current_dataset = dataset
            minimum, maximum = self.load_windows_from_file(dataset)
            self.current_timestamp = int(minimum)  # init timestamp value

            with open(dataset) as f:
                for data in f:
                    data = data.strip()
                    data = self.preprocess_input(data)
                    self.simulate_algorithm(data)
                self.write_results_to_file(maximum)  # write results for the last second

    def simulate_algorithm(self, data):
        pass

    def write_results_to_file(self, timestamp=None):
        current_dataset_name = os.path.basename(self.current_dataset)
        # store results according to their INTERVAL SIZES
        output_path = self.DATASET_PATH + '/results/' + str(self.INTERVAL_SIZE) + '/' + self.__class__.__name__ + '.' + str(
            self.NUM_STAGES) + '.' + str(self.NUM_COUNTERS) + '/' + current_dataset_name + '/'

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        output_path = output_path + str(timestamp)
        sorted_table = self.generate_output()
        with open(output_path, 'w') as f:
            for k in sorted_table:
                f.write(str(k[0]) + " " + str(k[1]) + " " + str(k[2]) + "\n")

    def generate_output(self):
        pass
