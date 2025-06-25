from datetime import datetime  , timezone


def test():
    check_in_time =  datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')  # Use UTC time
    print("watsr",check_in_time)

if __name__ == '__main__':
    test()