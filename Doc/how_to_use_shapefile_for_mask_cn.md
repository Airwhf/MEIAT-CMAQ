# 如何使用shapefile文件生成CMAQ中的mask文件？

------------------------

**作者：邱嘉馨**

------------------------

## 1. 准备shapefile文件

shapefile文件主要有以下几点要求：

* 投影必须为WGS1984投影。
* 属性表中不能有中文字符。
* 属性表中必须有字符串字段被程序提取。
* 该字符串字段中的必须为大写字母。

具体格式可以参考：[Anyang-around.shp](../shapefile/Anyang-around.shp)

## 2. 配置好文件

除了上述需要在代码中修改的部分以外， `GRIDDESC`文件也是程序所必须的，但是此文件将从namelist.input中去获取。

```python
# ------------------------------------------------------------
# Shapefile path.
shapefile_path = "shapefile文件路径"
# The field of each area.
field = "字符串字段名称"
# The output path.
output_name = "输出文件名称"
# ------------------------------------------------------------
```

## 3. 运行程序

在终端中输入：

```shell
python ./Create_CMAQ_mask.py
```

即可运行，并输出文件。


