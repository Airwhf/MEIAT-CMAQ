import os
import pandas as pd
import time
from src_c2f import *


if __name__ == '__main__':

    # ========================================================================================
    # Set GRIDDESC configuration.
    griddesc_file = 'input/GRIDDESC.PRD274x181'
    griddesc_name = 'PRD274x181'    
    
    # Set the coarse grid path.
    big_grid = 'shapefile/MEIC-0P25.shp'
    
    # Set allocator.
    allocator_types = ['raster', 'raster', 'raster', 'raster', 'line']
    allocators = ['landscan-global-2017_nodata.tif', 'power.tif', 'industry.tif', 'agriculture.tif', 'line']
    sectors = ['residential', 'power', 'industry', 'agriculture', 'transportation']
    
    line_files = ["motorway.shp", "primary.shp", "residential.shp", "secondary.shp"]
    line_factors = [0.435798, 0.326848, 0.081712, 0.155642]
    
    # Set the inventory with Geotiff format.
    geotiff_dir = r'F:\data\Emission\MEICv1.3\CB05-2017'  
    
    # Set the inventory.
    inventory_label = 'MEIC'
    inventory_year = 2017  
    
    # Set the inventory period.
    start_date = '2017-01-01'
    end_date = '2017-01-02'
    
    # Species allocation.
    inventory_mechanism = 'MEIC-CB05'
    target_mechanism = 'CB06'
    # ========================================================================================
    # Spatial allocation.
    # ========================================================================================
    start_time = time.time()
    
    main_coarse2fine(griddesc_file, griddesc_name, big_grid, allocator_types, allocators, sectors, geotiff_dir, start_date, end_date, 
                     inventory_label, inventory_year, line_files=line_files, line_factors=line_factors)
    
    # ========================================================================================
    # Create CMAQ emission files (temporal and species allocation).
    # ========================================================================================
    source_dir = f'model_emission_{griddesc_name}'
    periods = pd.period_range(pd.to_datetime(start_date), pd.to_datetime(end_date), freq='D')
    for sector in sectors:
        for emission_date in periods:
            create_emission_file(source_dir, str(emission_date), griddesc_file, griddesc_name, inventory_label, sector, inventory_year,
                                 inventory_mechanism, target_mechanism)
            print(f"Finish: {str(emission_date)} {sector}")
            
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")
