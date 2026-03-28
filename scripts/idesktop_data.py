"""
SuperMap iObjectsPy 数据操作工具库
功能：封装常用的工作空间、数据源、数据集操作，提供简洁的高层 API
"""

from typing import Optional, List, Union, Dict, Any
import os


# ============ 工作空间操作 ============

def open_workspace(path: str):
    """
    打开工作空间文件
    
    Args:
        path: 工作空间路径（.smwu / .sxwu / .smw 等）
    
    Returns:
        Workspace 对象
    
    Example:
        ws = open_workspace(r"D:\\data\\MyProject.smwu")
    """
    import iobjectspy as spy
    from iobjectspy import Workspace, WorkspaceConnectionInfo, WorkspaceType
    
    ext = os.path.splitext(path)[1].lower()
    type_map = {
        '.smwu': WorkspaceType.SMWU,
        '.sxwu': WorkspaceType.SXWU,
        '.smw':  WorkspaceType.SMW,
        '.sxw':  WorkspaceType.SXW,
    }
    
    ws = Workspace()
    conn = WorkspaceConnectionInfo()
    conn.server = path
    conn.type = type_map.get(ext, WorkspaceType.SMWU)
    
    if not ws.open(conn):
        raise RuntimeError(f"无法打开工作空间：{path}")
    
    print(f"✓ 工作空间已打开: {path}")
    print(f"  数据源数量: {ws.datasources.count}")
    print(f"  地图数量: {len(spy.list_maps(ws))}")
    return ws


def open_datasource(path_or_alias: str, password: str = ""):
    """
    打开数据源（支持 UDB/UDBX/SDB 文件和数据库连接）
    
    Args:
        path_or_alias: 数据源路径（.udb/.udbx）或别名
        password: 数据源密码（可选）
    
    Returns:
        Datasource 对象
    
    Example:
        ds = open_datasource(r"D:\\data\\world.udb")
    """
    import iobjectspy as spy
    from iobjectspy import DatasourceConnectionInfo, EngineType
    
    # 如果是文件路径
    if os.path.sep in path_or_alias or ':' in path_or_alias:
        conn = DatasourceConnectionInfo()
        conn.server = path_or_alias
        ext = os.path.splitext(path_or_alias)[1].lower()
        conn.engine_type = EngineType.UDBX if ext == '.udbx' else EngineType.UDB
        if password:
            conn.password = password
        ds = spy.open_datasource(conn)
    else:
        ds = spy.get_datasource(path_or_alias)
    
    if ds is None:
        raise RuntimeError(f"无法打开数据源：{path_or_alias}")
    
    print(f"✓ 数据源已打开: {ds.alias}")
    print(f"  数据集列表: {ds.dataset_names[:10]}{'...' if len(ds.dataset_names) > 10 else ''}")
    return ds


def list_datasets(ds, dataset_type: str = None) -> List[str]:
    """
    列出数据源中的数据集
    
    Args:
        ds: Datasource 对象
        dataset_type: 过滤类型 ('vector'/'raster'/'grid'/'image'/'network' 等)
    
    Returns:
        数据集名称列表
    """
    from iobjectspy import DatasetType
    
    names = ds.dataset_names
    if dataset_type:
        type_map = {
            'vector': [DatasetType.POINT, DatasetType.LINE, DatasetType.REGION,
                       DatasetType.POINT3D, DatasetType.LINE3D, DatasetType.REGION3D],
            'raster': [DatasetType.GRID, DatasetType.IMAGE],
            'grid':   [DatasetType.GRID],
            'image':  [DatasetType.IMAGE],
            'network': [DatasetType.NETWORK, DatasetType.NETWORK3D],
        }
        allowed = type_map.get(dataset_type.lower(), [])
        names = [n for n in names if ds[n].type in allowed]
    
    return names


# ============ 数据导入导出 ============

