# iObjectsPy 完整 API 参考（增强版）

> 版本：iObjectsPy 12.0.0  
> 文档：https://iobjectspy.supermap.io/html_zh/  
> 适用：Python 3.6 ~ 3.10

---

## 模块总览

| 模块 | 功能 |
|------|------|
| `iobjectspy` | 主包，含所有子模块 |
| `iobjectspy.analyst` | 空间分析（矢量+栅格） |
| `iobjectspy.conversion` | 数据导入导出格式转换 |
| `iobjectspy.data` | 工作空间/数据源/数据集/几何对象 |
| `iobjectspy.enums` | 枚举常量 |
| `iobjectspy.env` | 环境配置（Java路径等） |
| `iobjectspy.mapping` | 地图制图/图层/专题图 |
| `iobjectspy.threeddesigner` | 三维场景与三维设计 |
| `iobjectspy.ml` | 机器学习（目标检测、语义分割等） |
| `iobjectspy.rpc` | 远程过程调用/分布式计算 |

---

## 1. 初始化

```python
import iobjectspy as spy

# 设置 Java 库路径（必须在其他操作前调用）
spy.set_iobjects_java_path(r"D:\software\supermap-idesktopx-2025-windows-x64-bin\bin")

# 设置并发线程数（可选）
spy.set_omp_num_threads(4)
```

---

## 2. 工作空间（Workspace）

```python
from iobjectspy import Workspace, WorkspaceConnectionInfo, WorkspaceType

# 打开 smwu 工作空间
ws = Workspace()
conn = WorkspaceConnectionInfo()
conn.server = r"D:\data\MyProject.smwu"
conn.type = WorkspaceType.SMWU
ws.open(conn)

# 获取地图/场景列表
maps = spy.list_maps(ws)         # 地图名称列表
scenes = ws.scenes.names         # 场景名称列表

# 保存和关闭
ws.save()
ws.save_as(r"D:\data\MyProject_backup.smwu")
ws.close()
```

---

## 3. 数据源（Datasource）

```python
from iobjectspy import DatasourceConnectionInfo, EngineType

# 打开 UDB 数据源
conn = DatasourceConnectionInfo()
conn.server = r"D:\data\world.udb"
conn.engine_type = EngineType.UDB
ds = spy.open_datasource(conn)

# 快捷写法（路径字符串）
ds = spy.open_datasource(r"D:\data\world.udb")

# 创建新 UDB 数据源
spy.create_datasource(r"D:\data\new.udb")
spy.create_datasource(r"D:\data\new.udbx", engine_type=EngineType.UDBX)

# 数据源操作
print(ds.dataset_names)          # 查看所有数据集名
dataset = ds["Countries"]        # 获取数据集（按名称）
dataset = ds.get_dataset("Countries")  # 等效写法
spy.list_datasources()           # 列出所有已打开数据源
spy.close_datasource(ds)         # 关闭数据源
```

---

## 4. 矢量数据集（DatasetVector）

```python
from iobjectspy import DatasetVector, DatasetType, FieldInfo, FieldType

# 获取矢量数据集
dv = ds["Countries"]    # 类型：DatasetVector

# ─── 遍历要素 ───
rs = dv.get_recordset(True)     # True=只读，False=可编辑
rs.move_first()
while not rs.is_EOF:
    geom = rs.get_geometry()         # 获取几何对象
    name = rs.get_field_value("Name") # 获取属性值
    smid = rs.get_field_value("SmID") # 系统字段：SmID
    print(name, geom.inner_point)
    rs.move_next()
rs.close()

# ─── SQL 查询 ───
rs = dv.query("Pop > 1000000")
rs = dv.query("Name = 'China'")
rs = dv.query_with_filter("Pop > 1000000", order_by="Pop DESC")

# ─── 转为 DataFrame ───
import iobjectspy as spy
df = spy.datasetvector_to_df(dv)               # 全部字段
df = spy.datasetvector_to_df(dv, fields=["Name", "Pop"])  # 指定字段

# ─── 从 DataFrame 写回 ───
spy.df_to_datasetvector(df, out_datasource=ds, out_dataset="Result")

# ─── 字段操作 ───
fields = dv.field_infos                  # 所有字段信息
dv.add_field_info(FieldInfo("NewField", FieldType.DOUBLE))  # 添加字段
dv.delete_field("OldField")              # 删除字段
```

---

## 5. 栅格数据集（DatasetGrid / DatasetImage）

