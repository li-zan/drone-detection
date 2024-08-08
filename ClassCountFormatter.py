import numpy as np


def generate_detailed_statistics_string(class_ids, args):
    # 定义类别对应的中文名
    class_names = args.class_names

    # 统计每个类别的数量
    counts = {class_name: np.sum(class_ids == class_id) for class_id, class_name in class_names.items()}

    # 移除数量为0的类别
    counts = {class_name: count for class_name, count in counts.items() if count > 0}

    # 创建统计字符串，格式为 "\"类别:数量\""
    statistics_lines = ['"' + f'{class_name}:{count}' + '"' for class_name, count in counts.items()]

    # 将所有统计字符串连接成一行，以逗号和换行符分隔
    statistics_string = "当前帧统计结果如下:\n" + ",\n".join(statistics_lines)
    # print(statistics_string)

    return statistics_string


def generate_detailed_vehicle_statistics_string(class_ids, args):
    # 定义类别对应的中文名
    class_names = args.person_vehicle_names

    # 统计每个类别的数量
    counts = {class_name: np.sum(class_ids == class_id) for class_id, class_name in class_names.items()}

    # 移除数量为0的类别
    counts = {class_name: count for class_name, count in counts.items() if count > 0}

    # 创建统计字符串，格式为 "\"类别:数量\""
    statistics_lines = ['"' + f'{class_name}:{count}' + '"' for class_name, count in counts.items()]

    # 将所有统计字符串连接成一行，以逗号和换行符分隔
    statistics_string = "当前识别结果如下:\n" + ",\n".join(statistics_lines)
    # print(statistics_string)

    return statistics_string

# 示例
# class_ids_example = np.array([0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 5, 5])
# print(generate_detailed_vehicle_statistics_string(class_ids_example))
