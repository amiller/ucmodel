# A system of interacting processes
from gevent.event import Event
import gevent

env = {}
accepted = [("a","b")]

class Process(object):
    def __init__(self, name, env):
        self.name = name
        self.env = env
        self.queue = []
        self.signal = Event()

    def suspend(self):
        self.signal.clear()
        self.signal.wait()

    def read(self):
        return self.queue.pop(0)

    def write(self, receiver, m):
        self.env[receiver].queue.append((self.name, m))
        self.env[receiver].signal.set()
        self.signal.clear()
        self.signal.wait()

def p1(read,write,output):
    write("p2","1")
    write("p2","2")

def p2(read,write,output):
    s,x = read()
    s,y = read()
    print "p2 received:", x, y, "from", s
    output(x)

def make_processes(names, procs):
    env = {}
    threads = []
    for n,f in zip(names,procs):
        p = Process(n, env)
        env[n] = p
        def output(x): print "[%s] output: %s" % (n,x)
        threads.append(gevent.spawn(f, p.read, p.write, output))

    while not threads[0].dead:
        gevent.wait()
        env[names[0]].queue.append("continue")
        env[names[0]].signal.set()

make_processes(["p1","p2"], [p1,p2])
