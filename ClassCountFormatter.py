import numpy as np

def generate_detailed_statistics_string(class_ids):
    # 定义类别对应的中文名
    class_names = {
        0: '人',
        1: '头盔',
        2: '救生衣',
        3: '重型卡车',
        4: '挖掘机',
        5: '汽车吊机',
        6: '履带吊机',
        7: '旋挖钻机',
        8: '水泥车',
        9: '火焰',
        10: '烟雾'
    }

    # 统计每个类别的数量
    counts = {class_name: np.sum(class_ids == class_id) for class_id, class_name in class_names.items()}

    # 移除数量为0的类别,忽略‘火焰’和'烟雾'类别
    counts = {class_name: count for class_name, count in counts.items() if count > 0 and class_name not in ['火焰', '烟雾']}

    # 创建统计字符串，格式为 "\"类别:数量\""
    statistics_lines = ['"' + f'{class_name}:{count}' + '"' for class_name, count in counts.items()]

    # 将所有统计字符串连接成一行，以逗号和换行符分隔
    statistics_string = "当前帧统计结果如下:\n" + ",\n".join(statistics_lines)
    # print(statistics_string)

    return statistics_string

def generate_detailed_vehicle_statistics_string(class_ids):
    # 定义类别对应的中文名
    class_names = {
        0: '人',
        1: '头盔',
        2: '救生衣',
        3: '重型卡车',
        4: '挖掘机',
        5: '汽车吊机',
        6: '履带吊机',
        7: '旋挖钻机',
        8: '水泥车',
        9: '火焰',
        10: '烟雾'
    }

    # 统计每个类别的数量
    counts = {class_name: np.sum(class_ids == class_id) for class_id, class_name in class_names.items()}

    # 移除数量为0的类别,忽略‘火焰’和'烟雾'类别
    counts = {class_name: count for class_name, count in counts.items() if count > 0 and class_name not in ['头盔', '救生衣', '火焰', '烟雾']}

    # 创建统计字符串，格式为 "\"类别:数量\""
    statistics_lines = ['"' + f'{class_name}:{count}' + '"' for class_name, count in counts.items()]

    # 将所有统计字符串连接成一行，以逗号和换行符分隔
    statistics_string = "当前识别结果如下:\n" + ",\n".join(statistics_lines)
    # print(statistics_string)

    return statistics_string

# 示例
# class_ids_example = np.array([0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 5, 5])
# print(generate_detailed_vehicle_statistics_string(class_ids_example))
