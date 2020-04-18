import os
import sys
import csv

data = dict()
top_k = dict()

filename = sys.argv[1]
with open(filename) as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        dataset = row["dataset"]
        # print(dataset)
        k = int(row["top_k"])
        accuracy = row["accuracy"]

        dataset_name = os.path.basename(dataset)
        dataset_name = int(dataset_name.split(".")[0])

        if k not in top_k:
            top_k[k] = dict()
        top_k[k][dataset_name] = float(accuracy)


results = dict()
for k in top_k:
    results[k] = dict()
    for i in range(180):
        results[k][i] = list()

final = dict()
for k in top_k:
    final[k] = dict()
    for i in range(180):
        final[k][i] = list()

for key in top_k:
    temp = top_k[key]
    temp = sorted(temp)
    # print(temp)
    start = min(temp)
    end = max(temp)
    while start < end:
        for i in range(180):
            if start + i in temp:
                results[key][i].append(start + i)
        start += 180

for k1 in top_k:
    for k2 in results[k1]:
        for k3 in results[k1][k2]:
            final[k1][k2].append(top_k[k1][k3])

for k1 in top_k:
    for k2 in results[k1]:
        final[k1][k2] = sum(final[k1][k2])/len(final[k1][k2])

# generate csv
# header
output = list()

header = list()
header.append('time')

for key in final.keys():
    header.append(str(key))
header = ','.join(header)
output.append(header)

# print(header)
# for each row
for i in range(180):
    temp = list()
    temp.append(str(i+1))
    for k in top_k.keys():
        temp.append(str(final[k][i]))
    temp = ','.join(temp)
    output.append(temp)

filename = filename.replace('.csv', '.sine.csv')
with open(filename, 'w') as f:
    for out in output:
        f.write(out + '\n')