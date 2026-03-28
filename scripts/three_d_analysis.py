"""
SuperMap iDesktopX 三维分析工具库

提供常用的三维分析功能封装，简化 iObjectsPy API 调用。
适用于可视域分析、日照分析、淹没分析、填挖方计算等场景。

依赖:
- iObjectspy
- numpy
- matplotlib (可选，用于可视化)
"""

import iobjectspy as spy
from iobjectspy import Workspace, Point3D, GeoLine3D, GeoPolygon
from typing import List, Tuple, Dict, Optional
import datetime


class Scene3DAnalyzer:
    """三维场景分析器"""

    def __init__(self, workspace_path: str, scene_name: str):
        """
        初始化三维场景分析器

        Args:
            workspace_path: 工作空间文件路径 (.smwu)
            scene_name: 场景名称
        """
        self.ws = Workspace()
        self.ws.open(workspace_path)
        self.scene = spy.get_scene(self.ws, scene_name)
        print(f"✓ 已打开场景: {scene_name}")


class VisibilityAnalyzer:
    """可视域与通视分析器"""

    def __init__(self, scene):
        self.scene = scene

    def visibility_analysis(
        self,
        observer_point: Tuple[float, float, float],
        horizontal_angle: float = 360,
        vertical_angle: float = 60,
        max_distance: float = 2000,
        min_distance: float = 0,
        output_datasource_path: Optional[str] = None,
        output_dataset_name: Optional[str] = None
    ) -> Dict:
        """
        可视域分析

        Args:
            observer_point: 观察点坐标 (X, Y, Z)
            horizontal_angle: 水平视角范围（度）0-360
            vertical_angle: 垂直视角范围（度）0-90
            max_distance: 最大视距（米）
            min_distance: 最小视距（米）
            output_datasource_path: 输出数据源路径（可选）
            output_dataset_name: 输出数据集名称（可选）

        Returns:
            分析结果字典,包含可视面积、可见比例等统计信息
        """
        point = Point3D(*observer_point)

        result = spy.visibility_analysis(
            scene=self.scene,
            observer_point=point,
            horizontal_angle=horizontal_angle,
            vertical_angle=vertical_angle,
            max_distance=max_distance,
            min_distance=min_distance,
            out_datasource=output_datasource_path,
            out_dataset=output_dataset_name
        )

        print(f"✓ 可视域分析完成")
        print(f"  观察点: {observer_point}")
        print(f"  水平视角: {horizontal_angle}°, 垂直视角: {vertical_angle}°")
        print(f"  最大视距: {max_distance} 米")

        return {
            "observer_point": observer_point,
            "horizontal_angle": horizontal_angle,
            "vertical_angle": vertical_angle,
            "max_distance": max_distance,
            "result_dataset": output_dataset_name
        }

    def line_of_sight(
        self,
        start_point: Tuple[float, float, float],
        end_point: Tuple[float, float, float],
        output_datasource_path: Optional[str] = None,
        output_dataset_name: Optional[str] = None
    ) -> Dict:
        """
        通视分析

        Args:
            start_point: 起点坐标 (X, Y, Z)
            end_point: 终点坐标 (X, Y, Z)
            output_datasource_path: 输出数据源路径（可选）
            output_dataset_name: 输出数据集名称（可选）

        Returns:
            分析结果字典,包含是否通视、障碍点等信息
        """
        start = Point3D(*start_point)
        end = Point3D(*end_point)

        result = spy.line_of_sight(
            scene=self.scene,
            start_point=start,
            end_point=end,
            out_datasource=output_datasource_path,
            out_dataset=output_dataset_name
        )

        print(f"✓ 通视分析完成")
        print(f"  起点: {start_point}")
        print(f"  终点: {end_point}")
        print(f"  通视: {'是' if result.visible else '否'}")

        return {
            "start_point": start_point,
            "end_point": end_point,
            "visible": result.visible,
            "obstruction_point": result.obstruction_point,
            "obstacle_type": result.obstacle_type
        }

    def dynamic_visibility_analysis(
        self,
        waypoints: List[Tuple[float, float, float]],
        horizontal_angle: float = 360,
        vertical_angle: float = 60,
        max_distance: float = 2000,
        sample_interval: float = 100,
        output_datasource_path: Optional[str] = None,
        output_dataset_prefix: Optional[str] = None
    ) -> Dict:
        """
        动态可视域分析（沿路径）

        Args:
            waypoints: 路径关键点列表 [(X, Y, Z), ...]
            horizontal_angle: 水平视角范围（度）
            vertical_angle: 垂直视角范围（度）
            max_distance: 最大视距（米）
            sample_interval: 采样间隔（米）
            output_datasource_path: 输出数据源路径（可选）
            output_dataset_prefix: 输出数据集前缀（可选）

        Returns:
            分析结果字典
        """
        path = GeoLine3D.make(waypoints)

        result = spy.dynamic_visibility_analysis(
            scene=self.scene,
            path=path,
            horizontal_angle=horizontal_angle,
            vertical_angle=vertical_angle,
            max_distance=max_distance,
            sample_interval=sample_interval,
            out_datasource=output_datasource_path,
            out_dataset_prefix=output_dataset_prefix
        )

        print(f"✓ 动态可视域分析完成")
        print(f"  路径点数: {len(waypoints)}")
        print(f"  采样间隔: {sample_interval} 米")
        print(f"  最大视距: {max_distance} 米")

        return {
            "waypoints": waypoints,
            "horizontal_angle": horizontal_angle,
            "vertical_angle": vertical_angle,
            "max_distance": max_distance,
            "sample_interval": sample_interval,
            "result_prefix": output_dataset_prefix
        }


