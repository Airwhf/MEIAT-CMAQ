#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time      :2022/12/12 20:07
# @Author    :Haofan Wang
import glob
import os

import xarray as xr

import rasterio as rio
from rasterio.transform import Affine

if __name__ == "__main__":
    # Set where is the origin inventory in.
    fdir = r"H:\MEIC\中国高分辨率大气污染物集成清单"

    # Set the name of inventory.
    files = glob.glob(f"{fdir}/*.nc")

    for file in files:
        ds = xr.open_dataset(file)
        lats = ds.coords["lat"].__array__()
        lons = ds.coords["lon"].__array__()
        lonmin, latmax, lonmax, latmin = lons.min(), lats.max(), lons.max(), lats.min()
        num_lon = ds.__getattr__("xllcorner")
        num_lat = ds.__getattr__("yllcorner")
        res = 0.1

        transform = Affine.translation(lonmin - res / 2, latmin - res / 2) * Affine.scale(res, res)

        # Set sectors.
        sectors = ["POWER", "INDUSTRY", "RESIDENTIAL", "TRANSPORTATION", "SOLVENT", "AGRICULTURE", "BIOMASS", "SHIPPING"]
        # Obtain the pollutant.
        pollutant = os.path.basename(file).split("_")[0]

        for sector in sectors:
            for i in range(12):
                # convert to tons/year
                temp_ds = ds[f"{pollutant}_{sector}"][i, ...]
                mm = r"%.2d" % (i + 1)
                tiffile = f"HEIC_2017_{mm}__{sector}__{pollutant}.tiff"
                # print(ds)
                with rio.open(tiffile,
                              'w',
                              driver='GTiff',
                              height=num_lat,
                              width=num_lon,
                              count=1,
                              dtype=temp_ds.dtype,
                              crs='+proj=latlong',
                              transform=transform, ) as dst:
                    dst.write(temp_ds, 1)
                print(f"Finish and output {tiffile}.")
