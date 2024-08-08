import requests

# url_for_UAV_status = "http://119.36.93.100:9562/sysapi/Task/GetUAVStatus?projectId=29"
url_for_UAV_status = "http://10.84.11.153:9562/sysapi/Task/GetUAVStatus?projectId=29"

def get_UAV_status():
    response = requests.get(url_for_UAV_status)

    if response.status_code == 200:
        UAV_status = response.json()

        # 测试接口
        '''
        plan_id = UAV_status["data"]["planId"]
        flight_time = UAV_status["data"]["time"]
        
        # print(plan_id)
        # print(flight_time)
        '''

        return UAV_status
    else:
        print(f"无人机状态获取失败\nError: {response.status_code} - {response.text}")

if __name__ == "__main__":
    url = get_UAV_status()
    print(url)