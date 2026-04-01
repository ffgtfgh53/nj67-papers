def task3_1(list_of_values):
    def merge(left,right):
        merged = []
        while len(left) > 0 and len(right) > 0:
            if left[0] < right[0]:
                merged.append(left[0])
                del left[0]
            else:
                merged.append(right[0])
                del right[0]
        merged.extend(left)
        merged.extend(right)
        return merged
    if len(list_of_values) == 1:
        return list_of_values
    mid = len(list_of_values)//2
    left = task3_1(list_of_values[:mid])
    right = task3_1(list_of_values[mid:])
    return merge(left,right)

# def task3_1(values: list[int]):
#     l = len(values)
#     if l <= 1:
#         return values
#     def merge_helper(a, b):
#         res = []
#         while a and b:
#             if a[0] < b[0]:
#                 res.append(a.pop(0))
#             else:
#                 res.append(b.pop(0))
#         res.extend(a + b)
#         return res
#     return merge_helper(task3_1(values[:l//2]), task3_1(values[l//2:]))

import csv
import random

def task3_2(filename_in,filename_out,no_of_sample):
    folder_path = "./Resources/TASK3/"
    with open(folder_path+filename_in) as file:
        data = list(csv.reader(file))
    random_sample = []
    random_sample_w = []
    for i in range(no_of_sample):
        random_idx = random.randint(0,len(data)-1)
        random_pt = data.pop(random_idx)
        random_sample.append(float(random_pt[0]))
        random_sample_w.append(random_pt)
    with open(folder_path+filename_out,"w",newline="") as file:
        writer = csv.writer(file)
        writer.writerows(random_sample_w)
    average = sum(random_sample)/no_of_sample
    counter = 0
    for i in data+random_sample_w:
        if float(i[0]) < average:
            counter += 1
    return counter

def task3_3():
    import csv
    import random

    alpha = 5000
    no_of_sample = 700


    def task3_3(filename_in,no_of_sample,alpha):
        check_lower = 0
        check_notlower = 0
        while not (check_lower and check_notlower):
            folder_path = "./Resources/"
            with open(folder_path+filename_in) as file:
                data = list(csv.reader(file))
            random_sample = []
            random_sample_w = []
            for i in range(no_of_sample):
                random_idx = random.randint(0,len(data)-1)
                # random_pt = data[random_idx]
                random_pt = data.pop(random_idx)
                random_sample.append(float(random_pt[0]))
                random_sample_w.append(random_pt)
            average = sum(random_sample)/no_of_sample
            # print(average)
            counter = 0
            for i in data+random_sample_w:
                if float(i[0]) < average:
                    counter += 1
            print(counter)
            if counter < alpha:
                # print("LOWER.TXT")
                filename_out = "LOWER.TXT"
                check_lower = 1
            elif counter > alpha:
                # print("NOTLOWER.TXT")
                filename_out = "NOTLOWER.TXT"
                check_notlower = 1
            else:
                continue
            with open(folder_path+filename_out,"w",newline="") as file:
                writer = csv.writer(file)
                writer.writerows(random_sample_w)
            # print(f"{check_lower} | {check_notlower}")
        
    task3_3("TASK3FILE.txt",no_of_sample,alpha)