import math
import numpy
import sys

def linear_rescale(min, max, value):
    """
    Linearly rescale a value to 0 and 1 using the min and max values.
    :param min:
    :param max:
    :param value:
    :rtype: float
    """
    x = (value - min)/(max - min)
    return x

def wrapto360(angle):
    """
    Wrap a value on -180, 180 to 360.

    :param degrees: float
    :return: float
    """
    if angle >= 0:
        return angle
    else:
        return 360 + angle

def geometric_mean(data):
    """
    Get the geometric mean of the data.
    Useful for numbers that go from 0 -> and are a type of enrichment of the data.

    :param data: numpy.Array
    :return: float
    """
    logs = numpy.log(data)
    return math.exp(logs.mean())

def approx_geom_mean(xs, ys, offset_zero=False):
    """
    Returns geometric mean as a ratio.
    """

    logs = []
    for x, y, in zip(xs, ys):
        # Add 1 to all numbers to account for 0s.
        if offset_zero:
            if x == 0:
                x = x + 1
            if y == 0:
                y = y + 1
        else:
            if x == 0 or y == 0:
                continue

        # print(x)
        # print(y)
        logs.append(math.log(x / float(y)))

    #print([math.exp(b) for b in logs])
    a = np.array(logs)
    #print(math.exp(np.mean(a)))
    return math.exp(np.mean(a))

def distance_numpy(array1: numpy.array, array2: numpy.array) -> float:
    """
    Get the distance between two points
    """

    return numpy.linalg.norm(array1-array2)

def distance(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    """
    Get the distance between variables.
    """

    return math.sqrt( math.pow( (x1-x2), 2) ) + math.sqrt( math.pow( (y1-y2), 2) )  + math.sqrt( math.pow( (z1-z2), 2) )

def get_perc(freq, total):
    """
    Get percent
    """
    freq = int(freq)
    total = float(total)

    if freq==0 and total==0:
        return 1000
    if total==0:
        sys.exit("cannot calculate percent as total is 0!")
    return freq/total *100


def get_s_perc(freq, total):
    """
    Get string of percent
    """
    return get_n_s(get_perc(freq, total))

def get_n_s(num):
    """
    Get a string for a float at .2f
    """
    if num == None:
        return 'None'
    return "%.2f"%num