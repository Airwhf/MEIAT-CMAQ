# @Time    : 2023/02/21 19:17
# @Author  : Haofan Wang
# @Version : python3.9
# @Email   : wanghf58@mail2.sysu.edu.cn
import os

from src import *

os.environ["IOAPI_ISPH"] = "6370000."
# Ignore the warning information from pandas.
pd.options.mode.chained_assignment = None


if __name__ == "__main__":
    start_time = time.time()
    main_f2c()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")
