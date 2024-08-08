from ultralytics.utils import yaml_load
from ultralytics.cfg import cfg2dict
from cfg.IterableSimpleNamespace import IterableSimpleNamespace
from pathlib import Path
from typing import Union, Dict
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"

# 配置文件
CFG_DICT = yaml_load(CFG_PATH)


def handle_dict(d: Dict):
    for k, v in d.items():
        if isinstance(v, str) and (v.lower() == "none" or len(v.strip()) == 0):
            d[k] = None
        elif isinstance(v, dict):
            handle_dict(v)  # 递归处理嵌套字典


handle_dict(CFG_DICT)
CFG = IterableSimpleNamespace(**CFG_DICT)


def get_cfg(project_id: int, cfg: Union[str, Path, Dict, SimpleNamespace] = CFG, overrides: Dict = None):
    """
    从文件加载配置数据，并从overrides字典可选地进行覆盖。

    Args:
        project_id (int): 项目ID。合并指定项目配置项到全局配置项，并优先使用指定项目的配置项。
        cfg (str | Path | Dict | SimpleNamespace): 配置数据源。可以是文件路径、字典或 SimpleNamespace 对象。
        overrides (Dict | None): 包含要覆盖配置文件的字典。

    Returns:
        (SimpleNamespace): 包含合并配置参数的命名空间对象。

    Notes:
        - 如果同时提供 `cfg` 和 `overrides`，则 `overrides` 中的值将优先。
        - 函数对覆盖参数校验，保证覆盖参数必须是原配置文件支持配置项的子集。
    """
    cfg = cfg2dict(cfg)

    # 处理cfg空值("none","","  ")为None类型
    handle_dict(cfg)

    # 获取全局配置项
    global_cfg = cfg.copy()
    if 'custom' in global_cfg:
        del global_cfg['custom']

    # 获取项目自定义配置项
    custom_cfg = cfg.get('custom', {}).get(project_id, {})

    # 去除 自定义配置项 中 值为 None 的 k-v pair
    custom_cfg = {k: v for k, v in custom_cfg.items() if v is not None}

    # 合并配置项
    merged_cfg = {**global_cfg, **custom_cfg}  # 优先使用 自定义配置项

    # 合并覆盖
    if overrides:
        overrides = cfg2dict(overrides)
        check_dict_alignment(merged_cfg, overrides)
        merged_cfg = {**merged_cfg, **overrides}  # 合并 merged_cfg 和 overrides 字典（优先使用 overrides）

    return IterableSimpleNamespace(**merged_cfg)


def check_dict_alignment(base: Dict, custom: Dict):
    """
    该函数检查自定义配置列表和基础配置列表之间的任何不匹配键。如果发现任何不匹配键，
    函数将打印出基础列表中的相似配置项并退出程序。

    Args:
        custom (dict): 自定义配置选项的字典
        base (dict): 基础配置选项的字典
    """
    base_keys, custom_keys = (set(x.keys()) for x in (base, custom))
    mismatched = [k for k in custom_keys if k not in base_keys]
    if mismatched:
        from difflib import get_close_matches

        string = ""
        for x in mismatched:
            matches = get_close_matches(x, base_keys)  # 键列表
            matches = [f"{k}={base[k]}" if base.get(k) is not None else k for k in matches]
            match_str = f"相似的参数有: {matches}。" if matches else ""
            string += f"'{x}' 不是一个有效的配置参数。{match_str}\n"
        raise SyntaxError(string)


if __name__ == "__main__":
    # print(CFG)
    args = get_cfg(cfg=CFG, project_id=28)
    print(args)
