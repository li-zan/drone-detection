import requests
from datetime import datetime
# from HK.bim_post_image import upload_drone_img
from bim_post_image import upload_drone_img

url_for_production = "http://58.49.74.231:118/api/LSPersonnel/AddVideoRecognitionResult"
url_for_QDEQ = "http://119.36.93.100:9562/sysapi/Task/AnalysisResult"


# url_for_test = "http://58.49.74.231:106/api/LSPersonnel/AddVideoRecognitionResult"

def analysis_results(violator_lsnumber, event_type, camera_id, violation_photo, event_description=""):
    """
    将风险识别的异常报警记录写入到数据库
    :param violator_lsnumber: string，必须，违规人员ID，未成功识别时输入-1，识别成功时输入人员ID，由接口1获取
    :param event_type: string，必须，违规事件类型，无人机未戴安全帽：50，无人机识别工程机械和类数量统计：51
    :param time: DateTime，必须，时间
    :param camera_id: string，必须，由配置文件输入，测试时输入anJiu1
    :param violation_photo: string，必须，照片存储路径，由接口3文件服务器接口获得
    :param id: string，非必须，唯一ID值，不可重复，不输入时由系统自动生成
    :param event_description: string，非必须，违规事件描述，默认不写，如预置点信息采集则定义为球机或者枪机的预置点位置：，preset point 1，preset point 2，preset point 3
    :return:
    """

    # TODO 将图片上传到文件服务器，数据上传到数据库中
    upload_img_status, upload_img_path = upload_drone_img(violation_photo, camera_id)
    # 如果图片上传成功,将数据插入数据库
    if upload_img_status:
        Createtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(Createtime)

        # 将数据插入数据库
        url_upload = url_for_production

        result = requests.post(url=url_upload, json={
            "Violator_LSNumber": "{}".format(violator_lsnumber),
            "EventType": "{}".format(event_type),
            "time": Createtime,
            "CameraID": "{}".format(camera_id),
            "ViolationPhoto": "{}".format(upload_img_path),
            "T2": 6,  # 插入数据库的时间间隔限制
            "EventDescription": "{}".format(event_description)
        }
                               )

        print(result)
        result_json = result.json()
        print(result_json)

    else:
        print("[INFO] 文件：%s 上传失败！" % upload_img_path)

def analysis_results_for_QDEQ(violator_lsnumber, event_type, camera_id, violation_photo, UAV_status, CurrentObject="", CurrentLocation="", event_description=""):
    """
    将风险识别的异常报警记录写入到数据库
    :param violator_lsnumber: string，必须，违规人员ID，未成功识别时输入-1，识别成功时输入人员ID，由接口1获取
    :param event_type: string，必须，违规事件类型，无人机未戴安全帽：50，无人机识别工程机械：51 无人机统计人员机械总数：52
    :param time: DateTime，必须，时间
    :param camera_id: string，必须，由配置文件输入，测试时输入anJiu1
    :param violation_photo: string，必须，照片存储路径，由接口3文件服务器接口获得
    :param id: string，非必须，唯一ID值，不可重复，不输入时由系统自动生成
    :param CurrentObject: string，非必须，唯一ID值，描述当前帧的各个类的数量
    :param event_description: string，非必须，违规事件描述，默认不写，如预置点信息采集则定义为球机或者枪机的预置点位置：，preset point 1，preset point 2，preset point 3
    :return:
    """

    # TODO 将图片上传到文件服务器，数据上传到数据库中
    upload_img_status, upload_img_path = upload_drone_img(violation_photo, camera_id)
    # 如果图片上传成功,将数据插入数据库
    if upload_img_status:
        Createtime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        print(Createtime)

        # 将数据插入数据库
        url_upload = url_for_QDEQ

        # 从 UAV_status 中获取信息
        plan_id = UAV_status["data"]["planId"]
        flight_time = UAV_status["data"]["time"]
        record_id = UAV_status["data"]["uavRecordId"]
        project_id = UAV_status["data"]["projectId"]

        result = requests.post(url=url_upload, json={
            "Violator_LSNumber": "{}".format(violator_lsnumber),
            "EventType": "{}".format(event_type),
            "time": Createtime,
            "CameraID": "{}".format(camera_id),
            "ViolationPhoto": "{}".format(upload_img_path),
            "T2": 6,  # 插入数据库的时间间隔限制
            "EventDescription": "{}".format(event_description),
            "ProjectId": "{}".format(project_id),
            "RobotId": "0",
            "PlanId": "{}".format(plan_id),
            "RecordId": "{}".format(record_id),
            "FlightTime": "{}".format(flight_time),
            "CurrentObject": "{}".format(CurrentObject),
            # "Location": "{}".format(CurrentLocation),
        }
                               )

        print(result)
        result_json = result.json()
        print(result_json)

    else:
        print("[INFO] 文件：%s 上传失败！" % upload_img_path)

if __name__ == "__main__":
    UAV_status = {
        "data": {
            "planId": "1792375875246444546",
            "time": "2024-07-26T10:30:00",
            "uavRecordId": "1816367780593799168",
            "projectId": "29"
        }
    }

    Createtime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    print(Createtime)

    # 将数据插入数据库
    url_upload = url_for_QDEQ

    # 从 UAV_status 中获取信息
    plan_id = UAV_status["data"]["planId"]
    flight_time = UAV_status["data"]["time"]
    record_id = UAV_status["data"]["uavRecordId"]
    project_id = UAV_status["data"]["projectId"]

    result = requests.post(url=url_upload, json={
        "Violator_LSNumber": "{}".format("-1"),
        "EventType": "{}".format("51"),
        "time": Createtime,
        "CameraID": "{}".format("QDEJ-WRJ"),
        "ViolationPhoto": "{}".format("/Upload/DroneImage/QDER-WRJ/1722168234260_S_20240728203013314.jpg"),
        "T2": 6,  # 插入数据库的时间间隔限制
        "EventDescription": "{}".format(""),
        "ProjectId": "{}".format(project_id),
        "RobotId": "0",
        "PlanId": "{}".format(plan_id),
        "RecordId": "{}".format(record_id),
        "FlightTime": "{}".format(flight_time),
        "CurrentObject": "{}".format(""),
        # "Location": "{}".format(CurrentLocation),
    }
                           )

    print(result)
    result_json = result.json()
    print(result_json)


