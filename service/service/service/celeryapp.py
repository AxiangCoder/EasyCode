import os
from celery import Celery



# 设置Django的默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')

# 创建Celery应用实例
app = Celery('service')

# 从Django设置中加载配置，命名空间为CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务（从所有已注册的Django应用中）
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')