for i in range(10, 100):
    sec = pow(i, 2)
    if len(str(sec)) == 3:
        last = sec % 100
        if last * last == sec:
            print(last)