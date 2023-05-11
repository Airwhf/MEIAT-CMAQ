#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2023/4/29 10:48
# @Author    :Jiaxin Qiu

import glob
import os.path

import tqdm
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS
import re

if __name__ == "__main__":
    print("This script is written by Jiaxin Qiu.")
    # ------------------------------------------
    input_dir = r"H:\MEIC\QJX-MEIC-2019-2020\2019"
    output_dir = r"H:\MEIC\QJX-MEIC-2019-2020\GeoTiff-2019"
    # ------------------------------------------

    if os.path.exists(output_dir) is False:
        os.mkdir(output_dir)

    files = glob.glob(f"{input_dir}/*.asc")

    for file in tqdm.tqdm(files):
        sub_name = os.path.basename(file)
        # condition = f"(.*?)_(.*?)_(.*?)_(.*?).asc"
        condition = f"(.*?)_(.*?)__(.*?)__(.*?).asc"  # For 2019 and 2020.
        encode_name = re.findall(condition, sub_name)[0]
        year = r"%.4d" % int(encode_name[0])
        mm = r"%.2d" % int(encode_name[1])
        sector = encode_name[2]
        pollutant = encode_name[3].replace(".", "")
        output_name = f"{output_dir}/MEIC_{year}_{mm}__{sector}__{pollutant}.tiff"

        # 以只读模式打开文件
        with open(file, 'r', encoding='utf-8') as file:
            # 逐行读取文件内容，并以空格为分隔符分割每行，最后将其添加到数组（列表）中
            lines = [line.strip().split() for index, line in enumerate(file) if index >= 6]

        # 打印读取到的数组（列表）
        _ = np.array(lines, dtype="float")
        z = np.where(_ == -9999.0, 0.0, _)

        # 最大最小经纬度
        min_long, min_lat, max_long, max_lat = 70.0, 10.0, 150.0, 60.0

        # 分辨率
        x_resolution = 0.25
        y_resolution = 0.25

        # 计算栅格的行和列
        width = int((max_long - min_long) / x_resolution)
        height = int((max_lat - min_lat) / y_resolution)

        # 创建GeoTIFF文件的变换矩阵
        transform = from_bounds(min_long, min_lat, max_long, max_lat, width, height)

        # 定义GeoTIFF文件的元数据
        metadata = {
            "driver": "GTiff",
            "height": height,
            "width": width,
            "count": 1,
            "dtype": rasterio.float32,
            "crs": CRS.from_epsg(4326),
            "transform": transform,
        }

        # 创建GeoTIFF文件
        with rasterio.open(output_name, "w", **metadata) as dst:
            dst.write(z, 1)  # 将数据写入波段1




