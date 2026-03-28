"""
SQL 属性查询工具 + 空间查询工具 - 补充 MCP 未覆盖的功能

功能: 执行 SQL 属性查询和空间查询,并返回/导出结果
依赖: iobjectspy, pandas (可选,用于导出 CSV)
"""

from typing import List, Dict, Any, Optional, Tuple
import iobjectspy as spy
from iobjectspy import (
    DatasourceConnectionInfo, EngineType,
    GeoPoint, GeoLine, GeoRegion, Point2D
)


def query_dataset(
    datasource_path: str,
    dataset_name: str,
    sql_filter: str,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    执行 SQL 查询并返回结果列表

    Args:
        datasource_path: UDBX/UDB 文件路径
        dataset_name: 数据集名称
        sql_filter: SQL WHERE 条件 (如 "Population > 1000000")
        limit: 最多返回的记录数 (None = 无限制)

    Returns:
        查询结果列表,每条记录为一个字典 {字段名: 值}

    Example:
        >>> results = query_dataset(
        ...     datasource_path="D:/data/world.udbx",
        ...     dataset_name="cities",
        ...     sql_filter="Population > 1000000 AND Continent = 'Asia'",
        ...     limit=10
        ... )
        >>> for record in results:
        ...     print(f"{record['Name']}: {record['Population']}")
    """
    # 打开数据源
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_path
    ds_conn.engine_type = EngineType.UDBX if datasource_path.endswith('.udbx') else EngineType.UDB
    ds = spy.open_datasource(ds_conn)

    # 获取数据集
    dataset = ds[dataset_name]

    # 执行查询
    rs = dataset.query(sql_filter)
    results = []

    # 遍历结果集
    rs.move_first()
    count = 0
    while not rs.is_EOF:
        if limit is not None and count >= limit:
            break

        row = {}
        for field in rs.field_infos:
            field_name = field.name
            field_value = rs.get_field_value(field_name)

            # 处理几何对象
            if hasattr(field_value, 'to_json'):
                row[field_name] = field_value.to_json()
            else:
                row[field_name] = field_value

        results.append(row)
        rs.move_next()
        count += 1

    rs.close()
    ds.close()

    return results


def query_and_export(
    datasource_path: str,
    dataset_name: str,
    sql_filter: str,
    export_path: Optional[str] = None,
    limit: Optional[int] = None,
    fields: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    执行 SQL 查询并导出结果

    Args:
        datasource_path: UDBX/UDB 文件路径
        dataset_name: 数据集名称
        sql_filter: SQL WHERE 条件
        export_path: 导出文件路径 (支持 .csv, .json, .txt)
                     如果为 None,则只返回结果不导出
        limit: 最多返回的记录数
        fields: 指定要导出的字段列表 (None = 全部字段)

    Returns:
        查询结果列表

    Example:
        >>> query_and_export(
        ...     datasource_path="D:/data/world.udbx",
        ...     dataset_name="cities",
        ...     sql_filter="Continent = 'Asia'",
        ...     export_path="D:/output/asia_cities.csv"
        ... )
    """
    # 执行查询
    results = query_dataset(datasource_path, dataset_name, sql_filter, limit)

    # 如果指定了字段,过滤结果
    if fields is not None:
        filtered_results = []
        for record in results:
            filtered_record = {f: record[f] for f in fields if f in record}
            filtered_results.append(filtered_record)
        results = filtered_results

    # 导出文件
    if export_path is not None:
        export_results(results, export_path)

    return results


def export_results(results: List[Dict[str, Any]], export_path: str):
    """
    将查询结果导出到文件

    Args:
        results: 查询结果列表
        export_path: 导出文件路径
    """
    import os

    ext = os.path.splitext(export_path)[1].lower()

    if ext == '.csv':
        export_to_csv(results, export_path)
    elif ext == '.json':
        export_to_json(results, export_path)
    elif ext == '.txt':
        export_to_txt(results, export_path)
    else:
        raise ValueError(f"不支持的导出格式: {ext}. 支持: .csv, .json, .txt")


def export_to_csv(results: List[Dict[str, Any]], export_path: str):
    """导出为 CSV (需要 pandas)"""
    try:
        import pandas as pd
        df = pd.DataFrame(results)
        df.to_csv(export_path, index=False, encoding='utf-8-sig')
        print(f"✅ 已导出 {len(results)} 条记录到 {export_path}")
    except ImportError:
        print("⚠️ 未安装 pandas,无法导出 CSV. 运行: pip install pandas")
        export_to_txt(results, export_path.replace('.csv', '.txt'))


def export_to_json(results: List[Dict[str, Any]], export_path: str):
    """导出为 JSON"""
    import json
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ 已导出 {len(results)} 条记录到 {export_path}")


def export_to_txt(results: List[Dict[str, Any]], export_path: str):
    """导出为文本"""
    with open(export_path, 'w', encoding='utf-8') as f:
        for record in results:
            line = "\t".join([str(v) for v in record.values()])
            f.write(line + "\n")
    print(f"✅ 已导出 {len(results)} 条记录到 {export_path}")


def get_field_info(datasource_path: str, dataset_name: str) -> List[Dict[str, Any]]:
    """
    获取数据集的字段信息

    Args:
        datasource_path: UDBX/UDB 文件路径
        dataset_name: 数据集名称

    Returns:
        字段信息列表,每个字段包含: name, type, length 等
    """
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_path
    ds_conn.engine_type = EngineType.UDBX if datasource_path.endswith('.udbx') else EngineType.UDB
    ds = spy.open_datasource(ds_conn)

    dataset = ds[dataset_name]

    field_infos = []
    for field in dataset.field_infos:
        field_infos.append({
            'name': field.name,
            'type': field.type.name,
            'length': field.length,
            'is_required': field.is_required
        })

    ds.close()
    return field_infos


def get_dataset_info(datasource_path: str, dataset_name: str) -> Dict[str, Any]:
    """
    获取数据集的详细信息

    Args:
        datasource_path: UDBX/UDB 文件路径
        dataset_name: 数据集名称

    Returns:
        数据集信息字典
    """
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_path
    ds_conn.engine_type = EngineType.UDBX if datasource_path.endswith('.udbx') else EngineType.UDB
    ds = spy.open_datasource(ds_conn)

    dataset = ds[dataset_name]

    info = {
        'name': dataset.name,
        'type': dataset.type.name,
        'record_count': dataset.record_count,
        'field_count': dataset.field_count,
        'bounds': {
            'min_x': dataset.bounds.min_x,
            'min_y': dataset.bounds.min_y,
            'max_x': dataset.bounds.max_x,
            'max_y': dataset.bounds.max_y
        }
    }

    ds.close()
    return info


# ============================================================================
# 空间查询功能 - 新增
# ============================================================================

def query_by_spatial_relation(
    datasource_path: str,
    dataset_name: str,
    target_dataset_name: str,
    relation: str = "intersect",
    export_path: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    空间关系查询 - 查找与目标数据集有特定空间关系的要素

    Args:
        datasource_path: UDBX/UDB 文件路径
        dataset_name: 待查询数据集名称
        target_dataset_name: 目标数据集名称 (用于空间关系判断)
        relation: 空间关系类型,支持:
            - "intersect": 相交
            - "contain": 包含
            - "within": 在内部
            - "touch": 相接
            - "disjoint": 分离
            - "overlap": 重叠
            - "cross": 穿过
        export_path: 导出文件路径 (支持 .csv, .json, .txt)
        limit: 最多返回的记录数

    Returns:
        查询结果列表

    Example:
        >>> # 查找与道路相交的城市
        >>> results = query_by_spatial_relation(
        ...     datasource_path="D:/data/world.udbx",
        ...     dataset_name="cities",
        ...     target_dataset_name="roads",
        ...     relation="intersect"
        ... )
        >>> for record in results:
        ...     print(f"城市: {record['Name']}")
    """
    from iobjectspy import SpatialQueryMode

    # 打开数据源
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_path
    ds_conn.engine_type = EngineType.UDBX if datasource_path.endswith('.udbx') else EngineType.UDB
    ds = spy.open_datasource(ds_conn)

    # 获取数据集
    dataset = ds[dataset_name]
    target_dataset = ds[target_dataset_name]

    # 空间关系映射
    relation_map = {
        "intersect": SpatialQueryMode.INTERSECT,
        "contain": SpatialQueryMode.CONTAIN,
        "within": SpatialQueryMode.WITHIN,
        "touch": SpatialQueryMode.TOUCH,
        "disjoint": SpatialQueryMode.DISJOINT,
        "overlap": SpatialQueryMode.OVERLAP,
        "cross": SpatialQueryMode.CROSS
    }

    spatial_mode = relation_map.get(relation.lower(), SpatialQueryMode.INTERSECT)

    # 执行空间查询
    query_mode = spy.SpatialQueryMode(spatial_mode)
    
    # 创建空间查询对象
    query = spy.QueryParameter()
    query.spatial_query_mode = query_mode
    query.spatial_query_object = target_dataset

    # 执行查询
    rs = dataset.query(query)
    results = []

    # 遍历结果集
    rs.move_first()
    count = 0
    while not rs.is_EOF:
        if limit is not None and count >= limit:
            break

        row = {}
        for field in rs.field_infos:
            field_name = field.name
            field_value = rs.get_field_value(field_name)

            # 处理几何对象
            if hasattr(field_value, 'to_json'):
                row[field_name] = field_value.to_json()
            else:
                row[field_name] = field_value

        # 添加空间关系信息
        row["_spatial_relation"] = relation

        results.append(row)
        rs.move_next()
        count += 1

    rs.close()
    ds.close()

    # 导出文件
    if export_path is not None:
        export_results(results, export_path)

    return results


def query_nearest(
    datasource_path: str,
    dataset_name: str,
    point: Tuple[float, float],
    max_distance: Optional[float] = None,
    k: int = 5,
    export_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    最近邻查询 - 查找距离指定点最近的 k 个要素

    Args:
        datasource_path: UDBX/UDB 文件路径
        dataset_name: 数据集名称
        point: 查询点坐标 (x, y)
        max_distance: 最大搜索距离 (米),None = 无限制
        k: 返回的最近邻数量
        export_path: 导出文件路径 (支持 .csv, .json, .txt)

    Returns:
        查询结果列表,按距离升序排列

    Example:
        >>> # 查找距离指定点最近的 10 个城市
        >>> results = query_nearest(
        ...     datasource_path="D:/data/world.udbx",
        ...     dataset_name="cities",
        ...     point=(116.4, 39.9),  # 北京坐标
        ...     max_distance=100000,  # 100 公里内
        ...     k=10
        ... )
        >>> for i, record in enumerate(results):
        ...     print(f"{i+1}. {record['Name']} - 距离: {record['_distance']:.2f} 米")
    """
    # 打开数据源
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_path
    ds_conn.engine_type = EngineType.UDBX if datasource_path.endswith('.udbx') else EngineType.UDB
    ds = spy.open_datasource(ds_conn)

    # 获取数据集
    dataset = ds[dataset_name]

    # 创建查询点
    query_point = GeoPoint()
    query_point.set_x(point[0])
    query_point.set_y(point[1])

    # 执行最近邻查询
    # 注意: iObjectsPy 的最近邻查询需要使用距离查询
    # 这里使用简化的实现:先获取所有要素,计算距离,排序
    
    # 获取所有要素
    rs = dataset.query()
    
    # 计算每个要素到查询点的距离
    features = []
    rs.move_first()
    while not rs.is_EOF:
        geom = rs.get_geometry()
        if geom is not None:
            # 计算距离
            distance = geom.distance(query_point)
            
            # 检查最大距离
            if max_distance is None or distance <= max_distance:
                row = {}
                for field in rs.field_infos:
                    field_name = field.name
                    field_value = rs.get_field_value(field_name)
                    
                    if hasattr(field_value, 'to_json'):
                        row[field_name] = field_value.to_json()
                    else:
                        row[field_name] = field_value
                
                row["_distance"] = distance
                features.append(row)
        
        rs.move_next()
    
    rs.close()
    ds.close()
    
    # 按距离排序
    features.sort(key=lambda x: x["_distance"])
    
    # 返回前 k 个
    results = features[:k]
    
    # 导出文件
    if export_path is not None:
        export_results(results, export_path)
    
    return results


def query_by_distance(
    datasource_path: str,
    dataset_name: str,
    point: Tuple[float, float],
    distance: float,
    export_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    距离查询 - 查找距离指定点在指定距离范围内的所有要素

    Args:
        datasource_path: UDBX/UDB 文件路径
        dataset_name: 数据集名称
        point: 查询点坐标 (x, y)
        distance: 查询距离 (米)
        export_path: 导出文件路径 (支持 .csv, .json, .txt)

    Returns:
        查询结果列表

    Example:
        >>> # 查找距离北京 50 公里内的所有城市
        >>> results = query_by_distance(
        ...     datasource_path="D:/data/world.udbx",
        ...     dataset_name="cities",
        ...     point=(116.4, 39.9),
        ...     distance=50000  # 50 公里
        ... )
        >>> print(f"找到 {len(results)} 个城市")
    """
    # 使用 query_nearest,设置较大的 k 值
    results = query_nearest(
        datasource_path=datasource_path,
        dataset_name=dataset_name,
        point=point,
        max_distance=distance,
        k=999999,  # 足够大的值
        export_path=export_path
    )
    
    return results


def query_within_polygon(
    datasource_path: str,
    dataset_name: str,
    polygon_coords: List[Tuple[float, float]],
    export_path: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    多边形内查询 - 查找位于指定多边形内的所有要素

    Args:
        datasource_path: UDBX/UDB 文件路径
        dataset_name: 数据集名称
        polygon_coords: 多边形坐标列表 [(x1, y1), (x2, y2), ...]
        export_path: 导出文件路径 (支持 .csv, .json, .txt)
        limit: 最多返回的记录数

    Returns:
        查询结果列表

    Example:
        >>> # 查找北京市内的所有 POI
        >>> beijing_coords = [
        ...     (116.3, 39.9), (116.5, 39.9),
        ...     (116.5, 40.0), (116.3, 40.0)
        ... ]
        >>> results = query_within_polygon(
        ...     datasource_path="D:/data/pois.udbx",
        ...     dataset_name="poi",
        ...     polygon_coords=beijing_coords
        ... )
    """
    # 打开数据源
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_path
    ds_conn.engine_type = EngineType.UDBX if datasource_path.endswith('.udbx') else EngineType.UDB
    ds = spy.open_datasource(ds_conn)

    # 获取数据集
    dataset = ds[dataset_name]

    # 创建多边形几何
    polygon = GeoRegion()
    for i, (x, y) in enumerate(polygon_coords):
        point = Point2D()
        point.set_x(x)
        point.set_y(y)
        if i == 0:
            polygon.add_point(point)
        else:
            polygon.add_point(point)

    # 执行空间查询 (within)
    query = spy.QueryParameter()
    query.spatial_query_mode = spy.SpatialQueryMode.WITHIN
    query.spatial_query_object = polygon

    rs = dataset.query(query)
    results = []

    # 遍历结果集
    rs.move_first()
    count = 0
    while not rs.is_EOF:
        if limit is not None and count >= limit:
            break

        row = {}
        for field in rs.field_infos:
            field_name = field.name
            field_value = rs.get_field_value(field_name)

            if hasattr(field_value, 'to_json'):
                row[field_name] = field_value.to_json()
            else:
                row[field_name] = field_value

        row["_query_polygon"] = polygon_coords
        results.append(row)
        rs.move_next()
        count += 1

    rs.close()
    ds.close()

    # 导出文件
    if export_path is not None:
        export_results(results, export_path)

    return results


def query_along_path(
    datasource_path: str,
    dataset_name: str,
    path_dataset_name: str,
    buffer_distance: float,
    export_path: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    沿路径查询 - 查找距离指定路径缓冲区内的所有要素

    Args:
        datasource_path: UDBX/UDB 文件路径
        dataset_name: 待查询数据集名称
        path_dataset_name: 路径数据集名称 (线数据集)
        buffer_distance: 缓冲距离 (米)
        export_path: 导出文件路径 (支持 .csv, .json, .txt)
        limit: 最多返回的记录数

    Returns:
        查询结果列表

    Example:
        >>> # 查找道路两侧 500 米内的所有建筑
        >>> results = query_along_path(
        ...     datasource_path="D:/data/city.udbx",
        ...     dataset_name="buildings",
        ...     path_dataset_name="main_road",
        ...     buffer_distance=500
        ... )
    """
    # 打开数据源
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_path
    ds_conn.engine_type = EngineType.UDBX if datasource_path.endswith('.udbx') else EngineType.UDB
    ds = spy.open_datasource(ds_conn)

    # 获取数据集
    dataset = ds[dataset_name]
    path_dataset = ds[path_dataset_name]

    # 创建路径缓冲区
    # 先合并所有路径要素为一个多边形
    # 这里简化处理:使用 MCP 的缓冲区工具会更好
    # 现在的实现:遍历路径要素,创建缓冲区,查询
    
    results = []
    path_rs = path_dataset.query()
    path_rs.move_first()
    
    while not path_rs.is_EOF:
        path_geom = path_rs.get_geometry()
        
        if path_geom is not None:
            # 创建缓冲区
            buffer_geom = path_geom.buffer(buffer_distance)
            
            # 查询与缓冲区相交的要素
            query = spy.QueryParameter()
            query.spatial_query_mode = spy.SpatialQueryMode.INTERSECT
            query.spatial_query_object = buffer_geom
            
            rs = dataset.query(query)
            rs.move_first()
            
            while not rs.is_EOF:
                if limit is not None and len(results) >= limit:
                    break
                
                # 检查是否已经添加过 (避免重复)
                fid = rs.get_id()
                if not any(r.get("_feature_id") == fid for r in results):
                    row = {}
                    for field in rs.field_infos:
                        field_name = field.name
                        field_value = rs.get_field_value(field_name)
                        
                        if hasattr(field_value, 'to_json'):
                            row[field_name] = field_value.to_json()
                        else:
                            row[field_name] = field_value
                    
                    row["_feature_id"] = fid
                    row["_path_feature_id"] = path_rs.get_id()
                    row["_buffer_distance"] = buffer_distance
                    
                    results.append(row)
                
                rs.move_next()
            
            rs.close()
        
        path_rs.move_next()
    
    path_rs.close()
    ds.close()

    # 导出文件
    if export_path is not None:
        export_results(results, export_path)

    return results


# ============================================================================
# 示例代码
# ============================================================================

if __name__ == "__main__":
    # 示例用法
    print("SQL 查询 + 空间查询工具示例")
    print("=" * 50)

    # 获取数据集信息
    info = get_dataset_info(
        datasource_path="D:/data/world.udbx",
        dataset_name="cities"
    )
    print(f"\n数据集: {info['name']}")
    print(f"类型: {info['type']}")
    print(f"记录数: {info['record_count']}")
    print(f"字段数: {info['field_count']}")

    # SQL 查询示例
    print("\nSQL 查询示例:")
    results = query_and_export(
        datasource_path="D:/data/world.udbx",
        dataset_name="cities",
        sql_filter="Population > 1000000",
        limit=5,
        export_path="D:/output/large_cities.csv"
    )

    for record in results:
        print(f"  {record.get('Name', 'N/A')}: {record.get('Population', 0):,}")

    # 空间查询示例
    print("\n空间查询示例 (最近邻):")
    nearest_results = query_nearest(
        datasource_path="D:/data/world.udbx",
        dataset_name="cities",
        point=(116.4, 39.9),  # 北京坐标
        max_distance=100000,  # 100 公里内
        k=5
    )

    for i, record in enumerate(nearest_results):
        print(f"  {i+1}. {record.get('Name', 'N/A')} - 距离: {record['_distance']:.2f} 米")
