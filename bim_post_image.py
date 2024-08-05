# -*- coding: utf-8 -*-
# _author_ = nick chen
# Email: nick_ecust@163.com

"""
访问地址：http://58.49.74.231:85/Upload/CarLicense/1/20201223145854_下山_car_赣g5q867_64d6_S_20201223155928842.jpg
返回信息：
{'datas':
    [{
    'originalName': '20201223145854_下山_car_赣G5Q867_64d6.jpg',
    'saveName': '20201223145854_下山_car_赣g5q867_64d6_S_20201223155928842.jpg',
    'virtulPath': '/Upload/CarLicense/1/20201223145854_下山_car_赣g5q867_64d6_S_20201223155928842.jpg',
    'thumbnailVirtulPath': '/Upload/CarLicense/1/20201223145854_下山_car_赣g5q867_64d6_S_20201223155928842Thumbnail.jpg',
    'thumbnailName': '20201223145854_下山_car_赣g5q867_64d6_S_20201223155928842Thumbnail.jpg'}
    ],
'message': '',
'success': True}
"""

import requests


def upload_img(img_path, camera_id):
    """
    上传图片
    :param img_path: 需要上传的图片路径
    :param camera_id: 摄像头对应的ID，用于在数据库中生成目录
    :return: 状态值（True or False)，图片路径（与地址拼接后可访问）
    """
    virtual_dic = "CarLicense/{}".format(camera_id)
    url = "http://58.49.74.231:85/UploadFile/Upload?virtualDic=%s&createThumbnail=false" % virtual_dic

    files = {'file': open(img_path, 'rb')}
    result = requests.post(url=url, files=files)
    result_json = result.json()
    upload_status = result_json["success"]
    upload_img_path = result_json["datas"][0]["virtulPath"]
    return upload_status, upload_img_path


def upload_drone_img(img_path, camera_id):
    """
    上传图片
    :param img_path: 需要上传的图片路径
    :param camera_id: 摄像头对应的ID，用于在数据库中生成目录
    :return: 状态值（True or False)，图片路径（与地址拼接后可访问）
    """
    virtual_dic = "DroneImage/{}".format(camera_id)
    url = "http://58.49.74.231:85/UploadFile/Upload?virtualDic=%s&createThumbnail=false" % virtual_dic

    files = {'file': open(img_path, 'rb')}
    result = requests.post(url=url, files=files)
    result_json = result.json()
    upload_status = result_json["success"]
    upload_img_path = result_json["datas"][0]["virtulPath"]
    return upload_status, upload_img_path
    #return result_json



if __name__ == "__main__":
    res = upload_drone_img(img_path="E:/pic_for_test/北六环4标-0726/1722168234260.jpg", camera_id="QDER-WRJ")
    print(res)