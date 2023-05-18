import numpy as np
import rasterio as rio
import rasterio.errors

if __name__ == "__main__":
    """
    Sometimes there are only inventory of PM2.5 and PM10.
    But in the CMAQ model, we need the PMC to input rather PM10,
    thus, we should calculate the PMC inventory via PM2.5 and PM10.
    """
    # Set the input directory.
    input_dir = r"D:\GitHub\MEIAT-CMAQ-data\MIX-2010"

    # Set the inventory prefix.
    prefix = "MIX"

    # Set the months.
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    # months = ["00"]

    # Set the sectors.

    sectors = ['residential', 'transportation', 'power', 'industry', 'agriculture']

    # Set the years.
    years = [2010]

    for month in months:
        for sector in sectors:
            for year in years:
                pm25_file = f"{input_dir}/{prefix}_{year}_{month}__{sector}__PM25.tiff"
                pm10_file = f"{input_dir}/{prefix}_{year}_{month}__{sector}__PM10.tiff"
                try:
                    pm25_dataset = rio.open(pm25_file)
                    pm10_dataset = rio.open(pm10_file)
                except rasterio.errors.RasterioIOError:
                    print(f"skip: {pm25_file} & {pm10_file}")
                    continue

                height = pm25_dataset.height
                width = pm25_dataset.width
                transform = pm25_dataset.transform

                pm25_data = pm25_dataset.read(1)
                pm10_data = pm10_dataset.read(1)
                pmc_data = pm10_data - pm25_data

                # Check the PMC data.
                pmc_data = np.where(pmc_data < 0, 0, pmc_data)

                tiffile = f"{input_dir}/{prefix}_{year}_{month}__{sector}__PMC.tiff"

                with rio.open(tiffile,
                              'w',
                              driver='GTiff',
                              height=height,
                              width=width,
                              count=1,
                              dtype=pmc_data.dtype,
                              crs='+proj=latlong',
                              transform=transform, ) as dst:
                    dst.write(pmc_data, 1)