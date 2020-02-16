from threading import Thread
from client.cache_client import Cache


def count(n, name):
    cache = Cache(name="example")

    response = cache.get("acc")
    while (n > 0):
        if response.get("error") is not None:
            response = cache.get("acc")
        if response.get("error") is None:
            #print("{name}.get: {item}".format(name=name, item=response))
            response = cache.set("acc", int(response["value"]) + 1, response["cas"])
            if response.get("error") is None:
                n -= 1
                print("{name}.set: {item}".format(name=name, item=response))
            else:
                print("{name}.set: failed!".format(name=name))
    print("{name}: Exiting".format(name=name))

def concurrent_count():
    print("Counting to 250 with 3 threads")
    print("Connecting and setting accumulator to 0")
    cache = Cache(name="example")
    cache.set("acc", 0)
    t1 = Thread(target=count, args=(100,"t1"))
    t2 = Thread(target=count, args=(50,"t2"))
    t3 = Thread(target=count, args=(100,"t3"))
    
    [t.start() for t in (t1,t2,t3)]
    [t.join() for t in (t1,t2,t3)]

    print("All threads finished!")
    acc = cache.get("acc")
    print("Final accumulator value:{value}".format(value=acc.get("value")))

if __name__ == "__main__":
    concurrent_count()