import requests
from datetime import datetime
# from HK.bim_post_image import upload_drone_img
from bim_post_image import upload_drone_img

url_for_production = "http://58.49.74.231:118/api/LSPersonnel/AddVideoRecognitionResult"
url_for_QDEQ = "http://119.36.93.100:9562/sysapi/Task/AnalysisResult"


# url_for_test = "http://58.49.74.231:106/api/LSPersonnel/AddVideoRecognitionResult"

def analysis_results(violator_lsnumber, event_type, camera_id, violation_photo, event_description=""):
    """
    将风险识别的异常报警记录写入到数据库，同时将该抽检帧上传至服务器。【简易信息】

    Args:
        violator_lsnumber (string): 违规人员ID，未成功识别时输入"-1"，识别成功时输入人员ID。
        event_type (string): 违规事件类型。
            - 无人机检测未戴安全帽: "50"
            - 无人机识别工程机械和类数量统计: "51"
            - 无人机统计人员机械总数: "52"
        camera_id (string): 由配置文件输入，测试时输入 "anJiu1"。
        violation_photo (string): 异常抽检照片存储路径。
        event_description (string, optional): 违规事件描述，默认为空。
    """

    # 将图片上传到文件服务器，数据上传到数据库中
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
    将风险识别的异常报警记录写入到数据库，同时将该抽检帧上传至服务器。【详细信息】

    Args:
        violator_lsnumber (string): 违规人员ID，未成功识别时输入"-1"，识别成功时输入人员ID。
        event_type (string): 违规事件类型。
            - 无人机检测未戴安全帽: "50"
            - 无人机识别工程机械和类数量统计: "51"
            - 无人机统计人员机械总数: "52"
        camera_id (string): 由配置文件输入，测试时输入 "anJiu1"。
        violation_photo (string): 异常抽检照片存储路径。
        UAV_status (dict): UAV 飞行信息。
        CurrentObject (string, optional): 描述当前帧的各个类别的数量，默认为空。
        CurrentLocation (string, optional): 描述类别的位置，默认为空。
        event_description (string, optional): 违规事件描述，默认为空。
    """

    # 将图片上传到文件服务器，数据上传到数据库中
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


