#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2023/3/22 17:02
# @Author    :Haofan Wang
# @Email     :wanghf58@mail2.sysu.edu.cn
import glob
import os.path

import pandas as pd
from src import encode_title_tiff
import rasterio
import numpy as np

if __name__ == "__main__":
    """
    At first, your title of these files are required this format as following:
    "UKE_1970_00__AGS__nh3.tiff"
    LABEL_YEAR_00__SECTOR__POLLUTANT.tiff
    """
    print("This script is written by Haofan Wang.")
    # Input directory including emission raster.
    input_dir = r"D:\Emission-Inventory\EDGAR\GTiff4IAT_year_reclassification\1970"
    output_dir = r"D:\Emission-Inventory\EDGAR\GTiff4IAT_year_reclassification\monthly-1970"
    os.system(f"mkdir {output_dir}")

    # Search the file in the input directory.
    files = glob.glob(f"{input_dir}/*.tiff")
    factor = pd.read_csv("temporal/monthly.csv")
    for file in files:
        print(file)
        # Open and read the raster as array.
        dataset = rasterio.open(file)
        data = dataset.read(1)
        file_info = encode_title_tiff(os.path.basename(file))
        label = file_info["label"]
        year = file_info["year"]
        month = file_info["month"]
        sector = file_info["sector"]
        species = file_info["pollutant"]
        for month_i in range(1, 13):
            temp_factor = factor.iloc[np.where(factor.monthly.values == month_i)][sector].values[0]
            new_data = data * temp_factor
            mm = "%.2d" % month_i
            output_name = f"{output_dir}/{label}_{year}_{mm}__{sector}__{species}.tiff"
            with rasterio.open(
                    output_name,
                    'w',
                    driver='GTiff',
                    height=new_data.shape[0],
                    width=new_data.shape[1],
                    count=1,
                    dtype=new_data.dtype,
                    crs='+proj=latlong',
                    transform=dataset.transform,
            ) as dst:
                dst.write(new_data, 1)



