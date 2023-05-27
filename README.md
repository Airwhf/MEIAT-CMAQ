# MEIAT-CMAQ v1.3.4

开发者：
* 王浩帆 （中山大学 大气科学学院）
* 邱嘉馨 （吉林大学 新能源与环境学院）

特别贡献：
* 樊琦 （中山大学 大气科学学院）
* 刘一鸣 （中山大学 大气科学学院）
* 张洋 （成都信息工程大学 资源与环境学院）
* 吴锴 （University of California, Irvine）

## 简介

MEIAT-CMAQ是一个针对CMAQ模型的模块化排放清单分配工具，可以灵活的处理各类排放清单，包括常见的网格化和表格化排放清单。该工具采用Python-ArcGIS来完成空间分配过程，主要功能包括：

1.	清单的空间分配，支持栅格化和Shapefile（线）的排放因子。
2.	清单的时间分配。
3.	清单的物种分配。
4.	清单的垂直分配。
5.	输出可以供CMAQ直接使用的排放文件。

## 教程

认真完成以下几个教程，你可以很容易的上手**MEIAT-CMAQ**。

1. [如何使用2017年的MEIC清单制作珠三角的排放文件？](Doc/1-adopt_meic_for_prd_emission_file.md)
2. [原始清单分辨率如果小于模拟域网格分辨率应该如何处理？](Doc/how_to_treat_the_emssion_which_resolution_is_fine.md)
3. [如何同时使用MEIC清单和MIX清单？](Doc/how_to_combine_meic_and_mix.md)
4. 如何同时使用本地源清单和MEIC清单？
5. [如何使用shapefile文件生成CMAQ中的mask文件？](Doc/how_to_use_shapefile_for_mask.md)
6. [如何处理只有年总量的排放清单？](Doc/how_to_treat_the_yearly_emission.md)
7. [如何对排放文件进行垂直分配？](Doc/how_to_do_vertical_allocation.md)

## 数据下载

1. [排放因子数据下载](allocator/README.md)

## 前处理和后处理模块使用说明

### 前处理模块

* [重命名原始排放清单名称](UTIL/rename_original_inventory)





