import os
import sys

filename = sys.argv[1]

# k,HashPage.6.3360.10,HashPage.6.3360.15,HashPage.6.3360.20
# 20,84.11111111,89.5,91.83333333
# 60,78.31481481,85.18518519,88

random = False

top_k = dict()
algorithms = list()
# loaded into memory
with open(filename) as f:
    counter = 0
    input = f.readline()
    while input:
        input = input.strip()
        if counter == 0:
            input = input.split(",")
            algorithms = input[1:]
            if 'random' in algorithms[0]:
                random=True
            counter = counter + 1
        else:
            input = input.split(",")
            k = int(input[0])
            accuracies = input[1:]
            top_k.setdefault(k, list())
            top_k[k] = accuracies
        input = f.readline()
algorithms = [i.strip() for i in algorithms]

headers = set()  # (HashPipe.6.4890, 100)
memory = set()

# prepare for transpose
for algorithm in algorithms:
    temp = algorithm.split(".")
    memory.add(int(temp[2]))  # 4890
    temp.pop(2)
    algorithm = '.'.join(temp[:3]).strip()  # HashPipe.6.10
    for key in top_k:
        headers.add((algorithm, key))

memory = sorted(memory)
headers = sorted(headers)
# print(headers)
# print(memory)

# sys.exit(1)

# transposed
transposed = dict()
for header in headers:
    algorithm = header[0]
    k = header[1]

    if algorithm not in transposed:
        transposed[algorithm] = dict()

    for mem in memory:
        if mem not in transposed[algorithm]:
            transposed[algorithm][mem] = dict()
        temp = algorithm
        temp = temp.split(".")
        temp.insert(2, str(mem))
        column_name = '.'.join(temp)
        # print(column_name)
        if random:
            column_name += '.random'
        index = algorithms.index(column_name)
        for key, value in top_k.items():
            transposed[algorithm][mem][key] = value[index]
# print(transposed['HashSlide.6.9750'][20])

# output with lookback as x axis
output = list()
# generate first row
new_header = list()
new_header.append('memory')
# print(headers)
temp = ['.'.join([algorithm[0], str(algorithm[1])]) for algorithm in headers]  # HashPipe.6.10(lookback).20(top-k)
# temp = ['.'.join([algorithm[0], str(k)]) for algorithm in headers for k in top_k.keys()]
# print(temp)
new_header.extend(temp)
new_header = ','.join(new_header)
output.append(new_header)
# print(new_header)


# lookback
for mem in memory:
    temp = list()
    temp.append(str(mem))
    for algorithm in headers:
        temp.append(str(transposed[algorithm[0]][mem][int(algorithm[1])].strip()))
    output.append(','.join(temp))

# for out in output:
#     print('line')
#     print(out)

csv_filename = filename.replace('.csv', '.transposed.memory.csv')
# print(csv_filename)
with open(csv_filename, 'w') as f:
    for out in output:
        f.write(out + '\n')






