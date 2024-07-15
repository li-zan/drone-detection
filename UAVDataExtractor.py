import requests
from datetime import datetime

def get_uav_data(url):
    # 发送 HTTP GET 请求到指定的 URL
    response = requests.get(url)
    # 检查请求是否成功
    if response.status_code == 200:
        # 解析 JSON 响应
        data = response.json()
        # 提取所需的字段
        PlanId = data['data']['planId']
        RecordId = data['data'].get('uavRecordId')  # 使用 get 方法以处理 None 值
        FlvUrl = data['data'].get('flvUrl')
        WebRtcUrl = data['data'].get('webRtcUrl')
        RtmpSubUrl = data['data'].get('rtmpSubUrl')
        # 将 time 字段转换为 datetime 对象
        FlightTime = datetime.fromisoformat(data['data']['time'])
        return PlanId, RecordId, FlightTime, FlvUrl, WebRtcUrl, RtmpSubUrl
    else:
        raise Exception("Failed to get data from the URL")

# 调用函数并打印结果
try:
    url = "http://119.36.93.100:9562/sysapi/Task/GetUAVStatus"
    PlanId, RecordId, FlightTime, FlvUrl, WebRtcUrl, RtmpSubUrl = get_uav_data(url)
    print("PlanId:", PlanId)
    print("RecordId:", RecordId)
    print("FlightTime:", FlightTime)
    print("FlvUrl:", FlvUrl)
    print("WebRtcUrl:", WebRtcUrl)
    print("RtmpSubUrl:", RtmpSubUrl)
except Exception as e:
    print("Error:", e)
