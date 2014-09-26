import threading, time, random

def get_html():
    t = random.randint(2, 4)
    print('fetch',t)
    time.sleep(t)
    print('after sleep', t)
    return t

def save(a):
    print('save', a)
    time.sleep(1)
    return a

MAX_TREAD = 4
dblock = threading.Lock()
class FetchTread(threading.Thread):
    """docstring for FetchTread"""
    def run(self):
        c = get_html()
        with dblock:
            a = save(c)
            print('end', a)


while threading.active_count() < MAX_TREAD*2:
    print('active_count', threading.active_count())
    t = FetchTread()
    t.start()
    t.join(1)
