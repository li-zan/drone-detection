import torch

def generate_objects_location_string(xyxy, cls):
    """
    根据检测到的对象的边界框坐标和类别（张量格式），生成描述这些对象位置的字符串。

    参数:
    xyxy : torch.Tensor
        边界框坐标的二维张量，每行代表一个边界框的左上角和右下角坐标 (x1, y1, x2, y2)。
    cls : torch.Tensor
        每个边界框对应的类别ID的一维张量，类别ID范围从0到8。

    返回:
    str
        描述检测到的对象位置的字符串。每个类别的对象位置用中文名称表示，并按照 "(x_center, y_bottom)" 的格式输出。
        如果同一类别有多个对象，则它们的位置由逗号分隔。未检测到的类别不会出现在字符串中。

    示例:
        cls_example = torch.tensor([0., 1., 0.])
        xyxy_example = torch.tensor([[3051.3687, 744.3865, 3129.1760, 827.1392],
                                         [3092.5938, 744.1696, 3110.1521, 761.4154],
                                         [1111.6494, 1109.0299, 1150.4453, 1166.9314]])
        print(generate_objects_location_string(xyxy_example, cls_example))
        人：（3089.8，827.1）, （1131.0，1166.9） 头盔：（3101.4，761.4）
    """
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

    # 初始化存储每个类别坐标的字典
    coordinates = {class_name: [] for class_name in class_names.values()}

    # 计算每个盒子的中心点坐标，并将其添加到相应类别的列表中
    for box, class_id in zip(xyxy, cls):
        x_center = (box[0] + box[2]) / 2
        y_bottom = box[3]
        class_name = class_names[int(class_id)]
        coordinates[class_name].append(f"（{x_center:.1f},{y_bottom:.1f}）")

    # 创建最终的字符串，格式为 "类别：坐标1，坐标2 ..."
    result = []
    for class_name, coords in coordinates.items():
        if coords:
            result.append(f"{class_name}：{','.join(coords)}")

    return ' '.join(result)


# 示例
# cls_example = torch.tensor([0., 1., 0.])
# xyxy_example = torch.tensor([[3051.3687, 744.3865, 3129.1760, 827.1392],
#                              [3092.5938, 744.1696, 3110.1521, 761.4154],
#                              [1111.6494, 1109.0299, 1150.4453, 1166.9314]])
# print(generate_objects_location_string(xyxy_example, cls_example))