```python
from iobjectspy import DatasetGrid, DatasetImage

# 获取栅格数据集
grid = ds["DEM"]    # DatasetGrid（连续值，如高程）
img = ds["DOM"]     # DatasetImage（影像，如遥感影像）

# 转为 numpy 数组
arr = spy.datasetraster_to_numpy_array(grid)
print(arr.shape, arr.dtype)   # (rows, cols), float64

# numpy 写回栅格
spy.numpy_array_to_datasetraster(arr, out_datasource=ds, out_dataset="NewGrid",
                                  bounds=grid.bounds, pixel_format=grid.pixel_format)

# 转为 xarray（含坐标信息）
xarr = spy.datasetraster_to_df_or_xarray(grid, as_xarray=True)

# 栅格基本信息
print(grid.width, grid.height)     # 像元列数、行数
print(grid.cell_size_x)            # 像元大小（X方向）
print(grid.bounds)                 # 空间范围（Rectangle）
print(grid.no_value)               # 无效值（NoData）
```

---

## 6. 几何对象（Geometry）

```python
from iobjectspy import GeoPoint, GeoLine, GeoRegion, Point2D, Point3D

# 点
pt = GeoPoint(116.4, 39.9)           # 经度, 纬度

# 线
pts = [Point2D(0, 0), Point2D(1, 1), Point2D(2, 0)]
line = GeoLine(pts)

# 面
pts = [Point2D(0,0), Point2D(1,0), Point2D(1,1), Point2D(0,1), Point2D(0,0)]
region = GeoRegion(pts)

# 几何操作
region.inner_point           # 内部代表点
region.bounds               # 外接矩形
geom.to_geojson()            # 转为 GeoJSON 字符串
GeoRegion.from_geojson(json_str)  # 从 GeoJSON 创建

# WKT 互转
wkt = geom.to_wkt()
geom2 = Geometry.from_wkt(wkt)
```

---

## 7. 空间分析（analyst 模块）

### 7.1 缓冲区分析

```python
# 基础缓冲区
spy.create_buffer(
    source_dataset='D:/data/world.udb/Cities',
    left_distance=5000,          # 缓冲距离（米）
    right_distance=5000,         # 右侧距离（线数据用，左右可不同）
    out_datasource='D:/data/world.udb',
    out_dataset='CitiesBuffer',
    unit='Meter',
    semicircle_line_segment=4    # 端部半圆的线段数
)

# 多环缓冲区
spy.create_multi_buffer(
    source_dataset=dv,
    distances=[1000, 3000, 5000],   # 多个距离
    out_datasource=ds,
    out_dataset='MultiBuffer'
)
```

### 7.2 叠加分析

```python
from iobjectspy import OverlayMode

# 通用叠加接口
spy.overlay(
    source_dataset='D:/data.udb/Layer1',
    operate_dataset='D:/data.udb/Layer2',
    overlay_mode=OverlayMode.INTERSECT,   # 或 UNION/ERASE/CLIP/IDENTITY/UPDATE/XOR
    out_datasource='D:/data.udb',
    out_dataset='Result'
)

# 快捷叠加函数
spy.intersect(source, operate, out_ds, out_name)   # 相交
spy.union(source, operate, out_ds, out_name)        # 合并
spy.erase(source, erase, out_ds, out_name)          # 擦除
spy.clip(source, clip, out_ds, out_name)            # 裁剪（保留source在clip内的部分）
spy.identity(source, identity, out_ds, out_name)    # 标识
spy.xor(source, operate, out_ds, out_name)          # 对称差

# 多图层叠加
spy.multilayer_overlay(
    datasets=[ds["Layer1"], ds["Layer2"], ds["Layer3"]],
    overlay_mode=OverlayMode.INTERSECT,
    out_datasource=ds,
    out_dataset='MultiResult'
)
```

### 7.3 其他矢量分析

