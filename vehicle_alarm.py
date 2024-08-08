# -------------------预警模块-工程车辆-----------------------------------------------

from drone_video_alarm import analysis_results, analysis_results_for_QDEQ


def vehicle_alarm(path, number_info, UAV_status, class_ids_string, objects_location_string):
    """
    关于当前抽检帧的人员车辆统计的报警模块

    Args:
        path (string): 机械车辆抽检帧图片保存路径。
        number_info (dict, optional): 累计所有类别与其对应的数量。
        UAV_status (dict): UAV 飞行信息。
        class_ids_string (string): 描述当前帧的人员机械的数量。
        objects_location_string (string): 描述类别的位置。
    """

    # 调用 analysis_results_for_QDEQ 函数
    analysis_results_for_QDEQ(violator_lsnumber="-1", event_type="51", camera_id="QDER-WRJ",
                              violation_photo=path, UAV_status=UAV_status,
                              CurrentObject="", CurrentLocation=objects_location_string,
                              event_description=class_ids_string)


def vehicle_alarm_last(path, number_info, UAV_status, class_ids_string, objects_location_string, args):
    """
    关于最后累计人员车辆统计的报警模块

    Args:
        path (string): 最后帧保存路径。
        number_info (dict): 累计所有类别与其对应的数量。
        UAV_status (dict): UAV 飞行信息。
        class_ids_string (string, optional): 描述当前帧的人员机械的数量。
        objects_location_string (string, optional): 描述类别的位置。
        args: 参数配置。
    """
    ch_labels = args.person_vehicle_names

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
