import os
import cv2
import sys
import numpy as np
import torch

from valid import find_people_without_helmets
import random
import math

from PIL import Image, ImageDraw, ImageFont


# ---------------------------角点美化---------------------------
def draw_box_corner(draw_img, bbox, length, corner_color):
    """
    角点美化
    :param draw_img: 输入图像
    :param bbox: 目标检测框 形式(x1,y1,x2,y2)
    :param length: 角点描绘的直线长度
    :param corner_color: 直线颜色
    """
    # Top Left
    cv2.line(draw_img, (bbox[0], bbox[1]), (bbox[0] + length, bbox[1]), corner_color, thickness=2)
    cv2.line(draw_img, (bbox[0], bbox[1]), (bbox[0], bbox[1] + length), corner_color, thickness=2)
    # Top Right
    cv2.line(draw_img, (bbox[2], bbox[1]), (bbox[2] - length, bbox[1]), corner_color, thickness=2)
    cv2.line(draw_img, (bbox[2], bbox[1]), (bbox[2], bbox[1] + length), corner_color, thickness=2)
    # Bottom Left
    cv2.line(draw_img, (bbox[0], bbox[3]), (bbox[0] + length, bbox[3]), corner_color, thickness=2)
    cv2.line(draw_img, (bbox[0], bbox[3]), (bbox[0], bbox[3] - length), corner_color, thickness=2)
    # Bottom Right
    cv2.line(draw_img, (bbox[2], bbox[3]), (bbox[2] - length, bbox[3]), corner_color, thickness=2)
    cv2.line(draw_img, (bbox[2], bbox[3]), (bbox[2], bbox[3] - length), corner_color, thickness=2)


