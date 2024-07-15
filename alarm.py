# -------------------预警模块-未戴安全帽-----------------------------------------------

from drone_video_alarm import analysis_results, analysis_results_for_QDEQ


def cap_alarm(UAV_status, path, persons=0, helmets=0, class_ids_string="", objects_location_string=""):
    """
    关于未戴安全帽的报警模块
    :param path: img，必须，某一帧的检测画面
    :param persons: int，非必须，某一帧检测到的人数
    :param helmets: int，非必须，某一帧检测到的头盔数
    """
    # 判断是否要预警(当前只能通过比较persons和helmets的数目来判断是否有人没戴安全帽,不能精准定位到是哪个人违规了)
    if persons > helmets:
        print("当前人数:", persons, ",当前头盔数:", helmets, ",检测到有人未戴头盔！")
        # 调用接口 将违规信息写入数据库
        # analysis_results("-1", "50", "anJiu1", path)
        analysis_results_for_QDEQ("-1", "50", "QDEQ-WRJ", violation_photo=path, UAV_status=UAV_status, CurrentObject=class_ids_string, CurrentLocation=objects_location_string)
    else:
        print("当前人数:", persons, ",当前头盔数:", helmets, ",符合工地安全要求。")
