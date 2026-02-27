import sys
import os
from pathlib import Path


# 火山引擎TOS配置 
AK = "请填写你的 TOS Access Key"   
SK = "请填写你的 TOS Secret Key"
BUCKET_NAME = "请填写你的 TOS BUCKET_NAME"               
REGION = "cn-guangzhou"

# 豆包API Key
ARK_API_KEY = "你的_ACCESS_KEY_ID_请填写" #从火山引擎获取豆包模型密钥

#===============================七牛 API KEY================================
QINIU_API_KEY = '你的_ACCESS_KEY_ID_请填写' #七牛云api平台获取


# 支持的图片扩展名
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}


def resource_path(relative_path):
    """用于 config.py 初始化路径"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

LOCAL_IMAGE_PATH = Path(resource_path("product_image"))