class FloodAnalyzer:
    """淹没分析器"""

    def __init__(self, dem_dataset, workspace):
        self.dem = dem_dataset
        self.ws = workspace

    def flood_simulation(
        self,
        water_levels: List[float],
        min_water_level: float,
        max_water_level: float,
        rise_speed: float = 1.0,
        region: Optional[GeoPolygon] = None,
        output_datasource_path: Optional[str] = None,
        output_dataset_prefix: Optional[str] = None
    ) -> Dict:
        """
        洪水淹没模拟

        Args:
            water_levels: 关键水位点列表（米）
            min_water_level: 最低淹没水位（米）
            max_water_level: 最高淹没水位（米）
            rise_speed: 水位上涨速度（米/秒）
            region: 分析区域（可选）
            output_datasource_path: 输出数据源路径（可选）
            output_dataset_prefix: 输出数据集前缀（可选）

        Returns:
            淹没分析结果字典
        """
        result = spy.flood_analysis(
            dem=self.dem,
            water_levels=water_levels,
            min_water_level=min_water_level,
            max_water_level=max_water_level,
            rise_speed=rise_speed,
            region=region,
            out_datasource=output_datasource_path,
            out_dataset_prefix=output_dataset_prefix
        )

        print(f"✓ 淹没分析完成")
        print(f"  水位范围: {min_water_level} - {max_water_level} 米")
        print(f"  关键水位点: {len(water_levels)} 个")
        print(f"  上涨速度: {rise_speed} 米/秒")

        return {
            "water_levels": water_levels,
            "min_water_level": min_water_level,
            "max_water_level": max_water_level,
            "rise_speed": rise_speed,
            "result_prefix": output_dataset_prefix
        }


class SunlightAnalyzer:
    """日照分析器"""

    def __init__(self, scene, latitude: float, longitude: float, timezone: int = 8):
        self.scene = scene
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone

    def analyze(
        self,
        buildings_dataset,
        analysis_date: str,
        start_time: str = "8:00",
        end_time: str = "18:00",
        time_interval: int = 30,
        output_datasource_path: Optional[str] = None,
        output_dataset_name: Optional[str] = None
    ) -> Dict:
        """
        日照分析

        Args:
            buildings_dataset: 建筑物三维面数据集
            analysis_date: 分析日期 (YYYY-MM-DD)
            start_time: 开始时间 (HH:MM)
            end_time: 结束时间 (HH:MM)
            time_interval: 时间步长（分钟）
            output_datasource_path: 输出数据源路径（可选）
            output_dataset_name: 输出数据集名称（可选）

        Returns:
            日照分析结果字典
        """
        result = spy.sunlight_analysis(
            scene=self.scene,
            buildings=buildings_dataset,
            latitude=self.latitude,
            longitude=self.longitude,
            timezone=self.timezone,
            analysis_date=analysis_date,
            start_time=start_time,
            end_time=end_time,
            time_interval=time_interval,
            out_datasource=output_datasource_path,
            out_dataset=output_dataset_name
        )

        print(f"✓ 日照分析完成")
        print(f"  分析日期: {analysis_date}")
        print(f"  时间范围: {start_time} - {end_time}")
        print(f"  采样间隔: {time_interval} 分钟")

        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "analysis_date": analysis_date,
            "start_time": start_time,
            "end_time": end_time,
            "time_interval": time_interval,
            "result_dataset": output_dataset_name
        }


