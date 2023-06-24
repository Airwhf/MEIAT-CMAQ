# MEIAT-CMAQ v1.4 User's Guide

MEIAT-CMAQ (the Modular Emission Inventory Allocation Tools for Community Multiscale Air Quality Model) is a tool designed for the CMAQ model that allocates emission inventories. This tool quickly implements the allocation of emission inventories through the interface of Python and ArcGIS Pro 3.X.

This tutorial will guide you through a series of lessons, from basic to advanced, until you are fully familiar with this tool.

**This tool is guaranteed to be completely free for public use!!!**

## Authors Contribution

|        Name        |                         Affiliation                         |   Main Contribution   |
|:------------------:|:----------------------------------------------------------:|:-------------------:|
|   **Haofan Wang (Ph.D. student)**   |   Sun Yat-sen University   |   Model Development, User Manual  |
|   **Jiaxin Qiu (Master's student)**   |    Jilin University   |   Model Development, User Manual  |
| Yiming Liu (Assistant Professor) |    Sun Yat-sen University   |   Special Support    |
|   Qi Fan (Professor)     |  Sun Yat-sen University   |   Special Support    |
|   Xiao Lu (Associate Professor)   |   Sun Yat-sen University   |   Special Support    |
|   Yang Zhang (Associate Professor)   | Chengdu University of Information Technology   |   Special Support    |
|   Kai Wu (Ph.D. student)   |   University of California, Irvine   |   Special Support    |
| Ao Shen (Ph.D. student) | Sun Yat-sen University | User Manual |
| Yinbao Jin (Ph.D. student) |Sun Yat-sen University | User Manual |
| Yifei Xu (Master's student) |  Sun Yat-sen University | User Manual |
| Yuqi Zhu (Master's student) | Sun Yat-sen University | User Manual |

## Contact me

Email: wanghf58@mail2.sysu.edu.cn

## Table of Contents

----------

1. Setting Up the Operating Environment for MEIAT-CMAQ.

* This tutorial will provide a detailed explanation on how to set up the operating environment for MEIAT-CMAQ.

----------

2. [Creating CMAQ emission files for the Pearl River Delta simulation domain using the 2017 emission inventory from MEICv1.3.](Doc/adopt_meic_for_prd_emission_file_en.md)

* This tutorial will help users understand the most basic process of creating CMAQ emission files.

----------

3. [Bypass the spatial allocation step and directly output CMAQ emission files.](Doc/how_to_treat_the_emssion_which_resolution_is_fine_en.md)

* This tutorial is primarily intended to compensate for the shortcomings in **Tutorial 2**. In **Tutorial 2**, we only downscaled coarse emission inventories to finer resolutions. This tutorial will help us understand how to use MEIAT-CMAQ to apply fine-resolution emission inventories to coarse-resolution simulation domains.

----------

4. [Adding East Asian emissions (MIX) to the MEIC inventory.](Doc/how_to_combine_meic_and_mix_en.md)

* This tutorial primarily guides users on how to perform batch mosaic work on GeoTIFF files.

----------

5. [Using local emission sources in the MEIC inventory.](Doc/adopt_local_emission_to_meic_en.md)

* This tutorial will guide users on how to flexibly use MEIAT-CMAQ to simultaneously use tabulated and gridded emission inventories.

----------

6. [Processing annual-scale emission inventories.](Doc/how_to_treat_the_yearly_emission_en.md)

* MEIAT-CMAQ only allows direct processing of monthly-scale emission inventories, but we can convert annual-scale inventories to monthly-scale ones using the monthly time distribution files.

----------

7. [Performing vertical distribution of emission files.](Doc/how_to_do_vertical_allocation_en.md)

* This tutorial will guide users on how to perform vertical allocation of emission inventories using MEIAT-CMAQ.

----------

8. [Generating region files that can be used by CMAQ-ISAM.](Doc/how_to_use_shapefile_for_mask_en.md)

* Creating region files has always been a challenging part of running CMAQ-ISAM. This tutorial will guide users on how to quickly complete the production of region files.

--------------






