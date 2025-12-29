import base64
import io
from PIL import Image
from typing import Tuple

def validate_and_resize_image(image_base64: str, max_size: int = 1024) -> Tuple[str, str]:
    """
    验证并压缩图片，确保其适合 LLM 或存储
    返回: (压缩后的 base64, mime_type)
    """
    # 解码
    try:
        header, encoded = image_base64.split(",", 1) if "," in image_base64 else (None, image_base64)
        img_data = base64.b64decode(encoded)
        img = Image.open(io.BytesIO(img_data))
    except Exception as e:
        raise ValueError(f"无效的图片数据: {e}")

    # 获取原始格式
    fmt = img.format if img.format else "JPEG"
    mime_type = f"image/{fmt.lower()}"

    # 缩放
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    # 转换回 base64
    buffered = io.BytesIO()
    img.save(buffered, format=fmt)
    compressed_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return compressed_base64, mime_type
