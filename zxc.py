def fun(a):
    if a == 0 or a ==1:
        return 1
    return fun(a-1) + fun(a-2)

print(fun(35))