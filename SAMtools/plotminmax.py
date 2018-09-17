import numpy as np
import matplotlib.pyplot as plt
import sys

if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print('Usage: plotminmax.py <file> <variable>')
        exit()

    time = []
    vmin = []
    vmax = []
    with open(sys.argv[1], 'r') as f:
        line = '--'
        while line != '':
            if line.strip().startswith('DAY = '):
                time.append(float(line.split()[2]))
            if line.strip().startswith(sys.argv[2]):
                vmin.append(float(line.split()[1]))
                vmax.append(float(line.split()[2]))
            line = f.readline()

    time = np.array(time)
    vmin = np.array(vmin)
    vmax = np.array(vmax)
    plt.figure()
    plt.plot(time, vmax, 'b')
    plt.plot(time, vmin, 'r')
    plt.xlabel('time')
    plt.ylabel(sys.argv[2])
    plt.show()
