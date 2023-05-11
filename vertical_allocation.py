#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2022/11/22 16:03
# @Author    :Haofan Wang

from src import *

if __name__ == "__main__":
    files = glob.glob(r"output\*_power_*.nc")

    start_time = time.time()
    main_vertical_allocation(files)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")





