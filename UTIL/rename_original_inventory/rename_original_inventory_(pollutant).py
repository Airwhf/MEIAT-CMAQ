#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2023/5/11 15:15
# @Author    :Haofan Wang
# @Email     :wanghf58@mail2.sysu.edu.cn

from src import *

if __name__ == "__main__":

    tbl_name = {"org": ["PMcoarse"],
                "new": ["PMC"]}

    input_dir = r"H:\MEIC\GeoTiff-2017"
    output_dir = r"H:\MEIC\GeoTiff-2017_rename"

    main_rename_original_pollutant(tbl_name, input_dir, output_dir)



