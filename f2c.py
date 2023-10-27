# @Time    : 2023/02/21 19:17
# @Author  : Haofan Wang
# @Version : python3.9
# @Email   : wanghf58@mail2.sysu.edu.cn
import os
import time
from src_f2c import *


if __name__ == "__main__":
    # ========================================================================================
    # Set GRIDDESC configuration.
    griddesc_file = 'input/GRIDDESC.CN27km'
    griddesc_name = 'CN27km'    
    
    # Set the inventory with Geotiff format.
    geotiff_dir = r'F:\data\Emission\MEICv1.3\CB05-2017'  
    sectors = ['residential', 'power', 'industry', 'agriculture', 'transportation']
    
    # Set the inventory.
    inventory_label = 'MEIC'
    inventory_year = 2017  
    
    # Set the inventory period.
    start_date = '2017-01-01'
    end_date = '2017-01-02'
    
    # Species allocation.
    inventory_mechanism = 'MEIC-CB05'
    target_mechanism = 'CB06'
    
    # shape factor
    shapefactor = 4
    # ========================================================================================
    
    start_time = time.time()
    output_dir = f'model_emission_{griddesc_name}'
    os.makedirs(output_dir, exist_ok=True)
    periods = pd.period_range(pd.to_datetime(start_date), pd.to_datetime(end_date), freq='D')
    for sector in sectors:
        for emission_date in periods:
            source2cmaq(str(emission_date), griddesc_file, griddesc_name, sector, geotiff_dir, inventory_mechanism, target_mechanism, output_dir, shapefactor=shapefactor)
            
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"### Time consuming: {elapsed_time} s ###")