```python
# 矢量裁剪
spy.clip_vector(
    source_dataset=dv_big,
    clip_dataset=dv_boundary,
    out_datasource=ds,
    out_dataset='Clipped'
)

# 溶解/融合
spy.dissolve(
    source_dataset=dv,
    dissolve_fields=['Province'],           # 按省份融合
    statistic_dict={'Pop': 'SUM', 'Area': 'SUM'},  # 统计字段
    out_datasource=ds,
    out_dataset='Dissolved'
)

# 泰森多边形（Voronoi）
spy.create_thiessen_polygons(
    source_dataset='D:/data.udb/StationPoints',
    out_datasource=ds,
    out_dataset='Thiessen',
    clip_region=boundary_geometry
)

# 核密度分析
spy.kernel_density(
    source_dataset='D:/data.udb/Events',
    search_radius=5000,       # 搜索半径（米）
    cell_size=100,            # 输出栅格分辨率（米）
    weight_field='Weight',    # 权重字段（可选）
    out_datasource='D:/data.udb',
    out_dataset='KernelDensity'
)

# 区域制表
spy.tabulate_area(
    source_dataset='D:/data.udb/Districts',        # 区域图层
    classify_dataset='D:/data.udb/LandUse',        # 分类图层
    out_datasource=ds,
    out_dataset='TabulateResult'
)

# 光滑矢量
spy.smooth_vector(source_dataset=line_dv, smooth_factor=5,
                  out_datasource=ds, out_dataset='SmoothedLine')

# 简化矢量
spy.resample_vector(source_dataset=dv, tolerance=100.0,
                    out_datasource=ds, out_dataset='Simplified')
```

### 7.4 栅格分析

```python
# 坡度、坡向（DEM分析）
spy.calculate_slope(dem_dataset, out_ds=ds, out_name='Slope',
                    z_factor=1.0, unit='DEGREE')
spy.calculate_aspect(dem_dataset, out_ds=ds, out_name='Aspect')

# 栅格重采样
spy.resample_raster(source=grid, cell_size=30,
                    out_datasource=ds, out_dataset='Resampled30m',
                    resample_method='BILINEAR')  # NEAREST/BILINEAR/CUBIC

# 栅格重分级
spy.reclass_grid(
    source=land_use_grid,
    mapping_table={1: 10, 2: 20, 3: 10, 4: 30},  # 原值:新值
    out_datasource=ds,
    out_dataset='Reclassed'
)

# 栅格聚合
spy.aggregate_grid(source=fine_grid, cell_factor=5,
                   out_datasource=ds, out_dataset='Aggregated',
                   aggregation_type='MEAN')   # MEAN/MAX/MIN/SUM

# 裁剪栅格
spy.clip_raster(source_raster=dem, clip_region=boundary_geom,
                out_datasource=ds, out_dataset='ClippedDEM')

# 栅格擦除与填充
spy.erase_and_replace_raster(
    source_raster=dem,
    erase_region=cloud_mask,
    replace_value=0,          # 填充值
    out_datasource=ds,
    out_dataset='Filled'
)
```

### 7.5 插值分析

```python
from iobjectspy import InterpolationIDWParameter, InterpolationKrigingParameter

# IDW 插值
idw_param = InterpolationIDWParameter()
idw_param.max_point_count = 12     # 邻近点数
idw_param.power = 2                # 权重指数
spy.interpolate(
    source_dataset='D:/data.udb/SamplePoints',
    z_field='Elevation',
    param=idw_param,
    out_datasource='D:/data.udb',
    out_dataset='IDW_Result',
    cell_size=30
)

# Kriging 插值
krig_param = InterpolationKrigingParameter()
krig_param.max_point_count = 12
spy.interpolate(
    source_dataset=sample_points,
    z_field='Elevation',
    param=krig_param,
    out_datasource=ds,
    out_dataset='Kriging_Result',
    cell_size=30
)
```

---

## 8. 数据导入导出（conversion 模块）

### 8.1 矢量数据导入

```python
# Shapefile 导入
spy.import_shape(
    source_file=r'D:\data\boundary.shp',
    out_datasource=ds,
    out_dataset='Boundary',
    import_charset='UTF-8'
)

# GeoJSON 导入
spy.import_geojson(r'D:\data\points.geojson', out_datasource=ds)

# KML/KMZ 导入
spy.import_kml(r'D:\data\places.kml', out_datasource=ds)

# CAD 导入
spy.import_dwg(r'D:\data\drawing.dwg', out_datasource=ds)
spy.import_dxf(r'D:\data\drawing.dxf', out_datasource=ds)

# OSM 导入
spy.import_osm(r'D:\data\map.osm', out_datasource=ds)

# CSV 导入（含坐标字段的点数据）
spy.import_csv(
    r'D:\data\data.csv',
    out_datasource=ds,
    out_dataset='Data',
    x_field='longitude',      # 经度字段
    y_field='latitude',       # 纬度字段
    charset='UTF-8'
)
```

