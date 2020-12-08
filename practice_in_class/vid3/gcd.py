#by Adam Liu

#a = 42
#b = 30

def gcd(a, b): 
    #print("a=",a)

    #a, b MUST be positive integer
    if not (a > 0 and b > 0):
        raise ArithmeticError("%s, %s: Must be positive int." % (a, b))
    while a != b:
        if a > b:
            a = a - b
        else:
            b = b - a
    return a


#print(v)

#unit test

#version1
def test_gcd():
    ax = 42
    bx = 30
    v = gcd(ax, bx)

    assert(v == 6)

def test_gcd2():
    ax = 6
    bx = 6
    v = gcd(ax, bx)

    assert(v == 6)

#def test_gcd3():
#    ax = 42
#    bx = -30
#    v = gcd(ax, bx)
#
#    assert(v == 6)

def test_gcd3():
    ax = 42
    bx = -30
    try:
        v = gcd(ax, bx)
        # error if negative number doesn't fed in to function
        # to test exception handly
        # it shoud never  run line below in this test
        assert(False)
    except ArithmeticError as e:
        print(ArithmeticError)
        print(type(e))
        assert("Must be positive int." in str(e))
        print(str(e))
    except:
        # to test there's no more other error
        assert(False)
    finally:
        assert(True)

if __name__ == "__main__":
    test_gcd3()