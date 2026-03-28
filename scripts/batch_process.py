"""
批量处理工具 - 使用 MCP 工具的批处理包装

功能: 批量导入/导出数据,支持递归目录和多文件格式
依赖: iobjectspy, 可选 MCP 工具调用
"""

import os
import glob
from typing import List, Optional, Dict, Any
import iobjectspy as spy
from iobjectspy import DatasourceConnectionInfo, EngineType


def batch_import(
    source_dir: str,
    datasource_name: str,
    pattern: str = "*",
    recursive: bool = False,
    overwrite: bool = False,
    create_datasource: bool = True,
    dataset_prefix: str = ""
) -> Dict[str, Any]:
    """
    批量导入文件到 UDBX 数据源

    Args:
        source_dir: 源文件目录
        datasource_name: UDBX 数据源名称 (如 "output.udbx")
        pattern: 文件匹配模式 (如 "*.shp", "*.geojson", "*.csv")
        recursive: 是否递归子目录
        overwrite: 是否覆盖已存在的数据集
        create_datasource: 如果数据源不存在,是否创建
        dataset_prefix: 数据集名称前缀 (如 "imported_")

    Returns:
        统计信息字典 {
            'success_count': 成功导入数量,
            'failed_count': 失败数量,
            'failed_files': 失败文件列表,
            'total_size': 总大小 (字节)
        }

    Example:
        >>> batch_import(
        ...     source_dir="D:/data/input",
        ...     datasource_name="output.udbx",
        ...     pattern="*.shp",
        ...     recursive=True
        ... )
    """
    # 查找文件
    if recursive:
        files = glob.glob(os.path.join(source_dir, "**", pattern), recursive=True)
    else:
        files = glob.glob(os.path.join(source_dir, pattern))

    print(f"📁 找到 {len(files)} 个文件匹配 '{pattern}'")

    # 创建数据源 (如果需要)
    datasource_path = datasource_name
    if not os.path.isabs(datasource_name):
        # 相对路径,放在 source_dir 的上级目录
        datasource_path = os.path.join(os.path.dirname(source_dir), datasource_name)

    if not os.path.exists(datasource_path) and create_datasource:
        ds = spy.create_datasource(
            connection_info=DatasourceConnectionInfo(
                server=datasource_path,
                engine_type=EngineType.UDBX
            )
        )
        ds.close()
        print(f"✅ 已创建数据源: {datasource_path}")

    # 打开数据源
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_path
    ds_conn.engine_type = EngineType.UDBX
    ds = spy.open_datasource(ds_conn)

    # 统计信息
    stats = {
        'success_count': 0,
        'failed_count': 0,
        'failed_files': [],
        'total_size': 0
    }

    # 批量导入
    for filepath in files:
        try:
            filename = os.path.basename(filepath)
            ext = os.path.splitext(filename)[1].lower()

            # 确定数据集名称
            dataset_name = dataset_prefix + os.path.splitext(filename)[0]

            # 检查是否已存在
            if dataset_name in ds and not overwrite:
                print(f"⏭️  跳过 (已存在): {filename}")
                continue

            # 根据文件扩展名选择导入方法
            if ext == '.shp':
                spy.import_shape(
                    file_path=filepath,
                    out_datasource=ds,
                    out_dataset_name=dataset_name
                )
            elif ext == '.geojson':
                spy.import_geojson(
                    file_path=filepath,
                    out_datasource=ds,
                    out_dataset_name=dataset_name
                )
            elif ext == '.csv':
                spy.import_csv(
                    file_path=filepath,
                    out_datasource=ds,
                    out_dataset_name=dataset_name
                )
            elif ext == '.tif' or ext == '.tiff':
                spy.import_tiff(
                    file_path=filepath,
                    out_datasource=ds,
                    out_dataset_name=dataset_name
                )
            elif ext == '.kml':
                spy.import_kml(
                    file_path=filepath,
                    out_datasource=ds,
                    out_dataset_name=dataset_name
                )
            elif ext == '.dwg' or ext == '.dxf':
                spy.import_dwg(
                    file_path=filepath,
                    out_datasource=ds,
                    out_dataset_name=dataset_name
                )
            else:
                print(f"⏭️  跳过 (不支持的格式): {filename}")
                continue

            stats['success_count'] += 1
            stats['total_size'] += os.path.getsize(filepath)
            print(f"✅ 导入成功: {filename} → {dataset_name}")

        except Exception as e:
            stats['failed_count'] += 1
            stats['failed_files'].append(filepath)
            print(f"❌ 导入失败: {filename} - {str(e)}")

    ds.close()

    # 打印统计信息
    print("\n" + "=" * 50)
    print(f"导入完成:")
    print(f"  成功: {stats['success_count']} 个")
    print(f"  失败: {stats['failed_count']} 个")
    print(f"  总大小: {stats['total_size'] / 1024 / 1024:.2f} MB")
    if stats['failed_files']:
        print(f"\n失败文件列表:")
        for f in stats['failed_files']:
            print(f"  - {f}")

    return stats


