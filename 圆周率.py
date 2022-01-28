import math


def zu(n):
    def f(x):
        h = 1 - math.sqrt(1 - (x / 2) ** 2)
        return math.sqrt(h ** 2 + (a / 2) ** 2)

    a = 1
    k = 6
    for i in range(n):
        a = f(a)
        k *= 2
    return a * k / 2


if __name__ == '__main__':
    print(zu(10))
    print(math.pi)
