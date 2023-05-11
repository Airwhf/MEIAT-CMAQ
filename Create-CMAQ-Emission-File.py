#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2023/3/15 16:34
# @Author    :Haofan Wang
# @Email     :wanghf58@mail2.sysu.edu.cn

from src import *

os.environ["IOAPI_ISPH"] = "6370000."


if __name__ == "__main__":
    start_time = time.time()
    main_createCMAQ()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")
