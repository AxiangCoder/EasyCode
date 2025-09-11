from rest_framework import serializers
from .models import Sketch


class SketchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sketch
        fields = ['id', 'sketch_file', 'created_time', 'updated_time', 'creator', 'is_delete']
        # read_only_fields: 将这些字段设置为只读，客户端提交数据时不能包含它们
        # 这些字段将由后端自动填充
        read_only_fields = ['creator', 'created_time', 'updated_time', 'id']