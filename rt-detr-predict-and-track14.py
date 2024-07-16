# track by rt-detr_model   ---------------   detr模型预测+追踪
import datetime
import os




from ClassCountFormatter import generate_detailed_statistics_string, generate_detailed_vehicle_statistics_string
from ObjectLocationFormatter import generate_objects_location_string
from get_UAV_status14 import get_UAV_status

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import time
import cv2
import ffmpeg
import time
import supervision as sv
import threading
import numpy as np
from alarm import cap_alarm
from ultralytics.models import RTDETR
from draw import test_corner_boxes
from vehicle_alarm import vehicle_alarm, vehicle_alarm_last

# ----------------函数（等待放置于相关工具类）----------------------------------
# 对于每一帧的处理
def process_frame(results, max_id_per_class, count_per_class):
    # 获取当前帧的类别ID和跟踪ID
    class_ids = results.boxes.cls.cpu().numpy().astype(int)
    track_ids = results.boxes.id.cpu().numpy().astype(int)

    # 更新每个类别的最大ID和计数
    for class_id, track_id in zip(class_ids, track_ids):
        # 如果这是这个类别见过的最大ID，更新max_id_per_class
        if track_id > max_id_per_class[class_id]:
            # 更新这个类别的最大ID
            max_id_per_class[class_id] = track_id
            # 对于每个新的track_id，增加该类别的计数
            count_per_class[class_id] += 1

def probe_rtmp_stream(url):
    try:
        ffmpeg.probe(url)
    except ffmpeg.Error as e:
        pass

