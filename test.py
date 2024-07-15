from PIL import ImageFont

font = ImageFont.truetype("simsun.ttc", size=20)
width, height = font.getsize("测试文本")  # 测试文本尺寸获取
print("Width:", width, "Height:", height)

# import PIL
# print(PIL.__version__)