### 8.2 栅格数据导入

```python
# GeoTIFF 导入
spy.import_tif(r'D:\data\dem.tif', out_datasource=ds)
spy.import_tif(r'D:\data\dom.tif', out_datasource=ds, out_dataset='DOM')

# IMG 格式
spy.import_img(r'D:\data\landuse.img', out_datasource=ds)
```

### 8.3 三维数据导入

```python
# OSGB 倾斜摄影导入
spy.import_osgb(r'D:\data\tileset', out_datasource=ds, out_dataset='OSGB_Tiles')

# S3M 缓存导入
spy.import_s3m(r'D:\data\model.s3m', out_datasource=ds)

# 点云 LAS 导入
spy.import_las(r'D:\data\cloud.las', out_datasource=ds, out_dataset='PointCloud')
```

### 8.4 矢量数据导出

```python
# 导出为 Shapefile
spy.export_to_shape(dataset, r'D:\output\boundary.shp', charset='UTF-8')

# 导出为 GeoJSON
spy.export_to_geojson(dataset, r'D:\output\data.geojson')

# 导出为 KML
spy.export_to_kml(dataset, r'D:\output\data.kml')

# 导出为 CSV
spy.export_to_csv(dataset, r'D:\output\data.csv')

# 导出为 DXF
spy.export_to_dxf(dataset, r'D:\output\drawing.dxf')
```

### 8.5 栅格数据导出

```python
# 导出为 GeoTIFF
spy.export_to_tif(raster_dataset, r'D:\output\dem.tif')

# 导出为 PNG/JPG
spy.export_to_png(raster_dataset, r'D:\output\image.png')
spy.export_to_jpg(raster_dataset, r'D:\output\image.jpg')
```

---

## 9. 地图制图（mapping 模块）

```python
# 获取工作空间中的地图
map_obj = spy.get_map(ws, "WorldMap")

# 保存地图（更新到工作空间）
spy.add_map(ws, "WorldMap", map_obj)

# 创建专题图（在 iDesktopX 内置 Python 窗口使用）
# 通过 GUI 向导创建，或通过 mapping API 编程创建

# 导出地图为图片
spy.export_map_to_image(
    map_obj,
    output_path=r"D:\output\map.png",
    width=1920, height=1080,
    dpi=150
)
```

---

## 10. 三维场景（threeddesigner 模块）

```python
from iobjectspy.threeddesigner import *

# 获取场景
scene = spy.get_scene(ws, "MyScene")

# 添加地形图层（DEM）
terrain_layer = scene.terrain_layers.add(dem_dataset)

# 添加影像图层（DOM）
image_layer = scene.image_layers.add(dom_dataset)

# 添加三维矢量图层
vector3d_layer = scene.general_layers.add(region3d_dataset)

# 添加 OSGB 倾斜摄影
scene.general_layers.add_osgb(r"D:\data\osgb_tileset")

# 添加 S3M 模型缓存
scene.general_layers.add_s3m(r"D:\data\model.s3m")

# 相机控制
scene.camera.set_position(lon=116.4, lat=39.9, altitude=1000)
scene.camera.set_heading(0)    # 朝北
scene.camera.set_tilt(45)      # 倾斜角45°

# 飞行到指定位置
scene.fly_to(lon=116.4, lat=39.9, altitude=500, duration=3.0)

# 截图
scene.export_to_image(r"D:\output\scene.png", width=1920, height=1080)
```

---

## 11. 类型转换工具

```python
# 矢量类型互转
spy.dataset_region_to_line(region_ds, out_ds, out_name)    # 面→线（边界）
spy.dataset_line_to_region(line_ds, out_ds, out_name)      # 线→面（闭合线）
spy.dataset_line_to_point(line_ds, out_ds, out_name)       # 线→节点
spy.dataset_point_to_line(point_ds, out_ds, out_name,
                          order_field='SequenceNo')         # 点→线

# 栅格与矢量互转
spy.raster_to_vector(raster=land_use, out_ds=ds, out_name='LandUseVector',
                     smooth=True)           # 栅格→矢量面
spy.vector_to_raster(vector=land_use_dv,
                     cell_size=30,
                     value_field='LandType',
                     out_datasource=ds,
                     out_dataset='LandUseRaster')  # 矢量→栅格
```

---

## 12. 拓扑处理

