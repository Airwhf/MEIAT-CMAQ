#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2023/4/15 15:48
# @Author    :Jiaxin Qiu

import glob
import os.path

import rasterio
import xarray as xr
import pyproj
import numpy as np

"""
Data access: https://edgar.jrc.ec.europa.eu/dataset_ap61
"""

if __name__ == '__main__':
    print("This script is written by Jiaxin Qiu.")

    input_dir = r"I:\CEDSv2\2013"
    output_dir = r"I:\CEDSv2\2013\GTiff"

    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)

    files = glob.glob(f"{input_dir}/*.nc")
    for file in files:
        # 定义WGS84等经纬度投影
        crs_proj = pyproj.CRS.from_string('EPSG:4326')

        # 读取NetCDF数据集
        ds = xr.open_dataset(file)

        sub_name = os.path.basename(file)
        yyyy = sub_name.split("_")[-1].split(".")[0]
        
        # 获取所有数据变量列表
        variables = list(ds.data_vars.keys())
        # print(variables)

        for variable in variables:
            data_array = ds[variable]
            sector = variable.split("_")[1]
            pollutant = variable.split("_")[0]

            for month in range(1, data_array.shape[0]+1):
                month = r"%.2d" % month
                temp_data_array = data_array[int(month)-1, ...]
                # print(temp_data_array)
                # 获取空间信息
                height, width = temp_data_array.shape[0], temp_data_array.shape[1]
                lats, lons = temp_data_array.coords["lat"], temp_data_array.coords["lon"]
                south, north = lats.values.min(), lats.values.max()
                # south, north = lats.values.max(), lats.values.min()
                west, east = lons.values.min(), lons.values.max()
                # print(height, width, south, north, west, east)
                
                temp_data_array = np.flipud(np.where(temp_data_array < 0, 0, temp_data_array))
                
                # MEIAT-CMAQ: LABEL_YYYY_MM__SECTOR__POLUTANT.tiff
                _sub_name = f"CEDS_{yyyy}_{month}__{sector}__{pollutant}.tiff"
                # print(temp_data_array)
                # # 创建GTiff文件
                with rasterio.open(f'{output_dir}/{_sub_name}.tiff', 'w', driver='GTiff',
                                width=width, height=height, count=1,
                                dtype=temp_data_array.dtype.name, nodata=0,
                                transform=rasterio.transform.from_bounds(west, south, east, north, width, height),
                                crs=crs_proj) as dst:
                    # 将NetCDF数据写入GTiff
                    dst.write(temp_data_array * 10E-3 * 50 * 50 * 1000000 * 2592000, 1)
                print(f'{output_dir}/{_sub_name}')
                # exit()

        
