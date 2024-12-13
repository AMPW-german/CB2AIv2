import numpy as np

enemiesDone = np.ndarray((100,), np.uint)

print(enemiesDone)

enemiesDone[:] = 0
enemiesDone[10] = 10

print(enemiesDone)

if 10 in enemiesDone:
    print("hello")
    print(enemiesDone[np.argmax(enemiesDone)])

    enemiesDone[np.argmax(enemiesDone)] = 0

    print(enemiesDone)