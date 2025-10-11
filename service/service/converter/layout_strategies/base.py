from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseLayoutStrategy(ABC):
    """
    所有布局分析策略都必须遵守的抽象基类（接口）。
    """

    @abstractmethod
    def analyze(self, layers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析一组图层，并返回最终的布局分析结果。

        :param layers: 要分析的图层列表。
        :return: 一个包含 'layout_groups' 和 'outlier_indices' 的字典。
        """
        pass
