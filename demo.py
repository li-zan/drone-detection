import os
import time
import cv2
from PIL import Image
import supervision as sv
import numpy as np
from draw import test_corner_boxes

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
from ultralytics.models import YOLO
from ultralytics.models import RTDETR
from drone_video_alarm import analysis_results

# ----------------路径设置----------------------------------
source_path = "video/test1.mp4"
weights_path = "weights/rt-1280.pt"
save_path = "runs"
tracker = "botsort.yaml"
det_img_path = "result.jpg"
save_directory = "runs/screenshot"  # 异常图片保存路径

# ----------------参数设置------------------------------------
# 设置报警时间间隔
alarm_clock = 30
# 设置人数变动阈值
person_increase_or_decrease = 10
# 帧计数
frame_count = 0
# 人数变动计数
person_change_count = 0
# 初始人数
num_person = 0

# -----------------初始化-------------------------------------
if not os.path.exists(save_directory):
    os.makedirs(save_directory)  # 如果目录不存在，则创建目录

# ------------------alarm报警模块:未戴安全帽--------------------------
def alarm(path, persons=0, helmets=0):
    """
    关于未戴安全帽的报警模块
    :param path: img，必须，某一帧的检测画面
    :param persons: int，非必须，某一帧检测到的人数
    :param helmets: int，非必须，某一帧检测到的头盔数
    """
    # 判断是否要预警(当前只能通过比较persons和helmets的数目来判断是否有人没戴安全帽,不能精准定位到是哪个人违规了)
    if persons > helmets:
        print("当前人数:", persons, ",当前头盔数:", helmets, ",检测到有人未戴头盔！")
        # 发出预警的相关函数
        # analysis_results("-1", "50", "anJiu1", path)
    else:
        print("当前人数:", persons, ",当前头盔数:", helmets, ",符合工地安全要求。")


# ------------------推理模块-----------------------------------

# 1. predict by yolo_model   ---------------   yolo模型预测(不包含追踪)
# model = YOLO(weights_path)
# model.predict(source_path)

# 2. predict by re-detr_model   ---------------   detr模型预测(不包含追踪)
# model = RTDETR(weights_path)
# model.predict(source=source_path, device=0)

# 3. track by yolo_model   ---------------   yolo模型预测+追踪
# start = time.time()
# model = YOLO(weights_path)
# results = model.track(
#     source=source_path,
#     stream=True,  # 流模式处理，防止因为因为堆积而内存溢出
#     # show=True,  # 实时推理演示
#     tracker=tracker,  # 默认tracker为botsort
#     save=True,
#     save_dir=save_path,
#     # vid_stride=2,  # 视频帧数的步长，即隔几帧检测跟踪一次
#     save_txt=True,  # 把结果以txt形式保存
#     save_conf=True,  # 保存置信度得分
#     save_crop=True,  # 保存剪裁的图像
#     conf=0.4,
#     iou=0.5,
#     device=0,
# )
#
# # result.names输出的class为：
# # {0: 'person', 1: 'helmet', 2: 'life jacket', 3: 'truck', 4: 'excavator', 、
# # 5: 'car crane', 6: 'crawler crane', 7: 'rotary drill rig', 8: 'concrete tanker', 9: 'flame', 10: 'smoke'}
# # 其中 0:person 和 1:helmet 是重点要处理的
#
# for r in results:
#     frame_count += 1
#
#     boxes = r.boxes  # Boxes object for bbox outputs
#     masks = r.masks  # Masks object for segment masks outputs
#     probs = r.probs  # Class probabilities for classification outputs
#     frame = r.orig_img
#
#     # 用 supervision 解析预测结果 supervision的from_ultralytics方法对yolo和rt-detr均适用
#     # 此外supervision可以划分区域，并检测区域内有没有目标，这个对于"工地重载车辆周围的安全性判断"有重要意义
#     detections = sv.Detections.from_ultralytics(r)
#     # 只保留人和头盔，也就是class_id=0或1
#     detections = detections[(detections.class_id == 0) | (detections.class_id == 1)]
#     # 解析追踪ID
#     if r.boxes.id is not None:
#         detections.tracker_id = r.boxes.id.cpu().numpy().astype(int)
#         # 获取每个目标的：追踪ID、类别名称、置信度
#         # 1) 类别ID，如第一帧中检测出17个值，对应类别分别为[0 0 0 0 0 0 1 1 1 1 0 1 1 0 0 1 1]
#         class_ids = detections.class_id
#         # 2) 置信度，表示某一帧中检测出来的目标的置信度
#         confidences = detections.confidence
#         # 3) 多目标追踪ID，如第一帧共检测粗了9个人+8个头盔，该数组就有17个元素1~17
#         tracker_ids = detections.tracker_id
#         # labels为目前帧所有被检测出来目标的 编号+类别名+置信度
#         # labels = ['#{} {} {:.1f}'.format(tracker_ids[i], model.names[class_ids[i]], confidences[i] * 100) for i in
#         #           range(len(class_ids))]
#
#         # 首先保存上一帧的人数
#         last_frame_persons = num_person
#         # 接下来对目前帧的person和helmet个数进行统计
#         num_person = np.sum(class_ids == 0)
#         num_helmet = np.sum(class_ids == 1)
#         # 统计变动人数
#         person_change_count += abs(last_frame_persons - num_person)
#         # 报警条件判断
#         # 1. 人数变化达到阈值,检测到未戴安全帽立即发出警报
#         if person_change_count >= person_increase_or_decrease:
#             person_change_count = 0
#             alarm(num_person, num_helmet)
#             frame_count = 0
#         # 2. 人数变化未达到阈值,但时间/检测帧数足够了,若检测到未戴安全帽也立即警报
#         elif frame_count >= alarm_clock:
#             alarm(num_person, num_helmet)
#             frame_count = 0
#
#     # else:
#     #     print("当前未检测到人。")
#
# end = time.time()
# print(end - start)