# ---------------------------标签美化---------------------------
def draw_label_type(draw_img, bbox, cls, label_color):
    """
    标签美化
    :param draw_img: 输入图像
    :param bbox: 目标检测框 形式(x1,y1,x2,y2)
    :param cls: 标签类别
    :param label_color: 标签颜色
    """
    # class对应的类
    # all_cls = {0: '人', 1: '头盔', 2: '救生衣', 3: '重型卡车', 4: '挖掘机', 5: '汽车吊机',
    #            6: '履带吊机', 7: '旋挖钻机', 8: '水泥车', 9: '火焰', 10: '烟雾', 11: '未带安全帽！'}
    all_cls = {0: 'person', 1: 'helmet', 2: 'life jacket', 3: 'truck', 4: 'excavator', 5: 'car crane',
               6: 'crawler crane', 7: 'rotary drill rig', 8: 'concrete tanker', 9: 'flame', 10: 'smoke',
               11: 'person without helmet'}
    label = all_cls[cls]  # 获取标签
    labelSize = cv2.getTextSize(label + '0', cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
    if bbox[1] - labelSize[1] - 3 < 0:
        cv2.rectangle(draw_img,
                      (bbox[0], bbox[1] + 2),
                      (bbox[0] + labelSize[0], bbox[1] + labelSize[1] + 3),
                      color=label_color,
                      thickness=-1
                      )
        cv2.putText(draw_img, label,
                    (bbox[0], bbox[1] + labelSize[1] + 3),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    thickness=1
                    )
        # draw_img = cv2ImgAddText(draw_img, label, bbox[0], bbox[1] + 2, (0, 0, 0), 15)
    else:
        cv2.rectangle(draw_img,
                      (bbox[0], bbox[1] - labelSize[1] - 3),
                      (bbox[0] + labelSize[0], bbox[1] - 3),
                      color=label_color,
                      thickness=-1
                      )
        cv2.putText(draw_img, label,
                    (bbox[0], bbox[1] - 3),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    thickness=1
                    )
        # draw_img = cv2ImgAddText(draw_img, label, bbox[0], bbox[1] - labelSize[1] - 3, (0, 0, 0), 15)

    return draw_img


# 单个的情况
def test_corner_box(img, bbox, cls, l=20, is_transparent=False, draw_type=False, draw_corner=False,
                    box_color=(255, 0, 255)):
    draw_img = img.copy()
    pt1 = (bbox[0], bbox[1])
    pt2 = (bbox[2], bbox[3])

    out_img = img
    if is_transparent:
        alpha = 0.8
        # alpha = 0.5
        cv2.rectangle(draw_img, pt1, pt2, color=box_color, thickness=-1)
        out_img = cv2.addWeighted(img, alpha, draw_img, 1 - alpha, 0)

    cv2.rectangle(out_img, pt1, pt2, color=box_color, thickness=2)

    if draw_type:
        draw_label_type(out_img, bbox, cls, label_color=box_color)
    if draw_corner:
        draw_box_corner(out_img, bbox, length=l, corner_color=(0, 255, 0))
    return out_img


# 多个bbox的情况
def test_corner_boxes(img, xywh, xyxy, cls, ids, l, is_transparent=False, draw_type=False,
                      draw_corner=False,
                      box_color=(255, 0, 255)):
    """
    处理异常帧的图像
    :param img: 原始图形
    :param xywh: 格式为左上角坐标和宽高(归一化后的结果)的盒子集，用于计算IOU 形式(x1,y1,width,height)
    :param xyxy: 目标检测框集左上角坐标和右下角坐标 形式(x1,y1,x2,y2)
    :param cls: 各个盒子的对应类
    :param ids: 各个盒子的id值
    :param l: 角点描绘的直线长度
    :param is_transparent: 透明效果与否
    :param draw_type: 标签美化与否
    :param draw_corner: 角点美化与否
    :param box_color: 未带安全帽的盒子颜色
    :return: 绘制完毕的图片
    """

    # 获取没带安全帽的人的id列表
    people_without_helmets = find_people_without_helmets(cls, ids, xywh)
    # print("未带安全帽的人id有：" , people_without_helmets)

    # 初始化颜色列表以分配给不同的类别
    # 创建一个颜色列表，其中每个颜色都是一个随机的RGB元组
    colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(9)]
    # print(colors)

    draw_img = img.copy()
    out_img = img.copy()  # 创建一个新的输出图像以绘制形状

    for i, box in enumerate(xyxy):
        class_id = int(cls[i])
        current_id = ids[i]

        # ------------只标注未带安全帽的人时------------
        if current_id not in people_without_helmets:  # 假设cls中0代表“person”
            continue
        # ----------------------------------------

        #  ----------坐标处理-----------
        # 左上角坐标向下取整
        x_left_top = math.floor(box[0])
        y_left_top = math.floor(box[1])

        # 右下角坐标向上取整
        x_right_bottom = math.ceil(box[2])
        y_right_bottom = math.ceil(box[3])
        #  --------------------------

        pt1 = (x_left_top, y_left_top)  # 左上角坐标
        pt2 = (x_right_bottom, y_right_bottom)  # 右下角坐标
        # print(pt1, pt2)

        # 如果当前框是人，且此人未佩戴安全帽，使用特殊颜色
        if class_id == 0 and current_id in people_without_helmets:  # 假设cls中0代表“person”
            current_box_color = box_color
            if is_transparent:
                class_id = 11
                alpha = 0.8
                cv2.rectangle(draw_img, pt1, pt2, color=current_box_color, thickness=-1)
                out_img = cv2.addWeighted(out_img, alpha, draw_img, 1 - alpha, 0)
                draw_img = out_img.copy()  # 为下一步操作更新draw_img
        else:
            # 为其他类别分配颜色
            current_box_color = colors[class_id]

        # 画出框
        cv2.rectangle(out_img, pt1, pt2, color=current_box_color, thickness=1)

        # 用新的边界框坐标替换原来的处理逻辑(分别为左上角坐标和右下角坐标)
        bbox_new = [x_left_top, y_left_top, x_right_bottom, y_right_bottom]
        # print(bbox_new)

        # 判断是否需要添加标签美化和角点美化
        if draw_type:
            # 实现标签的具体绘制
            draw_label_type(out_img, bbox_new, cls=class_id, label_color=current_box_color)
        if draw_corner:
            # 实现角点的具体绘制
            draw_box_corner(out_img, bbox_new, length=l, corner_color=(0, 255, 0))

        draw_img = out_img.copy()

    # # 左上角统计数目
    # out_img = statistics(out_img, cls)

    return out_img