def import_data(source_file: str, out_datasource,
                out_dataset: str = None,
                charset: str = 'UTF-8') -> bool:
    """
    智能导入数据文件（根据扩展名自动选择导入方式）
    
    Args:
        source_file: 源文件路径
        out_datasource: 目标数据源（Datasource对象或路径字符串）
        out_dataset: 输出数据集名（可选，默认用文件名）
        charset: 字符集
    
    Returns:
        是否成功
    
    Supported formats:
        .shp  → Shapefile
        .geojson / .json → GeoJSON
        .kml / .kmz → KML/KMZ
        .csv  → CSV
        .dwg / .dxf → CAD
        .tif / .tiff → GeoTIFF
        .img  → Erdas IMG
        .osm  → OpenStreetMap
        .gpkg → GeoPackage
    """
    import iobjectspy as spy
    
    ext = os.path.splitext(source_file)[1].lower()
    out_name = out_dataset or os.path.splitext(os.path.basename(source_file))[0]
    
    import_funcs = {
        '.shp':     lambda: spy.import_shape(source_file, out_datasource, out_name, import_charset=charset),
        '.geojson': lambda: spy.import_geojson(source_file, out_datasource, out_name),
        '.json':    lambda: spy.import_geojson(source_file, out_datasource, out_name),
        '.kml':     lambda: spy.import_kml(source_file, out_datasource, out_name),
        '.kmz':     lambda: spy.import_kmz(source_file, out_datasource, out_name),
        '.csv':     lambda: spy.import_csv(source_file, out_datasource, out_name),
        '.dwg':     lambda: spy.import_dwg(source_file, out_datasource),
        '.dxf':     lambda: spy.import_dxf(source_file, out_datasource),
        '.tif':     lambda: spy.import_tif(source_file, out_datasource, out_name),
        '.tiff':    lambda: spy.import_tif(source_file, out_datasource, out_name),
        '.img':     lambda: spy.import_img(source_file, out_datasource, out_name),
        '.osm':     lambda: spy.import_osm(source_file, out_datasource),
        '.gpkg':    lambda: spy.import_gpkg(source_file, out_datasource, out_name),
        '.mif':     lambda: spy.import_mif(source_file, out_datasource, out_name),
    }
    
    func = import_funcs.get(ext)
    if not func:
        raise ValueError(f"不支持的文件格式：{ext}\n支持格式：{list(import_funcs.keys())}")
    
    print(f"正在导入: {source_file} → {out_name}")
    result = func()
    success = result is not None
    print(f"{'✓' if success else '✗'} 导入{'成功' if success else '失败'}")
    return success


def export_data(dataset, out_file: str, charset: str = 'UTF-8') -> bool:
    """
    智能导出数据集（根据目标文件扩展名自动选择格式）
    
    Args:
        dataset: 数据集对象（DatasetVector 或 DatasetGrid/Image）
        out_file: 输出文件路径
        charset: 字符集
    
    Returns:
        是否成功
    """
    import iobjectspy as spy
    
    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
    ext = os.path.splitext(out_file)[1].lower()
    
    export_funcs = {
        '.shp':     lambda: spy.export_to_shape(dataset, out_file, export_charset=charset),
        '.geojson': lambda: spy.export_to_geojson(dataset, out_file),
        '.kml':     lambda: spy.export_to_kml(dataset, out_file),
        '.kmz':     lambda: spy.export_to_kmz(dataset, out_file),
        '.csv':     lambda: spy.export_to_csv(dataset, out_file),
        '.dwg':     lambda: spy.export_to_dwg(dataset, out_file),
        '.dxf':     lambda: spy.export_to_dxf(dataset, out_file),
        '.tif':     lambda: spy.export_to_tif(dataset, out_file),
        '.tiff':    lambda: spy.export_to_tif(dataset, out_file),
        '.png':     lambda: spy.export_to_png(dataset, out_file),
        '.jpg':     lambda: spy.export_to_jpg(dataset, out_file),
    }
    
    func = export_funcs.get(ext)
    if not func:
        raise ValueError(f"不支持的导出格式：{ext}")
    
    print(f"正在导出: {dataset.name} → {out_file}")
    result = func()
    success = result is not None and result != False
    print(f"{'✓' if success else '✗'} 导出{'成功' if success else '失败'}")
    return success


def batch_import(source_dir: str, out_datasource,
                 file_pattern: str = "*",
                 recursive: bool = False) -> Dict[str, bool]:
    """
    批量导入目录中的数据文件
    
    Args:
        source_dir: 源目录
        out_datasource: 目标数据源
        file_pattern: 文件名匹配模式（如 "*.shp"）
        recursive: 是否递归子目录
    
    Returns:
        {文件名: 是否成功} 字典
    """
    import glob
    
    supported_exts = {'.shp', '.geojson', '.json', '.kml', '.kmz', 
                      '.csv', '.tif', '.tiff', '.img', '.osm', '.gpkg'}
    
    pattern = os.path.join(source_dir, "**" if recursive else "", file_pattern)
    files = glob.glob(pattern, recursive=recursive)
    files = [f for f in files if os.path.splitext(f)[1].lower() in supported_exts]
    
    print(f"找到 {len(files)} 个文件待导入")
    results = {}
    for f in files:
        try:
            results[f] = import_data(f, out_datasource)
        except Exception as e:
            print(f"  ✗ {f}: {e}")
            results[f] = False
    
    success_count = sum(1 for v in results.values() if v)
    print(f"\n导入完成: {success_count}/{len(files)} 成功")
    return results


