def border_up():
    x, y = 32, 96
    lst = []
    for i in range(48):
        # print([x, y], [x+1, y])
        lst.append([x, y])
        lst.append([x+1, y])
        x += 2
        y -= 2
    return lst

