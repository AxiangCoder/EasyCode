from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from core.models import BaseModel
import json

User = get_user_model()

class DesignTokens(BaseModel):
    """设计令牌配置文件"""
    name = models.CharField(max_length=100, help_text="令牌配置名称")
    file = models.FileField(
        upload_to='design_tokens/',
        validators=[FileExtensionValidator(['json'])],
        help_text="设计令牌JSON文件"
    )

    def __str__(self):
        return f"{self.name} ({self.creator.email if self.creator else 'System'})"

    class Meta:
        verbose_name = '设计令牌'
        verbose_name_plural = '设计令牌'


class ConversionTask(BaseModel):
    """转换任务"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    PHASE_CHOICES = [
        ('pending', '待开始'),
        ('dsl_conversion', 'DSL 转换'),
        ('frontend_generation', '前端生成'),
        ('completed', '已完成'),
    ]

    name = models.CharField(max_length=200, help_text="任务名称", null=True, blank=True,)
    source_type = models.CharField(
        max_length=20,
        choices=[
            ('sketch', 'Sketch'),
            ('figma', 'Figma'),
        ],
        default='sketch',
        help_text="设计源类型"
    )
    source_url = models.URLField(
        blank=True,
        null=True,
        help_text="设计源URL (例如 Figma 链接)"
    )
    input_file = models.FileField(
        upload_to='conversion_inputs/',
        help_text="输入的设计文件 (例如 Sketch 文件)",
        blank=True,
        null=True
    )
    design_tokens = models.ForeignKey(
        DesignTokens,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="使用的设计令牌"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="任务状态"
    )
    phase = models.CharField(
        max_length=32,
        choices=PHASE_CHOICES,
        default='pending',
        help_text="任务所处阶段"
    )
    progress = models.IntegerField(
        default=0,
        help_text="转换进度 (0-100)"
    )
    error_message = models.TextField(
        blank=True,
        help_text="错误信息"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="开始时间"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="完成时间"
    )
    llm_usage = models.JSONField(
        null=True,
        blank=True,
        help_text="LLM token 用量汇总"
    )
    input_nodes = models.IntegerField(
        null=True,
        blank=True,
        help_text="输入的总节点数"
    )
    handled_nodes = models.IntegerField(
        default=0,
        help_text="已处理的节点数"
    )
    hidden_nodes = models.IntegerField(
        default=0,
        help_text="隐藏的的节点数"
    )

    def __str__(self):
        return f"{self.name} - {self.status}"

    class Meta:
        verbose_name = '转换任务'
        verbose_name_plural = '转换任务'
        ordering = ['-created_time']


class ConversionResult(BaseModel):
    """转换结果"""
    task = models.OneToOneField(
        ConversionTask,
        on_delete=models.CASCADE,
        related_name='result',
        help_text="关联的转换任务"
    )
    dsl_output = models.JSONField(
        null=True,        # 允许数据库存储 NULL
        blank=True, 
        help_text="DSL输出结果"
    )
    token_report = models.JSONField(
        null=True,        # 允许数据库存储 NULL
        blank=True, 
        default=dict,
        help_text="令牌使用报告"
    )
    llm_usage = models.JSONField(
        null=True,        # 允许数据库存储 NULL
        blank=True,
        help_text="LLM token 用量汇总"
    )
    project_download_path = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="生成的前端项目压缩包存储路径"
    )

    def __str__(self):
        return f"Result for {self.task.name}"

    class Meta:
        verbose_name = '转换结果'
        verbose_name_plural = '转换结果'

    @property
    def dsl_archive_path(self) -> str:
        """返回 DSL 归档文件的默认相对路径。"""
        return f"conversion_out/{self.task.id}/dsl.json"

    def save_dsl_to_file(self):
        """将DSL输出保存到文件"""
        if not self.dsl_output:
            return None

        file_path = self.dsl_archive_path
        default_storage.delete(file_path)
        default_storage.save(file_path, ContentFile(json.dumps(self.dsl_output, ensure_ascii=False, indent=2)))
        return file_path
    
    def save_token_report_to_file(self):
        """将令牌报告保存到文件"""
        if not self.token_report:
            return None

        file_path = f"conversion_outputs/{self.task.id}/token_report.json"
        default_storage.save(file_path, ContentFile(json.dumps(self.token_report, ensure_ascii=False, indent=2)))
        return file_path
    
