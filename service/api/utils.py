import os
import zipfile
import tempfile
from django.conf import settings

def extract_sketch_file(sketch_file):
    """
    将.sketch文件作为zip文件解压到指定目录
    
    Args:
        sketch_file: 上传的.sketch文件对象
        
    Returns:
        str: 解压后的目录路径
    """
    # 获取原始文件名（不包含扩展名）
    original_name = os.path.splitext(sketch_file.name)[0]
    
    # 创建以原始文件名命名的目录
    output_dir = os.path.join(settings.MEDIA_ROOT, original_name)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 将上传的文件保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in sketch_file.chunks():
                temp_file.write(chunk)
        
        # 解压.sketch文件（作为zip文件处理）
        with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
            
        # 删除临时文件
        os.unlink(temp_file.name)
        
        return output_dir
        
    except Exception as e:
        # 如果出现错误，清理输出目录
        if os.path.exists(output_dir):
            import shutil
            shutil.rmtree(output_dir)
        raise e