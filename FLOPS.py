"""
测试参数量和计算量
"""

import torch
from thop import profile
from ultralytics.utils.torch_utils import model_info

from ultralytics.models import YOLO, RTDETR

# Model
# print('==> Building model..')
# model = YOLO("weights/yolov8-sahi-1280.pt")
#
# dummy_input = torch.randn(1, 3, 224, 224)
# flops, params = profile(model, (dummy_input,))
# print('flops: ', flops, 'params: ', params)
# print('flops: %.2f M, params: %.2f M' % (flops / 1000000.0, params / 1000000.0))


if __name__ == '__main__':
    # model = YOLO("../weights/yolov8-1280.pt")
    model = RTDETR("../weights/rtdetr-l-1280-batch1-all.pt")
    print(model_info(model, True, True, 1280))
