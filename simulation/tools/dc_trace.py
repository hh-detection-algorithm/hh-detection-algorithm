import sys

FILENAME = sys.argv[1]
FILE_LENGTH = 180 # 3 minutes

with open(FILENAME) as f:
    entries = f.readlines()

HEAD = int(float(entries[0].split()[0])) + 1
# print(HEAD)
FILE_SEQ = 1

FILE_OUTPUT = dict()

for entry in entries:
    current_time = int(float(entry.split()[0]))
    if current_time >= HEAD:
        if HEAD <= current_time < (HEAD + FILE_LENGTH):
            if FILE_SEQ not in FILE_OUTPUT:
                FILE_OUTPUT[FILE_SEQ] = list()
            else:
                FILE_OUTPUT[FILE_SEQ].append(entry.strip())
        else:
            # print(HEAD, HEAD+FILE_LENGTH)
            FILE_SEQ = FILE_SEQ + 1
            HEAD = HEAD + FILE_LENGTH
            # print(entry.strip())
            if FILE_SEQ not in FILE_OUTPUT:
                FILE_OUTPUT[FILE_SEQ] = list()
            else:
                FILE_OUTPUT[FILE_SEQ].append(entry)
    else:
        pass

for file in FILE_OUTPUT.keys():
    filename = "{:02d}".format(file) + '.dataset'
    with open(filename, 'wb') as f:
        for entry in FILE_OUTPUT[file]:
            f.write(entry + '\n')
