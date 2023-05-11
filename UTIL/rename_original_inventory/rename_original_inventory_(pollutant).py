#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2023/5/11 15:15
# @Author    :Haofan Wang
# @Email     :wanghf58@mail2.sysu.edu.cn

from src import *

if __name__ == "__main__":

    tbl_name = {"org": ["nh3", "nox", "pm10", "pm25", "voc", "co", "sox"],
                "new": ["NH3", "NOx", "PM10", "PM25", "VOC", "CO", "SO2"]}

    input_dir = r"D:\Emission-Inventory\UK-inventory\reclassification_tiff"
    output_dir = r"D:\Emission-Inventory\UK-inventory\reclassification_tiff_rename"

    main_rename_original_pollutant(tbl_name, input_dir, output_dir)