def batch_export(
    datasource_name: str,
    target_dir: str,
    format: str = "shapefile",
    pattern: str = "*",
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    批量导出数据集中的数据

    Args:
        datasource_name: UDBX 数据源名称
        target_dir: 目标目录
        format: 导出格式 (shapefile, geojson, tiff)
        pattern: 数据集名称匹配模式
        overwrite: 是否覆盖已存在的文件

    Returns:
        统计信息字典

    Example:
        >>> batch_export(
        ...     datasource_name="output.udbx",
        ...     target_dir="D:/output",
        ...     format="geojson",
        ...     pattern="buffer_*"
        ... )
    """
    # 创建目标目录
    os.makedirs(target_dir, exist_ok=True)

    # 打开数据源
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_name
    ds_conn.engine_type = EngineType.UDBX
    ds = spy.open_datasource(ds_conn)

    # 查找数据集
    import fnmatch
    datasets = [name for name in ds if fnmatch.fnmatch(name, pattern)]

    print(f"📁 找到 {len(datasets)} 个数据集匹配 '{pattern}'")

    # 统计信息
    stats = {
        'success_count': 0,
        'failed_count': 0,
        'failed_datasets': []
    }

    # 批量导出
    for dataset_name in datasets:
        try:
            dataset = ds[dataset_name]

            # 确定导出文件路径
            ext = f".{format}"
            target_path = os.path.join(target_dir, dataset_name + ext)

            # 检查是否已存在
            if os.path.exists(target_path) and not overwrite:
                print(f"⏭️  跳过 (文件已存在): {target_path}")
                continue

            # 根据格式选择导出方法
            if format == "shapefile":
                spy.export_to_shape(
                    source_data=dataset,
                    target_file_path=target_path
                )
            elif format == "geojson":
                spy.export_to_geojson(
                    source_data=dataset,
                    target_file_path=target_path
                )
            elif format == "tiff":
                spy.export_to_tiff(
                    source_data=dataset,
                    target_file_path=target_path
                )
            else:
                print(f"⏭️  跳过 (不支持的格式): {format}")
                continue

            stats['success_count'] += 1
            print(f"✅ 导出成功: {dataset_name} → {target_path}")

        except Exception as e:
            stats['failed_count'] += 1
            stats['failed_datasets'].append(dataset_name)
            print(f"❌ 导出失败: {dataset_name} - {str(e)}")

    ds.close()

    # 打印统计信息
    print("\n" + "=" * 50)
    print(f"导出完成:")
    print(f"  成功: {stats['success_count']} 个")
    print(f"  失败: {stats['failed_count']} 个")
    if stats['failed_datasets']:
        print(f"\n失败数据集列表:")
        for name in stats['failed_datasets']:
            print(f"  - {name}")

    return stats


def batch_process(
    source_dir: str,
    datasource_name: str,
    processing_function,
    pattern: str = "*.shp",
    recursive: bool = False
) -> List[Any]:
    """
    批量处理文件,对每个文件执行自定义处理函数

    Args:
        source_dir: 源文件目录
        datasource_name: UDBX 数据源名称
        processing_function: 处理函数,签名为 (dataset, datasource) -> result
        pattern: 文件匹配模式
        recursive: 是否递归子目录

    Returns:
        处理结果列表

    Example:
        >>> def my_processing(dataset, datasource):
        ...     # 执行缓冲区分析
        ...     result = spy.create_buffer(
        ...         source_dataset=dataset,
        ...         left_distance=1000,
        ...         out_datasource=datasource,
        ...         out_dataset=f"{dataset.name}_buffer"
        ...     )
        ...     return result
        >>>
        >>> results = batch_process(
        ...     source_dir="D:/data/input",
        ...     datasource_name="output.udbx",
        ...     processing_function=my_processing,
        ...     pattern="*.shp"
        ... )
    """
    # 先批量导入
    import_stats = batch_import(
        source_dir=source_dir,
        datasource_name=datasource_name,
        pattern=pattern,
        recursive=recursive
    )

    # 打开数据源
    ds_conn = DatasourceConnectionInfo()
    ds_conn.server = datasource_name
    ds_conn.engine_type = EngineType.UDBX
    ds = spy.open_datasource(ds_conn)

    # 查找新导入的数据集
    import fnmatch
    datasets = [name for name in ds if fnmatch.fnmatch(name, pattern)]

    # 批量处理
    results = []
    for dataset_name in datasets:
        try:
            dataset = ds[dataset_name]
            result = processing_function(dataset, ds)
            results.append(result)
            print(f"✅ 处理成功: {dataset_name}")
        except Exception as e:
            print(f"❌ 处理失败: {dataset_name} - {str(e)}")
            results.append(None)

    ds.close()
    return results


if __name__ == "__main__":
    # 示例用法
    print("批量处理工具示例")
    print("=" * 50)

    # 批量导入示例
    print("\n批量导入示例:")
    batch_import(
        source_dir="D:/data/input",
        datasource_name="output.udbx",
        pattern="*.shp",
        recursive=True
    )

    # 批量导出示例
    print("\n批量导出示例:")
    batch_export(
        datasource_name="output.udbx",
        target_dir="D:/output",
        format="geojson",
        pattern="buffer_*"
    )
