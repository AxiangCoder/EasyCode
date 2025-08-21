import { getSelectedLayerOriginalStyles } from './getOriginalStyles';

/**
 * 导出原始样式为JSON文件
 * @param {Object} context - Sketch 上下文对象
 * @param {Object} options - 导出选项
 * @returns {Object} 导出结果
 */
const exportOriginalStyles = (context, options = {}) => {
  // 获取原始样式数据
  const stylesData = getSelectedLayerOriginalStyles(context);
  
  if (stylesData.error) {
    throw new Error(stylesData.error);
  }

  // 构建导出文件名
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const layerName = stylesData.container ? 
    stylesData.container.name.replace(/[^a-zA-Z0-9]/g, '_') : 
    'unknown_layer';
  const fileName = `original_styles_${layerName}_${timestamp}.json`;

  // 构建完整的导出数据
  const exportData = {
    metadata: {
      exportType: 'original_styles',
      // sketchVersion: context.api.version,
      exportTime: new Date().toISOString(),
      fileName: fileName,
      options: options
    },
    styles: stylesData
  };

  // 格式化JSON字符串
  const jsonString = JSON.stringify(exportData, null, 2);

  // 创建文件内容
  const fileContent = jsonString;

  // 计算总图层数量（递归统计）
  const countLayers = (node) => {
    let count = 1; // 当前节点
    if (node.children && node.children.length > 0) {
      node.children.forEach(child => {
        count += countLayers(child);
      });
    }
    return count;
  };

  const totalLayers = countLayers(stylesData);

  // 返回导出结果
  return {
    success: true,
    fileName: fileName,
    fileContent: fileContent,
    dataSize: fileContent.length,
    layerCount: totalLayers,
    timestamp: new Date().toISOString()
  };
};

/**
 * 导出样式数据到剪贴板
 * @param {Object} context - Sketch 上下文对象
 * @returns {Object} 导出结果
 */
const exportStylesToClipboard = (context) => {
  const stylesData = getSelectedLayerOriginalStyles(context);
  
  if (stylesData.error) {
    throw new Error(stylesData.error);
  }

  // 格式化JSON字符串
  const jsonString = JSON.stringify(stylesData, null, 2);
  
  // 复制到剪贴板（需要Sketch API支持）
  if (context.api && context.api.copyToClipboard) {
    context.api.copyToClipboard(jsonString);
  }

  return {
    success: true,
    message: '样式数据已复制到剪贴板',
    dataSize: jsonString.length
  };
};

/**
 * 获取样式数据的统计信息
 * @param {Object} context - Sketch 上下文对象
 * @returns {Object} 统计信息
 */
const getStylesStatistics = (context) => {
  const stylesData = getSelectedLayerOriginalStyles(context);
  
  if (stylesData.error) {
    throw new Error(stylesData.error);
  }

  const stats = {
    success: true,
    containerName: stylesData.container ? stylesData.container.name : 'N/A',
    containerType: stylesData.container ? stylesData.container.type : 'N/A',
    totalLayers: stylesData.metadata ? stylesData.metadata.totalLayers : 1,
    layerTypes: stylesData.metadata ? stylesData.metadata.layerTypes : {},
    hasFills: false,
    hasBorders: false,
    hasShadows: false,
    hasTextStyles: false,
    timestamp: new Date().toISOString()
  };

  // 分析样式类型
  const analyzeLayerStyles = (layer) => {
    if (layer.style) {
      if (layer.style.fills && layer.style.fills.length > 0) stats.hasFills = true;
      if (layer.style.borders && layer.style.borders.length > 0) stats.hasBorders = true;
      if (layer.style.shadows && layer.style.shadows.length > 0) stats.hasShadows = true;
      if (layer.style.textStyle) stats.hasTextStyles = true;
    }
  };

  // 分析容器样式
  if (stylesData.container) {
    analyzeLayerStyles(stylesData.container);
  }

  // 分析子图层样式
  if (stylesData.children) {
    stylesData.children.forEach(child => {
      analyzeLayerStyles(child);
    });
  }

  return stats;
};

export { 
  exportOriginalStyles, 
  exportStylesToClipboard, 
  getStylesStatistics 
}; 