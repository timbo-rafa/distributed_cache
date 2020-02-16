from threading import Thread
from geo_cache_client.cache_client import Cache

def count(n, name):
    cache = Cache(name="example")

    response = cache.get("acc")
    while (n > 0):
        if not response.ok:
            response = cache.get("acc")
        if response.ok:
            #print("{name}.get: {item}".format(name=name, item=response))
            item = response.json()
            response = cache.set("acc", int(item["value"]) + 1, item["cas"])
            if response.ok:
                n -= 1
                print("{name}.set: {item}".format(name=name, item=response.json()))
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
    acc = cache.get("acc").json()
    print("Final accumulator value: {value}".format(value=acc.get("value")))

def main():
    concurrent_count()

if __name__ == "__main__":
    main()