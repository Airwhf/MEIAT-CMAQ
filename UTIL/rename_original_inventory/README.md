# 重命名原始排放清单文件名

* 修改输入参数
```python
tbl_name = {"org": ["PMcoarse"],
            "new": ["PMC"]}

input_dir = r"H:\MEIC\GeoTiff-2017"
output_dir = r"H:\MEIC\GeoTiff-2017_rename"
```
* 运行代码
```shell
cd UTIL/rename_original_inventory
python ./rename_original_inventory_(pollutant).py
```

