import random
import time
import string

odd = [1.08, 1.24, 2.98, 7, 1.11, 1.45, 1.65, 1.001, 1.78, 1.98, 2.2, 4, 3.5]



data = random.choice(odd)
status = True

while status:
    time.sleep(4)
    print(random.choice(odd))


