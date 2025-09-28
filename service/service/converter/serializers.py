from rest_framework import serializers
from .models import DesignTokens, ConversionTask, ConversionResult


class DesignTokensSerializer(serializers.ModelSerializer):
    """设计令牌序列化器"""
    file_size = serializers.SerializerMethodField()
    creator_email = serializers.CharField(source='creator.email', read_only=True)

    class Meta:
        model = DesignTokens
        fields = [
            'id', 'name', 'file', 'file_size', 'creator_email',
            'created_time', 'updated_time'
        ]
        read_only_fields = ['id', 'created_time', 'updated_time', 'creator_email']

    def get_file_size(self, obj):
        """获取文件大小"""
        try:
            return obj.file.size
        except:
            return 0

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class ConversionTaskSerializer(serializers.ModelSerializer):
    """转换任务序列化器"""
    creator_email = serializers.CharField(source='creator.email', read_only=True)
    input_file_size = serializers.SerializerMethodField()
    design_tokens_name = serializers.CharField(source='design_tokens.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    has_result = serializers.SerializerMethodField()
    result_id = serializers.SerializerMethodField()

    class Meta:
        model = ConversionTask
        fields = [
            'id', 'name', 'source_type', 'source_url', 'input_file', 'input_file_size', 'design_tokens',
            'design_tokens_name', 'status', 'status_display', 'progress',
            'error_message', 'started_at', 'completed_at', 'creator_email',
            'has_result', 'result_id', 'input_nodes', 'handled_nodes', 'hidden_nodes','created_time', 'updated_time'
        ]
        read_only_fields = [
            'id', 'status', 'progress', 'error_message', 'started_at',
            'completed_at', 'creator_email', 'has_result', 'result_id', 'input_nodes', 'handled_nodes', 'hidden_nodes','created_time', 'updated_time'
        ]

    def get_input_file_size(self, obj):
        """获取输入文件大小"""
        try:
            return obj.input_file.size
        except:
            return 0

    def get_has_result(self, obj):
        """检查是否有转换结果"""
        return hasattr(obj, 'result')

    def get_result_id(self, obj):
        """获取转换结果ID"""
        if hasattr(obj, 'result') and obj.result:
            return obj.result.id
        return None

    def validate(self, data):
        """验证输入源"""
        source_type = data.get('source_type')
        input_file = data.get('input_file')
        source_url = data.get('source_url')

        if source_type == 'sketch' and not input_file:
            raise serializers.ValidationError("当源类型为 Sketch 时，必须提供 input_file。")

        if source_type == 'figma' and not source_url:
            raise serializers.ValidationError("当源类型为 Figma 时，必须提供 source_url。")

        return data

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        if not validated_data.get('name'):
            input_file = validated_data.get('input_file')
            if input_file:
                filename = input_file.name.split('/')[-1] if '/' in input_file.name else input_file.name
                validated_data['name'] = filename
        return super().create(validated_data)


class ConversionResultSerializer(serializers.ModelSerializer):
    """转换结果序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    task_status = serializers.CharField(source='task.status', read_only=True)
    task_creator_email = serializers.CharField(source='task.creator.email', read_only=True)
    html_preview_url = serializers.SerializerMethodField()

    class Meta:
        model = ConversionResult
        fields = [
            'id', 'task', 'task_name', 'task_status', 'task_creator_email',
            'dsl_output', 'html_output', 'html_preview_url', 'token_report',
            'llm_usage', 'created_time', 'updated_time'
        ]
        read_only_fields = [
            'id', 'task', 'task_name', 'task_status', 'task_creator_email',
            'dsl_output', 'html_output', 'html_preview_url', 'token_report',
            'llm_usage','created_time', 'updated_time'
        ]

    def get_html_preview_url(self, obj):
        """获取HTML预览文件的URL"""
        if obj.html_output:
            return f"/media/conversion_outputs/{obj.task.id}/preview.html"
        return None


class ConversionTaskDetailSerializer(ConversionTaskSerializer):
    """转换任务详情序列化器（包含结果）"""
    result = ConversionResultSerializer(read_only=True)

    class Meta(ConversionTaskSerializer.Meta):
        fields = ConversionTaskSerializer.Meta.fields + ['result']


class DesignTokensListSerializer(serializers.ModelSerializer):
    """设计令牌列表序列化器"""
    creator_email = serializers.CharField(source='creator.email', read_only=True)
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = DesignTokens
        fields = ['id', 'name', 'file_size', 'creator_email', 'created_time']

    def get_file_size(self, obj):
        try:
            return obj.file.size
        except:
            return 0
