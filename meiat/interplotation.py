#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :interplotation.py
# @Time      :2024/09/16 14:33:31
# @Author    :Haofan Wang

import pandas as pd
import numba

# def interplotation(emis_ds, target_resolution=0.01):
#     lon_max = emis_ds.coords['lon'].max().values
#     lon_min = emis_ds.coords['lon'].min().values
#     lat_max = emis_ds.coords['lat'].max().values
#     lat_min = emis_ds.coords['lat'].min().values
#     ds_out = xr.Dataset(    
#         {
#             "lat": (["lat"], np.arange(lat_min, lat_max+target_resolution, target_resolution), {"units": "degrees_north"}),
#             "lon": (["lon"], np.arange(lon_min, lon_max+target_resolution, target_resolution), {"units": "degrees_east"}),
#         }
#     )   
#     regridder = xe.Regridder(emis_ds, ds_out, "conservative")
#     dr_out = regridder(emis_ds, keep_attrs=True)

#     return dr_out

import pandas as pd

def interplotation_to_cmaq(emis_ds, gf):
    
    # 获取CMAQ网格经纬度
    lon2d = gf.variables['longitude'].__array__()
    lat2d = gf.variables['latitude'].__array__()
    
    #TODO 遍历每个经纬度，寻找最近点数据
    df = pd.DataFrame(columns=['lon', 'lat', 'emissions'])
    lon_list, lat_list, emis_list = [], [], []
    for i in range(gf.getncattr('NROWS')):
        for j in range(gf.getncattr('NCOLS')):
            stn_lat = lat2d[i, j]
            stn_lon = lon2d[i, j]
            # 找到排放数据中最近的点的数值
            emis_point = emis_ds.sel(lat=stn_lat, lon=stn_lon, method='nearest').values
            
            lon_list.append(stn_lon)
            lat_list.append(stn_lat)
            emis_list.append(emis_point)

    df['lon'] = lon_list
    df['lat'] = lat_list
    df['emissions'] = emis_list
                   
    return df