# 4. track by rt-detr_model   ---------------   detr模型预测+追踪
start = time.time()
model = RTDETR(weights_path)
results = model.track(
    source=source_path,
    stream=True,  # 流模式处理，防止因为因为堆积而内存溢出
    # show=True,  # 实时推理演示
    tracker=tracker,  # 默认tracker为botsort
    save=True,
    save_dir=save_path,
    # vid_stride=2,  # 视频帧数的步长，即隔几帧检测跟踪一次
    save_txt=True,  # 把结果以txt形式保存
    # save_conf=True,  # 保存置信度得分
    save_crop=True,  # 保存剪裁的图像
    conf=0.4,
    iou=0.5,
    device=0,
)

# result.names输出的class为：
# {0: 'person', 1: 'helmet', 2: 'life jacket', 3: 'truck', 4: 'excavator', 、
# 5: 'car crane', 6: 'crawler crane', 7: 'rotary drill rig', 8: 'concrete tanker', 9: 'flame', 10: 'smoke'}
# 其中 0:person 和 1:helmet 是重点要处理的

for r in results:
    frame_count += 1

    boxes = r.boxes  # Boxes object for bbox outputs
    if boxes.id is not None: print(boxes)
    masks = r.masks  # Masks object for segment masks outputs
    probs = r.probs  # Class probabilities for classification outputs
    # frame = r.orig_img

    # 得到某一帧的检测结果(转化为PIL图片)
    im_array = r.plot(conf=False, line_width=1, font_size=1.5)  # plot a BGR numpy array of predictions
    im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
    # im.show()  # show image
    # im.save(det_img_path)  # save image

    # 用 supervision 解析预测结果 supervision的from_ultralytics方法对yolo和rt-detr均适用
    # 此外supervision可以划分区域，并检测区域内有没有目标，这个对于"工地重载车辆周围的安全性判断"有重要意义
    detections = sv.Detections.from_ultralytics(r)
    # 只保留人和头盔，也就是class_id=0或1
    detections = detections[(detections.class_id == 0) | (detections.class_id == 1)]
    # 解析追踪ID
    if r.boxes.id is not None: print(boxes)
    if r.boxes.id is not None:  # boxes.id:盒子的轨道id(如果可以被跟踪算法检测的话就为True)。
        detections.tracker_id = r.boxes.id.cpu().numpy().astype(int)
        # 获取每个目标的：追踪ID、类别名称、置信度
        # 1) 类别ID，如第一帧中检测出17个值，对应类别分别为[0 0 0 0 0 0 1 1 1 1 0 1 1 0 0 1 1]
        class_ids = detections.class_id
        # 2) 置信度，表示某一帧中检测出来的目标的置信度
        confidences = detections.confidence
        # 3) 多目标追踪ID，如第一帧共检测粗了9个人+8个头盔，该数组就有17个元素1~17
        tracker_ids = detections.tracker_id
        # labels为目前帧所有被检测出来目标的 编号+类别名+置信度
        # labels = ['#{} {} {:.1f}'.format(tracker_ids[i], model.names[class_ids[i]], confidences[i] * 100) for i in
        #           range(len(class_ids))]

        # 首先保存上一帧的人数
        last_frame_persons = num_person
        # 接下来对目前帧的person和helmet个数进行统计
        num_person = np.sum(class_ids == 0)
        num_helmet = np.sum(class_ids == 1)
        # 统计变动人数
        person_change_count += abs(last_frame_persons - num_person)
        # 报警条件判断
        # 1. 人数变化达到阈值,检测到未戴安全帽立即发出警报
        if person_change_count >= person_increase_or_decrease:
            # ----------------------处理选框------------------------
            out_img = test_corner_boxes(r.orig_img, boxes.xywh, boxes.cls, boxes.id, l=20, is_transparent=True,
                                        draw_type=True, draw_corner=True)
            # 形成文件名
            filename = str(int(time.time())) + ".png"  # 使用当前时间的时间戳（无小数点）
            file_path = os.path.join(save_directory, filename)

            # 保存图像
            cv2.imwrite(file_path, out_img)  # OpenCV的方法来保存numpy数组格式的图像
            # -----------------------------------------------------
            person_change_count = 0
            alarm(det_img_path, num_person, num_helmet)
            frame_count = 0
        # 2. 人数变化未达到阈值,但时间/检测帧数足够了,若检测到未戴安全帽也立即警报
        elif frame_count >= alarm_clock:
            # ----------------------处理选框------------------------
            out_img = test_corner_boxes(r.orig_img, boxes.xywh, boxes.cls, boxes.id, l=20, is_transparent=True,
                                        draw_type=True, draw_corner=True)
            # 形成文件名
            filename = str(int(time.time())) + ".png"  # 使用当前时间的时间戳（无小数点）
            file_path = os.path.join(save_directory, filename)

            # 保存图像
            cv2.imwrite(file_path, out_img)  # OpenCV的方法来保存numpy数组格式的图像
            # -----------------------------------------------------
            person_change_count = 0
            alarm(det_img_path, num_person, num_helmet)
            frame_count = 0

    # else:
    #     print("当前未检测到人。")

