

class Test:
    def __init__(self, i):
        self.i = i
        print("initted " + str(self.i))

    def __del__(self):
        print("killed " + str(self.i))





x = Test(1)


def test():
    x = Test(2)


test()
