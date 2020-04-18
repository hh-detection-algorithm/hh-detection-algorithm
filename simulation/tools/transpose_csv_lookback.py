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
            # print(algorithms)
            counter = counter + 1
        else:
            input = input.split(",")
            k = int(input[0])
            accuracies = input[1:]
            top_k.setdefault(k, list())
            top_k[k] = accuracies
        input = f.readline()
algorithms = [i.strip() for i in algorithms]
# print(top_k)
# print(algorithms)

headers = set()  # (HashPipe.6.4890, 100)
look_back = set() # 10

# prepare for transpose
current_index = 0
for algorithm in algorithms:
    temp = algorithm.split(".")
    look_back.add(int(temp[3]))  # 10
    algorithm = '.'.join(temp[:3]).strip()  # HashPipe.6.4890
    for key in top_k:
        headers.add((algorithm, key))

headers = sorted(headers)
look_back = sorted(look_back)

# print(headers)
# print(look_back)

# transposed
transposed = dict()
for header in headers:
    algorithm = header[0]
    k = header[1]

    if algorithm not in transposed:
        transposed[algorithm] = dict()

    for lookback in look_back:
        if lookback not in transposed[algorithm]:
            transposed[algorithm][lookback] = dict()
        column_name = '.'.join([algorithm, str(lookback)])
        if random:
            column_name += '.random'
        index = algorithms.index(column_name)
        for key, value in top_k.items():
            transposed[algorithm][lookback][key] = value[index]
# print(transposed['HashSlide.6.9750'][20])

# output with lookback as x axis
output = list()
# generate first row
new_header = list()
new_header.append('lookback')
# print(headers)
temp = ['.'.join([algorithm[0], str(algorithm[1])]) for algorithm in headers]
# temp = ['.'.join([algorithm[0], str(k)]) for algorithm in headers for k in top_k.keys()]
# print(temp)
new_header.extend(temp)
new_header = ','.join(new_header)
output.append(new_header)
# print(new_header)


# lookback
for lookback in look_back:
    temp = list()
    temp.append(str(lookback))
    for algorithm in headers:
        temp.append(str(transposed[algorithm[0]][lookback][int(algorithm[1])].strip()))
    output.append(','.join(temp))

# for out in output:
#     print('line')
#     print(out)

csv_filename = filename.replace('.csv', '.transposed.csv')
# print(csv_filename)
with open(csv_filename, 'w') as f:
    for out in output:
        f.write(out + '\n')