# ============ 空间分析 ============

def buffer_analysis(source_dataset, distance: float,
                    out_datasource, out_dataset: str,
                    unit: str = 'Meter',
                    dissolve: bool = False) -> Any:
    """
    缓冲区分析
    
    Args:
        source_dataset: 源数据集（对象或路径字符串）
        distance: 缓冲距离
        out_datasource: 输出数据源
        out_dataset: 输出数据集名
        unit: 单位（'Meter'/'Kilometer'/'Mile' 等）
        dissolve: 是否融合结果
    
    Returns:
        结果数据集
    """
    import iobjectspy as spy
    
    print(f"执行缓冲区分析: 距离={distance} {unit}")
    result = spy.create_buffer(
        source_dataset=source_dataset,
        left_distance=distance,
        right_distance=distance,
        out_datasource=out_datasource,
        out_dataset=out_dataset,
        unit=unit
    )
    
    if result and dissolve:
        dissolve_name = out_dataset + "_Dissolved"
        result = spy.dissolve(result, out_datasource=out_datasource, out_dataset=dissolve_name)
    
    print(f"✓ 缓冲区分析完成: {out_dataset}")
    return result


def overlay_analysis(source_dataset, operate_dataset,
                     mode: str, out_datasource,
                     out_dataset: str) -> Any:
    """
    叠加分析
    
    Args:
        source_dataset: 源数据集
        operate_dataset: 操作数据集
        mode: 叠加模式 ('intersect'/'union'/'erase'/'clip'/'identity'/'update'/'xor')
        out_datasource: 输出数据源
        out_dataset: 输出数据集名
    
    Returns:
        结果数据集
    """
    import iobjectspy as spy
    from iobjectspy import OverlayMode
    
    mode_map = {
        'intersect': OverlayMode.INTERSECT,
        'union':     OverlayMode.UNION,
        'erase':     OverlayMode.ERASE,
        'clip':      OverlayMode.CLIP,
        'identity':  OverlayMode.IDENTITY,
        'update':    OverlayMode.UPDATE,
        'xor':       OverlayMode.XOR,
    }
    
    overlay_mode = mode_map.get(mode.lower())
    if overlay_mode is None:
        raise ValueError(f"不支持的叠加模式: {mode}，可选: {list(mode_map.keys())}")
    
    print(f"执行叠加分析: 模式={mode}")
    result = spy.overlay(
        source_dataset=source_dataset,
        operate_dataset=operate_dataset,
        overlay_mode=overlay_mode,
        out_datasource=out_datasource,
        out_dataset=out_dataset
    )
    print(f"✓ 叠加分析完成: {out_dataset}")
    return result


def query_by_sql(dataset, sql_filter: str) -> Any:
    """
    SQL 属性查询
    
    Args:
        dataset: DatasetVector 对象
        sql_filter: SQL WHERE 子句（如 "Population > 1000000"）
    
    Returns:
        Recordset 对象（记得调用 rs.close()）
    
    Example:
        rs = query_by_sql(ds["Countries"], "GDP > 1e12")
        while not rs.is_EOF:
            print(rs.get_field_value("Name"))
            rs.move_next()
        rs.close()
    """
    rs = dataset.query(sql_filter)
    count = rs.record_count if rs else 0
    print(f"查询结果: {count} 条记录")
    return rs


def dataset_to_dataframe(dataset):
    """
    将矢量数据集转为 pandas DataFrame
    
    Args:
        dataset: DatasetVector 对象
    
    Returns:
        pandas DataFrame
    """
    import iobjectspy as spy
    df = spy.datasetvector_to_df(dataset)
    print(f"✓ 转换完成: {len(df)} 行 × {len(df.columns)} 列")
    return df


if __name__ == "__main__":
    # 使用示例
    print("iDesktop 数据工具库已加载")
    print("可用函数：")
    print("  open_workspace(path)           - 打开工作空间")
    print("  open_datasource(path)          - 打开数据源")
    print("  list_datasets(ds)              - 列出数据集")
    print("  import_data(file, ds)          - 导入数据")
    print("  export_data(dataset, file)     - 导出数据")
    print("  batch_import(dir, ds)          - 批量导入")
    print("  buffer_analysis(...)           - 缓冲区分析")
    print("  overlay_analysis(...)          - 叠加分析")
    print("  query_by_sql(dataset, sql)     - SQL查询")
    print("  dataset_to_dataframe(dataset)  - 转DataFrame")