class TerrainAnalyzer:
    """地形分析器"""

    def __init__(self, dem_dataset):
        self.dem = dem_dataset

    def calculate_slope_aspect(
        self,
        slope_unit: str = "DEGREE",
        z_factor: float = 1.0,
        output_datasource_path: Optional[str] = None,
        slope_dataset_name: Optional[str] = None,
        aspect_dataset_name: Optional[str] = None
    ) -> Dict:
        """
        坡度坡向分析

        Args:
            slope_unit: 输出单位 (DEGREE 或 PERCENT)
            z_factor: 高程转换因子
            output_datasource_path: 输出数据源路径（可选）
            slope_dataset_name: 坡度数据集名称（可选）
            aspect_dataset_name: 坡向数据集名称（可选）

        Returns:
            分析结果字典
        """
        # 计算坡度
        slope_result = spy.calculate_slope(
            dem_dataset=self.dem,
            slope_unit=slope_unit,
            z_factor=z_factor,
            out_datasource=output_datasource_path,
            out_dataset=slope_dataset_name
        )

        # 计算坡向
        aspect_result = spy.calculate_aspect(
            dem_dataset=self.dem,
            out_datasource=output_datasource_path,
            out_dataset=aspect_dataset_name
        )

        print(f"✓ 坡度坡向分析完成")
        print(f"  坡度单位: {slope_unit}")
        print(f"  Z 因子: {z_factor}")

        return {
            "slope_unit": slope_unit,
            "z_factor": z_factor,
            "slope_dataset": slope_dataset_name,
            "aspect_dataset": aspect_dataset_name
        }

    def extract_contour(
        self,
        base_value: float = 0,
        interval: float = 10,
        smooth_method: str = "BSPLINE",
        smoothness: int = 3,
        output_datasource_path: Optional[str] = None,
        output_dataset_name: Optional[str] = None
    ) -> Dict:
        """
        等值线提取

        Args:
            base_value: 起始等值线值（米）
            interval: 等值线间距（米）
            smooth_method: 平滑方法 (BSPLINE 或 POLYLINE)
            smoothness: 平滑程度
            output_datasource_path: 输出数据源路径（可选）
            output_dataset_name: 输出数据集名称（可选）

        Returns:
            分析结果字典
        """
        result = spy.extract_contour(
            dem_dataset=self.dem,
            base_value=base_value,
            interval=interval,
            smooth_method=smooth_method,
            smoothness=smoothness,
            out_datasource=output_datasource_path,
            out_dataset=output_dataset_name
        )

        print(f"✓ 等值线提取完成")
        print(f"  起始值: {base_value} 米, 间距: {interval} 米")
        print(f"  平滑方法: {smooth_method}")

        return {
            "base_value": base_value,
            "interval": interval,
            "smooth_method": smooth_method,
            "smoothness": smoothness,
            "result_dataset": output_dataset_name
        }

    def terrain_profile(
        self,
        profile_line: GeoLine,
        sample_interval: float = 10,
        output_datasource_path: Optional[str] = None,
        output_dataset_name: Optional[str] = None
    ) -> Dict:
        """
        地形剖面分析

        Args:
            profile_line: 剖面线 (GeoLine)
            sample_interval: 采样间隔（米）
            output_datasource_path: 输出数据源路径（可选）
            output_dataset_name: 输出数据集名称（可选）

        Returns:
            剖面数据字典,包含距离和高程列表
        """
        result = spy.terrain_profile(
            scene=self.scene,
            profile_line=profile_line,
            sample_interval=sample_interval,
            out_datasource=output_datasource_path,
            out_dataset=output_dataset_name
        )

        print(f"✓ 地形剖面分析完成")
        print(f"  采样间隔: {sample_interval} 米")
        print(f"  剖面点数: {len(result.distances)}")

        return {
            "sample_interval": sample_interval,
            "distances": result.distances,
            "elevations": result.elevations,
            "result_dataset": output_dataset_name
        }


