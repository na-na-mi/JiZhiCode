with open("file.txt", "r", encoding='UTF-8') as str:
    data = str.read()
    data.replace(" ", "")
print("".join(data.split()))
