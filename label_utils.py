import os
import tempfile

label_list = os.listdir(r".\\images\\Dataset0\\labels")

label_dict = {}

for label_file in label_list:
    labels = open(r".\\images\\Dataset0\\labels\\" + label_file).readlines()
    for label in labels:
        label_num = int(label.split(" ")[0])
        if label_dict.get(label_num, -1) >= 1:
            label_dict[label_num] += 1
        else:
            label_dict.update({label_num: 1})

label_file_old = open(r"labels_old.txt")
label_file = open(r"labels.txt")

changeDict = {} # Keys: old index | Values: new index

lines_old = label_file_old.readlines()
lines = label_file.readlines()

for i in range(len(lines_old)):
    for j in range(len(lines)):
        if lines_old[i].strip() == lines[j].strip():
            changeDict.update({i: j})

print(changeDict)

for label_file_num in label_list:
    temp_list = []
    label_file = open(r".\\images\\Dataset0\\labels\\" + label_file_num)
    labels = label_file.readlines()
    for label in labels:
        label_num = int(label.split(" ")[0])
        new_num = changeDict.get(label_num, -1)
        if new_num != -1:
            temp_list.append(str(new_num) + " " + " ".join(str(x) for x in label.split(" ")[1:]))
    print("".join(str(x) for x in temp_list))

    label_file = open(r".\\images\\Dataset0\\labels\\" + label_file_num, "w")
    label_file.write("".join(str(x) for x in temp_list))
    label_file.close()