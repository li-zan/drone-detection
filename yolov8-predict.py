# predict by yolo_model   ---------------   yolo模型预测(不包含追踪)
from ultralytics.models import YOLO

source_path = "video/test1.mp4"
weights_path = "weights/yolov8-1280.pt"

model = YOLO(weights_path)
model.predict(source_path)
