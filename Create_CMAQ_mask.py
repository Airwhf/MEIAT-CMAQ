#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2023/5/11 13:27
# @Author    :Haofan Wang
# @Email     :wanghf58@mail2.sysu.edu.cn


from src import *

os.environ['IOAPI_ISPH'] = '6370000.'

if __name__ == "__main__":
    # ------------------------------------------------------------
    # Shapefile path.
    shapefile_path = "shapefile/Anyang-around"
    # The field of each area.
    field = "NAME"
    # The output path.
    output_name = "output/mask.nc"
    # ------------------------------------------------------------

    start_time = time.time()
    main_create_CMAQ_mask(shapefile_path, field, output_name)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")


