# -------------------预警模块-工程车量-----------------------------------------------

from drone_video_alarm import analysis_results, analysis_results_for_QDEQ


def vehicle_alarm(path, number_info, UAV_status, class_ids_string, objects_location_string):
    """
    关于未戴安全帽的报警模块
    :param path: img，必须，某一帧的检测画面
    :param number_info: string，输出当前每个label对应的数量消息，如person：7，helmet：8...
    """


     # 调用 analysis_results_for_QDEQ 函数
    analysis_results_for_QDEQ(violator_lsnumber="-1", event_type="51", camera_id="QDER-WRJ",
                                      violation_photo=path, UAV_status=UAV_status,
                                      CurrentObject="", CurrentLocation=objects_location_string,
                                      event_description=class_ids_string)

def vehicle_alarm_last(path, number_info, UAV_status, class_ids_string, objects_location_string):
    """
    关于未戴安全帽的报警模块
    :param path: img，必须，某一帧的检测画面
    :param number_info: string，输出当前每个label对应的数量消息，如person：7，helmet：8...
    """
    ch_labels = {0: '人',
                 3: '重型卡车',
                 4: '挖掘机',
                 5: '汽车吊机',
                 6: '履带吊机',
                 7: '旋挖钻机',
                 8: '水泥车'}

    # 遍历字典，并在每个迭代中调用 analysis_results_for_QDEQ
    for key, label in ch_labels.items():
        if key in number_info:
            # 生成当前类的累计数量描述
            current_output = f"{label}：{number_info[key]}"
            print(current_output)

            # 调用 analysis_results_for_QDEQ 函数
            analysis_results_for_QDEQ(violator_lsnumber="-1", event_type="52", camera_id="QDER-WRJ",
                                      violation_photo=path, UAV_status=UAV_status,
                                      CurrentObject="", CurrentLocation=objects_location_string,
                                      event_description=current_output)


if __name__ == "__main__":
    ch_labels = {0: '人',
                 1: '头盔',
                 2: '救生衣',
                 3: '重型卡车',
                 4: '挖掘机',
                 5: '汽车吊机',
                 6: '履带吊机',
                 7: '旋挖钻机',
                 8: '水泥车'}

    number_info = {0: 118, 1: 117, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}

    # 初始化一个空字符串用于收集输出
    output = "累计结果如下：\n"

    # 遍历字典，将信息添加到输出字符串
    for key in ch_labels:
        output += f"\"{ch_labels[key]}：{number_info[key]}\",\n"

    # 打印合并后的字符串
    print(output)

