file = open("names.txt", "rt")
data = file.read()
print(data)
lst = data.split()
print(lst)
file.close()

