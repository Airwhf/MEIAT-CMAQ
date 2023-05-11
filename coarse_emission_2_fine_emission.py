from src import *

os.environ["IOAPI_ISPH"] = "6370000."


if __name__ == '__main__':
    start_time = time.time()
    main_coarse2fine()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")
