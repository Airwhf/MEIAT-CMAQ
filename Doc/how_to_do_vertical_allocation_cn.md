# 如何对排放文件进行垂直分配？

面源排放的垂直分配过程是使用[vertical_allocation.py](../vertical_allocation.py)

* 程序提供了power和industry两个部门的垂直分配方案，分别是`profile-industry.csv`和`profile-power.csv`，用户也可以按照已提供的两个文件格式自定义垂直分配系数。

由于[vertical_allocation.py](../vertical_allocation.py)只能够识别文件名为`profile.csv`的文件，所以在进行分配时，需要将文件复制为`profile.csv`。

以下步骤通过对power部门的排放来进行说明：

1. 复制`profile-power.csv`到`profile.csv`。

2. 打开[vertical_allocation.py](../vertical_allocation.py)修改以下代码：

```python
files = glob.glob(r"output\*_power_*.nc")
```

3. 在终端输入以下命令即可开始运行。

```shell
python .\vertical_allocation.py
```

4. 在`output/vertical`路径下可以看到垂直分配后的结果。