# 左上角标注
# def statistics(img, cls):
#     labels = {0: '人',
#               1: '头盔',
#               2: '救生衣',
#               3: '重型卡车',
#               4: '挖掘机',
#               5: '汽车吊机',
#               6: '履带吊机',
#               7: '旋挖钻机',
#               8: '水泥车'}
#     left = 30
#     top = 30
#     stride = 50
#     right = 300
#     class_ids = cls.cpu().numpy().astype(int)
#     for i in range(9):
#         if np.sum(class_ids == i) != 0:
#             img = cv2ImgAddText(img, labels[i] + ":" + str(np.sum(class_ids == i)),
#                                 left, top, (255, 0, 0), 40)
#             top = top + stride
#     img = cv2.rectangle(img, (left - 10, 20), (right, top), color=(0, 255, 255), thickness=2)
#
#     return img


# cv2写中文
def cv2ImgAddText(img, text, left, top, textColor=(0, 0, 255), textSize=20):
    if isinstance(img, np.ndarray):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def test1():
    img_name = './pikachu.jpg'
    img = cv2.imread(img_name)
    box = [140, 16, 468, 390]
    box_color = (255, 0, 255)  # pink
    out_img = test_corner_box(img, box, cls=0, l=30, is_transparent=False, draw_type=False, draw_corner=False,
                              box_color=box_color)
    cv2.imshow("1", out_img)
    cv2.waitKey(0)


def test2():
    img_name = './pikachu.jpg'
    img = cv2.imread(img_name)
    box = [140, 16, 468, 390]
    box_color = (255, 0, 255)  # pink
    out_img = test_corner_box(img, box, cls=0, l=30, is_transparent=False, draw_type=True, draw_corner=False,
                              box_color=box_color)
    cv2.imshow("2", out_img)
    cv2.waitKey(0)


def test3():
    img_name = './pikachu.jpg'
    img = cv2.imread(img_name)
    box = [140, 16, 468, 390]
    box_color = (255, 0, 255)  # pink
    out_img = test_corner_box(img, box, cls=0, l=30, is_transparent=False, draw_type=True, draw_corner=True,
                              box_color=box_color)
    cv2.imshow("3", out_img)
    cv2.waitKey(0)


def test4():
    img_name = './pikachu.jpg'
    img = cv2.imread(img_name)
    box = [140, 16, 468, 390]
    box_color = (255, 0, 255)  # pink
    out_img = test_corner_box(img, box, cls=0, l=30, is_transparent=True, draw_type=True, draw_corner=True,
                              box_color=box_color)
    cv2.imshow("4", out_img)
    cv2.waitKey(0)


def test5():
    img1 = cv2.imread("./sample/src.jpg")
    img2 = cv2.imread("./sample/fill.jpg")
    alpha = 0.6
    out_img = cv2.addWeighted(img1, alpha, img2, 1 - alpha, 0)
    small_image = cv2.resize(out_img, (960, 600))
    cv2.imshow("5", small_image)
    cv2.waitKey(0)


def test6():
    img_name = 'result.jpg'
    img = cv2.imread(img_name)
    xywh = [[3090.2725, 785.7628, 77.8074, 82.7527],
            [3101.3730, 752.7925, 17.5583, 17.2458],
            [1131.0474, 1137.9807, 38.7959, 57.9015]]
    cls = [0., 1., 0.]
    ids = [10., 24., 35.]
    box_color = (255, 0, 255)  # pink
    out_img = test_corner_boxes(img, xywh, cls, ids, l=20, is_transparent=True, draw_type=True, draw_corner=True,
                                box_color=box_color)
    cv2.imshow("6", out_img)
    cv2.waitKey(0)


def test7():
    img_name = './pikachu.jpg'
    img = cv2.imread(img_name)
    xywh = [[140, 16, 328, 374]]
    cls = [0., ]
    ids = [10., ]
    box_color = (255, 0, 255)  # pink
    out_img = test_corner_boxes(img, xywh, cls, ids, l=20, is_transparent=True, draw_type=True, draw_corner=True,
                                box_color=box_color)
    cv2.imshow("6", out_img)
    cv2.waitKey(0)


def test8():
    img_name = './000011.jpg'
    img = cv2.imread(img_name)
    xywh = [[767, 430, 27, 41]]
    cls = [0., ]
    ids = [10., ]
    box_color = (255, 0, 255)  # pink
    out_img = test_corner_boxes(img, xywh, cls, ids, l=20, is_transparent=True, draw_type=True, draw_corner=True,
                                box_color=box_color)
    cv2.imshow("6", out_img)
    cv2.waitKey(0)


if __name__ == "__main__":
    # test1()
    # test2()
    # test3()
    # test4()
    # test5()
    # test6()
    # test7()
    test8()
