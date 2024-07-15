import numpy as np


def box_iou_xywh(box1, box2):
    """
    交并比计算
    :param box1: person选框
    :param box2: helmet选框
    :return: iou值
    """
    x1min, y1min = box1[0] - box1[2] / 2.0, box1[1] - box1[3] / 2.0
    x1max, y1max = box1[0] + box1[2] / 2.0, box1[1] + box1[3] / 2.0
    s1 = box1[2] * box1[3]

    x2min, y2min = box2[0] - box2[2] / 2.0, box2[1] - box2[3] / 2.0
    x2max, y2max = box2[0] + box2[2] / 2.0, box2[1] + box2[3] / 2.0
    s2 = box2[2] * box2[3]

    xmin = np.maximum(x1min, x2min)
    ymin = np.maximum(y1min, y2min)
    xmax = np.minimum(x1max, x2max)
    ymax = np.minimum(y1max, y2max)
    inter_h = np.maximum(ymax - ymin, 0.)
    inter_w = np.maximum(xmax - xmin, 0.)
    intersection = inter_h * inter_w

    union = s1 + s2 - intersection
    iou = intersection / union
    # if iou > 0 : print('IoU is {}'.format(iou))
    return iou


def find_people_without_helmets(cls, ids, xywh):
    # 首先，我们将人和头盔的边界框分开，同时保留对应的ids。
    person_boxes = []
    person_ids = []
    helmet_boxes = []

    for i in range(len(cls)):
        if cls[i] == 0:  # 假设cls中0代表“person”
            person_boxes.append(xywh[i])
            person_ids.append(ids[i])
        elif cls[i] == 1:  # 假设cls中1代表“helmet”
            helmet_boxes.append(xywh[i])

    # 存储没有戴安全帽的人的id
    no_helmet_ids = []

    # 针对每个人，我们检查他与每个头盔的IoU。如果所有的IoU都是0，那么他就没有戴头盔。
    for person_id, person_box in zip(person_ids, person_boxes):
        has_helmet = False
        for helmet_box in helmet_boxes:
            iou = box_iou_xywh(person_box, helmet_box)
            if iou > 0:
                has_helmet = True
                break  # 如果找到一个匹配的头盔，就不需要继续检查了

        # 如果经过所有头盔检查后，这个人没有头盔，则记录他的ID
        if not has_helmet:
            no_helmet_ids.append(person_id)

    return no_helmet_ids


if __name__ == "__main__":
    # 假设以下是您的输入数据
    cls = np.array([0, 1, 0])  # 示例数据，代表类别
    ids = np.array([10, 24, 35])  # 示例数据，代表每个对象的唯一ID
    xywh = np.array([[3090.2725, 785.7628, 77.8074, 82.7527],  # 示例数据，代表边界框
                     [3101.3730, 752.7925, 17.5583, 17.2458],
                     [1131.0474, 1137.9807, 38.7959, 57.9015]])

    # 执行函数，找到没有戴头盔的人的ID
    people_without_helmets = find_people_without_helmets(cls, ids, xywh)
    print("People not wearing helmets:", people_without_helmets)
