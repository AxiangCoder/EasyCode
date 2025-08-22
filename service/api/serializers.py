from rest_framework import serializers

class SketchFileSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)
    
    def validate_file(self, value):
        """验证上传的文件是否是.sketch文件"""
        if not value.name.endswith('.sketch'):
            raise serializers.ValidationError("只能上传.sketch文件")
        return value