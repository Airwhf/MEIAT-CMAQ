#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :script.py
# @Time      :2024/09/15 18:14:35
# @Author    :Haofan Wang

# 原始数据下载地址：http://meicmodel.org.cn/?page_id=2740&lang=en

# =============================================================================================================
# - Gridded emissions are prepared in NetCDF format.
# - Species included: BC, OC, CO, CO2, NH3, NMVOC, NOx, PM10, PM25, SO2, in unit of Mg/month/grid (10^6 g/month/grid)
# - Chemical mechanisms included: SAPRC99, SAPRC07, CB05, in unit of Mmol/month/grid(10^6 mol/month/grid)
# - Filename format: MIXv2.3_(species name)_xxxx(year)_monthly_0.1deg.nc.
# - For each species, emissions by seven sectors are developed: Residential, Industry, Power, 
#   Transportation, Agriculture, Open_biomass, Shipping.
# - Spatial resolution: 0.1 x 0.1 degree. Domain: 60.05 E – 153.95 E (center of grid, longitude), 
#   14.95 S – 59.95 N (center of grid, latitude). Dimension of dataset: 940 (cols) x 750 (rows) x 12 (months).
# =============================================================================================================


import os
import glob
import pandas as pd
import numpy as np
import xarray as xr
import calendar

def seconds_in_month(year, month):
    year = int(year)
    month = int(month)
    # 获取当月的天数
    days_in_month = calendar.monthrange(year, month)[1]
    # 每天的秒数
    seconds_per_day = 24 * 60 * 60
    # 计算当月的总秒数
    return days_in_month * seconds_per_day

def calc_area(lat, resolution=0.1):
    """_summary_

    Args:
        lat (_type_): _description_
        resolution (float, optional): _description_. Defaults to 0.1.

    Returns:
        units (km^2): _description_
    """
    Re = 6371.392
    X = Re * np.cos(lat * (np.pi / 180)) * (np.pi / 180) * resolution
    Y = Re * (np.pi / 180) * resolution
    return X * Y

if __name__ == '__main__':

    # 读取原始数据
    input_dir = '/Volumes/project/post_emissions/mix_emis_2017'

    # 创建输出目录
    emissions_year = '2017'
    output_dir = emissions_year
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    # 计算当前年份每个月有多少秒
    seconds_list = []
    for month in range(1, 13):
        seconds = seconds_in_month(emissions_year, month)
        seconds_list.append(seconds)
    seconds_list = np.array(seconds_list)

    files = glob.glob(f"{input_dir}/*.nc")
    for f in files:
        file_name = os.path.basename(f)
        species = file_name.split('MIXv2.3_')[1].split(f'_{emissions_year}')[0]
        
        # 读取原始数据
        ds = xr.open_dataset(f)
        cell_area = calc_area(ds['latitude'].values) * 10**6 # m^2
        
        new_ds = xr.Dataset()
        new_ds.coords['time'] = pd.date_range(f'{emissions_year}-01-01', periods=12, freq='MS') + pd.Timedelta(days=14)
        new_ds.coords['lon'] = xr.DataArray(ds['longitude'][0, :], dims=('lon'), attrs={'units': 'degree_east'})
        new_ds.coords['lat'] = xr.DataArray(ds['latitude'][:, 0], dims=('lat'), attrs={'units': 'degree_north'})
        # print(new_ds)
        
        # 写入变量
        for var_item in ds.data_vars:
            if var_item == 'longitude' or var_item == 'latitude':
                continue
            
            var_ds = ds[var_item]
            if var_ds.units == 'Mg per month':
                # Convert to kg/m2/s.
                factor = np.array(10**3 / cell_area)  # kg/m2
                factor_array = np.zeros((12, factor.shape[0], factor.shape[1]))
                for month_i in range(12):
                    factor_array[month_i, :, :] = factor[:, :] / seconds_list[month_i]
            elif var_ds.units == 'Mmole per month':
                # Convert to mol/m2/s
                factor = np.array(10**6 / cell_area)  # mol/m2
                factor_array = np.zeros((12, factor.shape[0], factor.shape[1]))
                for month_i in range(12):
                    factor_array[month_i, :, :] = factor[:, :] / seconds_list[month_i]
            else:
                print(f"{var_item} units is not supported.")
                continue
            
            
            # 转化为kg/m2/s或者mol/m2/s
            emis_amount = ds[var_item].values * factor_array
            
            # Create a new variable in the new dataset
            new_ds[var_item] = xr.DataArray(
                emis_amount, dims=('time', 'lat', 'lon'),
                coords={'time': new_ds.coords['time'], 'lat': new_ds.coords['lat'], 'lon': new_ds.coords['lon']}
            )
            new_ds[var_item].values = emis_amount
            new_ds[var_item].attrs['units'] = 'kg m-2 s-1'
            new_ds[var_item].attrs['Fillvalue'] = -9999

        output_name = f"{output_dir}/MIXv2.3_{species}_{emissions_year}.nc"
        new_ds.to_netcdf(output_name, format='NETCDF4')
        print(f"Done: {output_name}")
        # exit()
        
    # 处理PMC
    pm10_ds = xr.open_dataset(f"{output_dir}/MIXv2.3_PM10_{emissions_year}.nc")
    pm25_ds = xr.open_dataset(f"{output_dir}/MIXv2.3_PM25_{emissions_year}.nc")
    
    pmc_ds = pm10_ds.copy()
    for var_item in pm10_ds.data_vars:
        if var_item == 'longitude' or var_item == 'latitude':
            continue
        sector = var_item.split('PM10_')[1]
        _pm10 = pm10_ds['PM10_'+sector].values
        _pm25 = pm25_ds['PM25_'+sector].values
        
        # Rename the variable in pmc_ds.
        pmc_ds['PMC_'+sector] = xr.DataArray(
            _pm10 - _pm25, dims=('time', 'lat', 'lon'),
            coords={'time': pmc_ds.coords['time'], 'lat': pmc_ds.coords['lat'], 'lon': pmc_ds.coords['lon']}
        )
        pmc_ds[var_item].values = _pm10 - _pm25
        pmc_ds[var_item].attrs['units'] = 'kg m-2 s-1'
        pmc_ds[var_item].attrs['Fillvalue'] = -9999
        # Delete the xarray.dataarray.
        pmc_ds.drop_vars(var_item)
        
    output_name = f"{output_dir}/MIXv2.3_PMC_{emissions_year}.nc"
    pmc_ds.to_netcdf(output_name, format='NETCDF4')
    print(f"Done: {output_name}")
        
        
    