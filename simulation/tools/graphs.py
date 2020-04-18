import os
import csv
import sys
import random

class Graphs():
    def __init__(self):
        self.dataset_length = 180

    def extract_by_top_k(self, processed_result):
        self.current_file = processed_result
        top_k = dict()
        with open(processed_result) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                subdataset = row["subdataset"]
                snapshot = int(row["snapshot"])
                k = int(row["top_k"])
                recall = row["recall"]

                if k not in top_k:
                    top_k[k] = []
                top_k[k].append((subdataset, snapshot, recall))
        return top_k

    def extract_by_subdataset(self, top_k):
        top_k_subdataset = dict()

        for k, entries in top_k.items():
            subdatasets = dict()
            for entry in entries:
                subdataset, snapshot, recall = entry
                if subdataset not in subdatasets:
                    subdatasets[subdataset] = []
                subdatasets[subdataset].append((snapshot, recall))
            top_k_subdataset[k] = subdatasets
        return top_k_subdataset

    def saw_graph_average(self, subdatasets):
        recalls = [[] for i in range(self.dataset_length)]

        for subdataset, entries in subdatasets.items():
            entries = sorted(entries, key=lambda tup: tup[0])
            start = entries[0][0]

            for entry in entries:
                index = entry[0] - start
                recalls[index].append(float(entry[1]))

        recalls = [sum(i)/len(i) for i in recalls]
        return recalls

    def generate_saw_graph_output(self, results):
        headers = []
        output = []

        headers.append('time')
        headers.extend([str(k) for k in results.keys()])
        # print(','.join(headers))
        for i in range(self.dataset_length):
            entries = [str(i+1)]
            entries.extend(str(v[i]) for k,v in results.items())
            # print(','.join(entries))
            output.append(entries)
        return headers, output

    def output_to_csv(self, filename, headers, entries):
        with open(filename, 'w') as f:
            f.write(','.join(headers))
            f.write('\n')
            for entry in entries:
                f.write(','.join(entry))
                f.write('\n')

    def saw_graph(self, top_k_subdataset):
        results = dict()
        for top_k, subdatasets in top_k_subdataset.items():
            results[top_k] = self.saw_graph_average(subdatasets)
        headers, entries = self.generate_saw_graph_output(results)
        filename = self.current_file.replace('.csv', '.SAW.csv')
        self.output_to_csv(filename, headers, entries)
        return filename

    def random_queries(self, top_k_subdataset):
        results = dict()
        iterations = 3
        for i in range(iterations):
            for top_k, subdatasets in top_k_subdataset.items():
                results[top_k] = []
                temp_results = dict()

                for subdataset in subdatasets:
                    temp_results[subdataset] = []
                    for i in range(0, len(subdatasets[subdataset]), 10):
                        # print(i)
                        index = random.randrange(i, i+9)
                        # print('index', index)
                        # print(subdatasets[subdataset][index][1])
                        acc = float(subdatasets[subdataset][index][1])
                        temp_results[subdataset].append(acc)
                for subdataset in subdatasets:
                    temp_results[subdataset] = sum(temp_results[subdataset])/len(temp_results[subdataset])
                temp_results = [temp_results[subdataset] for subdataset in subdatasets]
                temp_results = sum(temp_results)/len(temp_results)
                # print(top_k, temp_results)
                results[top_k] = temp_results
        # print(results)
        return results


filename = sys.argv[1]
if len(sys.argv) > 2:
    memory = sys.argv[2]
else:
    memory = None

graphs = Graphs()
top_k = graphs.extract_by_top_k(filename)
top_k_subdataset = graphs.extract_by_subdataset(top_k)

if not memory:
    filename = graphs.saw_graph(top_k_subdataset)
    print('Wrote file', filename)
else:
    # print(top_k_subdataset)
    print(os.path.basename(filename))
    memory_results = graphs.random_queries(top_k_subdataset)
    # print('memory,' + filename.split('.')[2])
    print(memory_results)


