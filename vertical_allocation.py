#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2022/11/22 16:03
# @Author    :Haofan Wang

from src import *

if __name__ == "__main__":
    sectors = ['power', 'industry']
    
    start_time = time.time()
    for sector in sectors:
        files = glob.glob(fr"output\*_{sector}_*.nc") 
        main_vertical_allocation(files)
        
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")