def detect(UAV_status):
    # ----------------路径设置----------------------------------
    source_path = "E:/videos_for_test/DJI_20240217140153_0001_Z.mp4"  # 视频路径
    # weights_path = "best/best1.pt"  # 权重文件路径
    weights_path = "weights/rtdetr-l-1280-batch1-all.pt"
    save_path = "runs"  # 运行结果保存路径
    tracker = "botsort.yaml"  # 所采用的跟踪算法
    save_directory = "runs/screenshot"  # 异常图片保存路径
    vehicle_directory = "runs/vehicle_screenshot"

    # ----------------参数设置------------------------------------
    # 设置报警帧间隔
    alarm_clock = 30
    # 设置人数变动阈值
    person_increase_or_decrease = 10
    # 帧计数
    frame_count = 0
    # 人数变动计数
    person_change_count = 0
    # 初始人数
    num_person = 0
    rtmp_sub_url = str(UAV_status["data"]["rtmpSubUrl"])

    # ----------------初始化------------------------------------
    # 每个类别当前的最大ID
    max_id_per_class = {i: -1 for i in range(9)}  # 假设类别ID范围为0到8
    # 每个类别的计数
    count_per_class = {i: 0 for i in range(9)}
    # 用于计时：每隔五秒输出一次各个类的累计数量
    p_start = time.time()

    # ------------------推理模块-----------------------------------
    start = time.time()
    model = RTDETR(weights_path)
    classes = [i for i in range(9)]
    results = model.track(
        source=rtmp_sub_url,
        stream=True,  # 流模式处理，防止因为因为堆积而内存溢出
        show=True,  # 实时推理演示
        tracker=tracker,  # 默认tracker为botsort
        save=True,
        save_dir=save_path,
        # vid_stride=2,  # 视频帧数的步长，即隔几帧检测跟踪一次
        # save_txt=True,  # 把结果以txt形式保存
        # save_conf=True,  # 保存置信度得分
        # save_crop=True,  # 保存剪裁的图像
        classes=classes,  # 忽略’火焰‘和’烟雾‘类别
        conf=0.4,
        iou=0.5,
        device=0,
    )

    """
    # result.names输出的class为：
    # {0: 'person', 1: 'helmet', 2: 'life jacket', 3: 'truck', 4: 'excavator', 、
    # 5: 'car crane', 6: 'crawler crane', 7: 'rotary drill rig', 8: 'concrete tanker', 9: 'flame', 10: 'smoke'}
    # 其中 0:person 和 1:helmet 是重点要处理的
    """

    for r in results:
        frame_count += 1

        boxes = r.boxes  # Boxes object for bbox outputs
        masks = r.masks  # Masks object for segment masks outputs
        probs = r.probs  # Class probabilities for classification outputs

        # 得到某一帧的检测结果(转化为PIL图片)
        im_array = r.plot(conf=False, line_width=1, font_size=1.5)  # plot a BGR numpy array of predictions
        # im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
        # im.show()  # show image
        # im.save(det_img_path)  # save image

        if r.boxes.id is not None:  # boxes.id:盒子的轨道id(如果可以被跟踪算法检测的话就为True)。
            # ----------------------对各个类别进行累计计数------------------------
            # 得放进来否则在r.boxes.id为None的时候会报错
            process_frame(r, max_id_per_class, count_per_class)
            # 打印累计计数
            # print(count_per_class)

            # ----------------------------------------------------------------

            class_ids = r.boxes.cls.cpu().numpy().astype(int)
            class_ids_string = generate_detailed_statistics_string(class_ids)
            class_ids_vehicle_string = generate_detailed_vehicle_statistics_string(class_ids)
            objects_location_string = generate_objects_location_string(boxes.xyxy, boxes.cls)

            if time.time() - p_start >= 30:
                # ---------------------先保存numpy数组格式的图像--------------------
                # 形成文件名
                filename = str(int(time.time())) + ".png"  # 使用当前时间的时间戳（无小数点）
                _file_path = os.path.join(vehicle_directory, filename)

                # 保存图像
                cv2.imwrite(_file_path, im_array)  # OpenCV的方法来保存numpy数组格式的图像
                # ---------------------------------------------------------------

                vehicle_alarm(_file_path, count_per_class, UAV_status, class_ids_vehicle_string,
                              objects_location_string)
                p_start = time.time()
                # print("6秒时间到")

            # ----------------------------------------------------------------

            # 首先保存上一帧的人数
            last_frame_persons = num_person
            # 接下来对目前帧的person和helmet个数进行统计
            num_person = np.sum(class_ids == 0)
            num_helmet = np.sum(class_ids == 1)
            # 统计变动人数
            person_change_count += abs(last_frame_persons - num_person)
            # 报警条件判断
            # 时间/检测帧数足够了,若检测到未戴安全帽立即警报
            if frame_count >= alarm_clock:
                # ----------------------处理选框------------------------

                # 得到某一帧的检测结果(转化为PIL图片)
                im_alarm_array = r.plot(conf=False, line_width=1, font_size=1.5,
                                        vehicle=False)  # plot a BGR numpy array of
                out_img = test_corner_boxes(im_alarm_array, boxes.xywh, boxes.xyxy, boxes.cls, boxes.id, l=5,
                                            is_transparent=True,
                                            draw_type=True, draw_corner=True)
                # 形成文件名
                filename = str(int(time.time())) + ".png"  # 使用当前时间的时间戳（无小数点）
                file_path = os.path.join(save_directory, filename)
                # 保存图像
                cv2.imwrite(file_path, out_img)  # OpenCV的方法来保存numpy数组格式的图像
                # -----------------------------------------------------
                person_change_count = 0
                print(objects_location_string)
                cap_alarm(UAV_status, file_path, num_person, num_helmet, class_ids_string, objects_location_string)
                print("此帧异常检测图片已保存至", file_path, ",并同步上传至数据库。")
                frame_count = 0

    # ---------------------推理结束调vehicle_alarm接口---------------------
    # 先保存numpy数组格式的图像
    # 形成文件名
    filename = str(int(time.time())) + ".png"  # 使用当前时间的时间戳（无小数点）
    _file_path = os.path.join(vehicle_directory, filename)

    # 保存图像
    cv2.imwrite(_file_path, im_array)  # OpenCV的方法来保存numpy数组格式的图像
    # ---------------------------------------------------------------
    print(objects_location_string)
    vehicle_alarm_last(_file_path, count_per_class, UAV_status, class_ids_string, objects_location_string)
    # ----------------------------------------------------------------

    end = time.time()
    print("推理所用时间:", end - start)


def check_rtmp_stream():
    while True:
        uav_status = get_UAV_status()
        url = uav_status["data"]["rtmpSubUrl"]
        if url:
            print("RTMP stream: " + str(url) + " is available.")
            detect(uav_status)
            time.sleep(60)
        else:
            print("RTMP stream is not available.")
            time.sleep(60)

check_rtmp_stream()

#if __name__ == "__main__":
#    url = "E:/videos_for_test/DJI_20240326140208_0001_Z.mp4"
#    detect(url, UAV_status="")
# -----------------------------------------------------------------------------------------------------------------------------
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

"""
# 用 supervision 解析预测结果 supervision的from_ultralytics方法对yolo和rt-detr均适用
# 此外supervision可以划分区域，并检测区域内有没有目标，这个对于"工地重载车辆周围的安全性判断"有重要意义
detections = sv.Detections.from_ultralytics(r)
# 只保留人和头盔，也就是class_id=0或1
detections = detections[(detections.class_id == 0) | (detections.class_id == 1)]
# 解析追踪ID
if r.boxes.id is not None: print(boxes)

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
"""
