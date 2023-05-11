# !/usr/bin/env python
# -*-coding:utf-8 -*-
# @Time    : 2023/01/14 16:01
# @Author  : Haofan Wang
# @Version : python3.9
# @Email   : wanghf58@mail2.sysu.edu.cn

import glob
import os
import re

import xarray as xr
import tqdm

import rasterio as rio
from rasterio.transform import Affine


if __name__ == '__main__':
    # The path of MIX emissions inventory.
    fdir = "/mnt/f/MEIC-排放清单/MIX清单/MIX_2010"
    output_dir = "/mnt/e/GitHub/MyCode/Python/CMAQ-Tools/排放清单工具/排放清单数据库/MIX-2010"

    # Set the year of emission inventory.
    year = 2010

    # Search the files.
    files = glob.glob(f"{fdir}/*.nc")

    # Get the name of pollutants.
    for file in tqdm.tqdm(files):
        ds = xr.open_dataset(file)
        lats = ds.coords["lat"].__array__()
        lons = ds.coords["lon"].__array__()
        lonmin, latmax, lonmax, latmin = lons.min(), lats.max(), lons.max(), lats.min()
        num_lon = lons.shape[0]
        num_lat = lats.shape[0]
        res = 0.25
        transform = Affine.translation(lonmin - res / 2, latmin - res / 2) * Affine.scale(res, res)

        # Set sectors.
        sectors = ["POWER", "INDUSTRY", "RESIDENTIAL", "TRANSPORT", "AGRICULTURE"]
        file_name = os.path.basename(file)
        condition = fr"MICS_Asia_(.*?)_{year}_0.25x0.25.nc"
        pollutant = re.findall(condition, file_name)[0]

        for var_name in list(ds.keys()):
            var = ds[var_name]
            months = var.__getattr__("time").values
            for i in range(12):
                month = "%.2d" % months[i]
                temp_var = var[i, ...].values
                sector = var_name.split("_")[-1]

                if sector == "TRANSPORT":
                    sector_label = "transportation"
                else:
                    sector_label = sector.lower()

                tiffile = f"MIX_{year}_{month}__{sector_label}__{pollutant}.tiff"
                with rio.open(f"{output_dir}/{tiffile}",
                              'w',
                              driver='GTiff',
                              height=num_lat,
                              width=num_lon,
                              count=1,
                              dtype=temp_var.dtype,
                              crs='+proj=latlong',
                              transform=transform, ) as dst:
                    dst.write(temp_var, 1)
                # print(f"Finish and output {output_dir}/{tiffile}.")
