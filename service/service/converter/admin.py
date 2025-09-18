from django.contrib import admin
from .models import DesignTokens, ConversionTask, ConversionResult


@admin.register(DesignTokens)
class DesignTokensAdmin(admin.ModelAdmin):
    """设计令牌管理"""
    list_display = ['name', 'creator', 'created_time', 'file_size']
    list_filter = ['created_time', 'creator']
    search_fields = ['name', 'creator__email']
    readonly_fields = ['id', 'created_time', 'updated_time']

    def file_size(self, obj):
        try:
            return f"{obj.file.size} bytes"
        except:
            return "N/A"
    file_size.short_description = "文件大小"


@admin.register(ConversionTask)
class ConversionTaskAdmin(admin.ModelAdmin):
    """转换任务管理"""
    list_display = ['name', 'creator', 'status', 'progress', 'created_time', 'completed_at']
    list_filter = ['status', 'created_time', 'creator']
    search_fields = ['name', 'creator__email']
    readonly_fields = ['id', 'created_time', 'updated_time', 'started_at', 'completed_at']
    list_editable = ['status']

    def get_queryset(self, request):
        """只显示当前用户创建的任务（管理员除外）"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(creator=request.user)


@admin.register(ConversionResult)
class ConversionResultAdmin(admin.ModelAdmin):
    """转换结果管理"""
    list_display = ['task_name', 'task_creator', 'created_time']
    list_filter = ['created_time', 'task__creator']
    search_fields = ['task__name', 'task__creator__email']
    readonly_fields = ['id', 'created_time', 'updated_time']

    def task_name(self, obj):
        return obj.task.name
    task_name.short_description = "任务名称"

    def task_creator(self, obj):
        return obj.task.creator.email
    task_creator.short_description = "创建者"

    def get_queryset(self, request):
        """只显示当前用户任务的结果（管理员除外）"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(task__creator=request.user)
