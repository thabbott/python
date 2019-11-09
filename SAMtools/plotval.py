import numpy as np
import matplotlib.pyplot as plt
import sys

if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print('Usage: plotval.py <file> <variable>')
        exit()

    time = []
    val = []
    with open(sys.argv[1], 'r') as f:
        line = '--'
        while line != '':
            if line.strip().startswith('DAY = '):
                time.append(float(line.split()[2]))
            if line.strip().startswith(sys.argv[2]):
                val.append(float(line.split()[-1]))
            line = f.readline()

    time = np.array(time)
    val = np.array(val)
    plt.figure()
    plt.plot(time, val, 'k')
    plt.xlabel('time')
    plt.ylabel(sys.argv[2])
    plt.title('mean = %.2f' % np.mean(val))
    plt.show()
