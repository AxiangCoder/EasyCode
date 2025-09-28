
from abc import ABC, abstractmethod

class BaseParser(ABC):
    """
    解析器抽象基类，定义了所有解析器必须遵循的接口。
    """

    def __init__(self, source_data: dict, tokens_data: dict):
        """
        初始化解析器。

        :param source_data: 已加载的源设计文件数据（Python 字典）。
        :param tokens_data: 已加载的设计令牌数据（Python 字典）。
        """
        self.source_data = source_data
        self.tokens_data = tokens_data

    @staticmethod
    @abstractmethod
    def count_nodes(source_data: dict) -> int:
        """
        静态方法，用于在转换开始前快速计算源数据中的总节点数。
        这对于实现进度跟踪至关重要。

        :param source_data: 已加载的源设计文件数据。
        :return: 节点总数。
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, progress_callback=None) -> tuple:
        """
        执行转换的核心方法。

        :param progress_callback: 一个可选的回调函数，用于在处理过程中报告进度。
                                  它应接受 (handled_nodes, total_nodes) 两个参数。
        :return: 一个元组 (dsl_dict, metadata_dict)，其中:
                 - dsl_dict: 标准化的 DSL 输出。
                 - metadata_dict: 包含附加信息（如 Token 使用报告）的元数据字典。
        """
        raise NotImplementedError
