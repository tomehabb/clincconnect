l1 = [9,9,9,9,9,9,9] 
l2 = [9,9,7,8]
output = []




def addNum(l1: list, l2: list):
    # Check indices
    if len(l1) != len(l2):
        for index1, value1 in enumerate(l1):
            print(value1)

addNum(l1, l2=l2)