class EarthworkAnalyzer:
    """填挖方分析器"""

    def __init__(self, original_dem, modified_dem):
        self.dem_before = original_dem
        self.dem_after = modified_dem

    def calculate_cut_fill(
        self,
        region: Optional[GeoPolygon] = None,
        output_datasource_path: Optional[str] = None
    ) -> Dict:
        """
        填挖方计算

        Args:
            region: 分析区域（可选）
            output_datasource_path: 输出数据源路径（可选）

        Returns:
            土方计算结果字典,包含挖方体积、填方体积等
        """
        result = spy.cut_fill_analysis(
            original_dem=self.dem_before,
            modified_dem=self.dem_after,
            region=region,
            out_datasource=output_datasource_path
        )

        # 计算土方平衡
        net_volume = result.fill_volume - result.cut_volume

        print("=" * 50)
        print("填挖方计算结果")
        print("=" * 50)
        print(f"挖方体积: {result.cut_volume:,.2f} 立方米")
        print(f"填方体积: {result.fill_volume:,.2f} 立方米")
        print(f"挖方面积: {result.cut_area:,.2f} 平方米")
        print(f"填方面积: {result.fill_area:,.2f} 平方米")
        print("-" * 50)
        if abs(net_volume) < 100:
            print("✓ 土方平衡")
        else:
            action = "外运" if net_volume < 0 else "外购"
            print(f"✗ 土方不平衡,需要{action} {abs(net_volume):,.2f} 立方米")
        print("=" * 50)

        return {
            "cut_volume": result.cut_volume,
            "fill_volume": result.fill_volume,
            "cut_area": result.cut_area,
            "fill_area": result.fill_area,
            "net_volume": net_volume,
            "balanced": abs(net_volume) < 100
        }


# ========== 使用示例 ==========

if __name__ == "__main__":
    # 示例 1: 可视域分析
    def example_visibility_analysis():
        workspace_path = r"D:\data\project.smwu"
        scene_name = "Scene3D"

        # 初始化场景分析器
        analyzer = Scene3DAnalyzer(workspace_path, scene_name)

        # 创建可视域分析器
        vis_analyzer = VisibilityAnalyzer(analyzer.scene)

        # 执行可视域分析
        result = vis_analyzer.visibility_analysis(
            observer_point=(116.4, 39.9, 100),
            horizontal_angle=360,
            vertical_angle=60,
            max_distance=2000,
            output_dataset_name="Monitor_01_Visibility"
        )

    # 示例 2: 淹没分析
    def example_flood_analysis():
        # 打开数据源
        ds = spy.open_datasource(r"D:\data\project.udb")
        dem = ds["DEM"]

        # 创建淹没分析器
        flood_analyzer = FloodAnalyzer(dem, None)

        # 执行淹没模拟
        result = flood_analyzer.flood_simulation(
            water_levels=[50, 60, 70, 80, 90, 100],
            min_water_level=50,
            max_water_level=100,
            rise_speed=0.5,
            output_dataset_prefix="Flood_"
        )

    # 示例 3: 填挖方计算
    def example_cut_fill():
        ds = spy.open_datasource(r"D:\data\project.udb")
        dem_before = ds["DEM_Original"]
        dem_after = ds["DEM_Design"]

        earthwork = EarthworkAnalyzer(dem_before, dem_after)
        result = earthwork.calculate_cut_fill()

        print(f"挖方体积: {result['cut_volume']} 立方米")
        print(f"填方体积: {result['fill_volume']} 立方米")
        print(f"是否平衡: {result['balanced']}")

    # 示例 4: 日照分析
    def example_sunlight_analysis():
        workspace_path = r"D:\data\city.smwu"
        scene_name = "CityScene"

        analyzer = Scene3DAnalyzer(workspace_path, scene_name)
        ds = spy.open_datasource(r"D:\data\city.udb")
        buildings = ds["Buildings_3D"]

        sunlight_analyzer = SunlightAnalyzer(
            scene=analyzer.scene,
            latitude=39.9,
            longitude=116.4,
            timezone=8
        )

        # 冬至日日照分析（住宅日照标准）
        result = sunlight_analyzer.analyze(
            buildings_dataset=buildings,
            analysis_date="2025-12-22",  # 冬至
            start_time="8:00",
            end_time="16:00",
            time_interval=15,
            output_dataset_name="Sunlight_Solstice"
        )
