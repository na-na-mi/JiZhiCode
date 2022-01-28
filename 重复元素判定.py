def ifRepeat(*list):
    set1=set(list)
    if len(set1)!=len(list):
        return False
    return True
print(ifRepeat(1,2,3,5,4,6,7,8))
