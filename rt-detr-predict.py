# predict by re-detr_model   ---------------   detr模型预测(不包含追踪)
from ultralytics.models import RTDETR
source_path = "../DJI_0333.MP4"
weights_path = "weights/rtdetr-l-1280-batch1-all.pt"

model = RTDETR(weights_path)
model.predict(source_path)