#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :script.py
# @Time      :2024/09/15 17:40:24
# @Author    :Haofan Wang


# =============================================================================================================
# 本程序用于处理 MEIC v1.4 的排放清单，使其能够被MEIAT-CMAQ使用。

# 原始数据的下载地址：
# http://meicmodel.org.cn/?page_id=560

# 下载的时候请选择逐月 分部门 等经纬度投影的排放数据。
# =============================================================================================================

import os
import glob
import numpy as np
import xarray as xr

if __name__ == '__main__':

    # 读取原始数据
    input_dir = '/Volumes/project/post_emissions/747c47'    
    
    # 创建输出目录
    output_dir = '2020'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    # 分物种创建文件
    pollutant = 'CO'
    
    files = glob.glob(f'{input_dir}/*_{pollutant}.nc')
    # Create xarray.dataset to store data.
    ds = xr.Dataset()
    for file in files:
        ds = xr.open_dataset(file)
        xrange = ds['xrange'].values
        yrange = ds['yrange'].values
        emis = np.zeros_like((yrange, xrange))
        
        print(ds)
        
        
        exit(0)
    


