from service.celeryapp import app as celery_app
# 它能确保当 Django 启动时，Celery 应用实例被加载，这样 @shared_task 装饰器才能找到并使用这个配置好的应用实例
__all__=('celery_app')

