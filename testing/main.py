
blocks = input("Number of blocks: ")
blocks = int(blocks)

for i in range(blocks):
    space = " "
    print (space * (blocks-(i+1)), "#" * (i+1))
    i+1