```python
# 拓扑检查（返回错误报告）
errors = spy.topology_validate(dataset, rules=['NO_OVERLAP', 'MUST_BE_CLOSED'])

# 拓扑构面（由线构建面）
spy.topology_build_regions(
    source_line=road_lines,
    out_datasource=ds,
    out_dataset='BuildRegions'
)

# 拓扑处理（自动修复）
spy.topology_processing(
    dataset=messy_polygons,
    out_datasource=ds,
    out_dataset='CleanPolygons',
    snap_tolerance=0.001      # 容差
)
```

---

## 13. 网络分析

```python
# 构建网络数据集
spy.build_network_dataset(
    line_dataset=road_dv,
    out_datasource=ds,
    out_dataset='RoadNetwork',
    node_snap_tolerance=1.0
)

# 最短路径分析
result = spy.path_line(
    network_dataset=network_dv,
    start_point=Point2D(116.4, 39.9),
    end_point=Point2D(121.5, 31.2),
    weight_field='Length'
)

# 服务区分析
spy.build_facility_network_directions(
    network_dataset=network_dv,
    facility_points=[Point2D(116.4, 39.9)],
    max_weight=1000,           # 最大成本（如距离1000米）
    weight_field='Length',
    out_datasource=ds,
    out_dataset='ServiceArea'
)
```

---

## 14. 常用枚举常量

```python
from iobjectspy import (
    EngineType,         # UDB, UDBX, SQL, ORACLE, POSTGRESQL, GOOGLEMAPS...
    DatasetType,        # POINT, LINE, REGION, GRID, IMAGE, NETWORK, POINT3D, LINE3D...
    FieldType,          # TEXT, INT16, INT32, INT64, DOUBLE, BOOLEAN, DATE, BINARY...
    WorkspaceType,      # SMWU, SXWU, SXW, SMW, DEFAULT（默认XML格式）
    OverlayMode,        # INTERSECT, UNION, ERASE, CLIP, IDENTITY, UPDATE, XOR
    Unit,               # METER, KILOMETER, MILE, FOOT, DEGREE...
    BufferEndType,      # FLAT, ROUND
    StatisticsType,     # SUM, MAX, MIN, AVERAGE, STD, COUNT, VARIANCE...
    SpatialQueryMode,   # INTERSECT, CONTAIN, WITHIN, DISJOINT, TOUCH...
    PixelFormat,        # BIT1, BIT4, BIT8, BIT16, SINGLE, DOUBLE, RGB, RGBA...
    ColorGradientType,  # 色带类型（BLACKTOWHITE, GREENTOWHITE...）
)
```

---

## 15. 完整工作流示例

### 示例：批量处理 Shapefile → 缓冲区 → 导出

```python
import os
import iobjectspy as spy
from iobjectspy import DatasourceConnectionInfo, EngineType

# 初始化
spy.set_iobjects_java_path(r"D:\software\supermap-idesktopx-2025-windows-x64-bin\bin")

# 打开/创建数据源
in_ds = spy.open_datasource(r"D:\data\input.udb")
out_ds = spy.open_datasource(r"D:\data\output.udb")

# 遍历所有面数据集，做5km缓冲区
for name in in_ds.dataset_names:
    dv = in_ds[name]
    if dv.type.name == 'REGION':
        buffer_name = name + "_Buffer5km"
        spy.create_buffer(
            source_dataset=dv,
            left_distance=5000,
            out_datasource=out_ds,
            out_dataset=buffer_name
        )
        # 导出为 Shapefile
        spy.export_to_shape(out_ds[buffer_name],
                             fr"D:\data\output\{buffer_name}.shp")
        print(f"✓ 完成：{buffer_name}")

spy.close_datasource(in_ds)
spy.close_datasource(out_ds)
print("全部处理完成！")
```

### 示例：DEM → 坡度坡向分析

```python
import iobjectspy as spy

spy.set_iobjects_java_path(r"D:\software\supermap-idesktopx-2025-windows-x64-bin\bin")

ds = spy.open_datasource(r"D:\data\terrain.udb")
dem = ds["DEM"]

# 坡度
spy.calculate_slope(dem, out_ds=ds, out_name="Slope", z_factor=1.0)

# 坡向
spy.calculate_aspect(dem, out_ds=ds, out_name="Aspect")

# 导出结果
spy.export_to_tif(ds["Slope"], r"D:\output\slope.tif")
spy.export_to_tif(ds["Aspect"], r"D:\output\aspect.tif")

spy.close_datasource(ds)
print("坡度坡向分析完成！")
```
