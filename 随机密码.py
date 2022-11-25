import random

list1 = [chr(i) for i in range(ord('a'), ord('z') + 1)] + [chr(i) for i in range(ord('A'), ord('Z') + 1)] + [i for i in
                                                                                                             range(1,
                                                                                                                   10)]
for i in range(10):
    for q in range(8):
        print(random.choice(list1), end="")
    print("\n")
