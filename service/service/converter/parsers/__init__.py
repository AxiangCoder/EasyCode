
from .base import BaseParser
from .sketch.converter import SketchParser


def get_parser_class(source_type: str) -> type[BaseParser]:
    """
    解析器工厂函数，根据源类型返回相应的解析器类。

    :param source_type: 设计源类型 (例如, 'sketch', 'figma').
    :return: 对应的解析器类。
    :raises ValueError: 如果源类型不被支持。
    """
    if source_type == 'sketch':
        return SketchParser
    # elif source_type == 'figma':
    #     return FigmaParser  # 未来可以添加
    else:
        raise ValueError(f"Unsupported source type: {source_type}")
