from django.apps import AppConfig


class ConverterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'converter'

    """ def ready(self):
        from django.conf import settings
        if settings.DEBUG:
            print("--- 项目已启动，开始执行调试方法 ---")
            # 导入并调用你想要调试的方法
            try:
                from .models import Converter
                Converter()
            except Exception as e:
                print(f"执行调试方法时发生错误: {e}")

            print("--- 调试方法执行完毕 ---") """
