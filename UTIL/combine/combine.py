#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2023/5/18 14:52
# @Author    :Haofan Wang
# @Email     :wanghf58@mail2.sysu.edu.cn

from src import *

if __name__ == "__main__":
    upper_raster_dir = r"D:\GitHub\MEIAT-CMAQ-data\MEIC-2017"
    bottom_raster_dir = r"D:\GitHub\MEIAT-CMAQ-data\MIX-2010"
    output_dir = r"D:\GitHub\MEIAT-CMAQ-data\MIX&MEIC"

    upper_raster_pollutants = ["NH3", "NOx", "PMcoarse", "PM25", "SO2", "CO",
                               "CB05_ALD2", "CB05_ALDX", "CB05_CH4", "CB05_ETH", "CB05_ETHA", "CB05_ETOH", "CB05_FORM",
                               "CB05_IOLE", "CB05_ISOP", "CB05_MEOH", "CB05_NVOL", "CB05_OLE", "CB05_PAR", "CB05_TERP",
                               "CB05_TOL", "CB05_UNR", "CB05_XYL"]
    bottom_raster_pollutants = ["NH3", "NOx", "PMC", "PM25", "SO2", "CO",
                                "CB05_ALD2", "CB05_ALDX", "CB05_CH4", "CB05_ETH", "CB05_ETHA", "CB05_ETOH", "CB05_FORM",
                                "CB05_IOLE", "CB05_ISOP", "CB05_MEOH", "CB05_NVOL", "CB05_OLE", "CB05_PAR", "CB05_TERP",
                                "CB05_TOL", "CB05_UNR", "CB05_XYL"]
    output_pollutants = ["NH3", "NOx", "PMC", "PM25", "SO2", "CO",
                         "CB05_ALD2", "CB05_ALDX", "CB05_CH4", "CB05_ETH", "CB05_ETHA", "CB05_ETOH", "CB05_FORM",
                         "CB05_IOLE", "CB05_ISOP", "CB05_MEOH", "CB05_NVOL", "CB05_OLE", "CB05_PAR", "CB05_TERP",
                         "CB05_TOL", "CB05_UNR", "CB05_XYL"]

    upper_label = "MEIC"
    bottom_label = "MIX"
    output_label = "MEIC&MIX"

    upper_raster_template = fr"{upper_raster_dir}\MEIC_2017_01__agriculture__NH3.tiff"
    bottom_raster_template = fr"{bottom_raster_dir}\MIX_2010_01__industry__CB05_TOL.tiff"

    upper_resolution = 0.25
    bottom_resolution = 0.25

    sectors = ["power", "transportation", "residential", "industry", "agriculture"]

    upper_year = 2017
    bottom_year = 2010
    output_year = 2017
    # ------------------------------------------------------------------------------------------------------------------

    start_time = time.time()
    main_mosaic(
        upper_raster_dir,
        bottom_raster_dir,
        output_dir,
        upper_raster_pollutants,
        bottom_raster_pollutants,
        output_pollutants,
        upper_label,
        bottom_label,
        output_label,
        upper_raster_template,
        bottom_raster_template,
        upper_resolution,
        bottom_resolution,
        sectors,
        upper_year,
        bottom_year,
        output_year,
    )
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")