end = time.time()
print(end - start)

# 同一帧检测到多个对象且可被跟踪的情况
# 其中要处理的是
"""
cls: tensor([0., 1., 0.])
id: tensor([10., 24., 35.])
xywh: tensor([[3090.2725,  785.7628,   77.8074,   82.7527],
        [3101.3730,  752.7925,   17.5583,   17.2458],
        [1131.0474, 1137.9807,   38.7959,   57.9015]])
"""

"""
ultralytics.engine.results.Boxes object with attributes:

cls: tensor([0., 1., 0.])
conf: tensor([0.7931, 0.6240, 0.5696])
data: tensor([[3.0514e+03, 7.4439e+02, 3.1292e+03, 8.2714e+02, 1.0000e+01, 7.9314e-01, 0.0000e+00],
        [3.0926e+03, 7.4417e+02, 3.1102e+03, 7.6142e+02, 2.4000e+01, 6.2397e-01, 1.0000e+00],
        [1.1116e+03, 1.1090e+03, 1.1504e+03, 1.1669e+03, 3.5000e+01, 5.6956e-01, 0.0000e+00]])
id: tensor([10., 24., 35.])
is_track: True
orig_shape: (2160, 3840)
shape: torch.Size([3, 7])
xywh: tensor([[3090.2725,  785.7628,   77.8074,   82.7527],
        [3101.3730,  752.7925,   17.5583,   17.2458],
        [1131.0474, 1137.9807,   38.7959,   57.9015]])
xywhn: tensor([[0.8048, 0.3638, 0.0203, 0.0383],
        [0.8076, 0.3485, 0.0046, 0.0080],
        [0.2945, 0.5268, 0.0101, 0.0268]])
xyxy: tensor([[3051.3687,  744.3865, 3129.1760,  827.1392],
        [3092.5938,  744.1696, 3110.1521,  761.4154],
        [1111.6494, 1109.0299, 1150.4453, 1166.9314]])
xyxyn: tensor([[0.7946, 0.3446, 0.8149, 0.3829],
        [0.8054, 0.3445, 0.8099, 0.3525],
        [0.2895, 0.5134, 0.2996, 0.5402]])
"""
