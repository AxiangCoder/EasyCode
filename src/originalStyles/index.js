import { getSelectedLayerOriginalStyles } from './getOriginalStyles';
import { exportOriginalStyles, exportStylesToClipboard, getStylesStatistics } from './exportStyles';

/**
 * 一键获取并导出原始样式（完整流程）
 * 包含选择验证、样式获取、文件导出等完整逻辑
 * @param {Object} sketchContext - Sketch 上下文对象
 * @param {Object} options - 导出选项
 * @returns {Object} 完整的结果对象
 */
const getAndExportOriginalStyles = (sketchContext, options = {}) => {
  try {
    // 1. 验证选择
    console.log(1);

    const validation = validateLayerSelection(sketchContext);
    console.log(validation);

    if (!validation.valid) {
      return {
        success: false,
        error: validation.message,
        type: 'validation_error'
      };
    }

    // 2. 获取原始样式
    const stylesData = getSelectedLayerOriginalStyles(sketchContext);
    console.log(stylesData);

    if (stylesData.error) {
      return {
        success: false,
        error: stylesData.error,
        type: 'styles_error'
      };
    }

    // 3. 导出样式
    const exportResult = exportOriginalStyles(sketchContext, {
      includeMetadata: true,
      format: 'pretty',
      ...options
    });

    if (!exportResult.success) {
      return {
        success: false,
        error: exportResult.error,
        type: 'export_error',
        stylesData: stylesData
      };
    }

    // 4. 返回完整结果
    return {
      success: true,
      validation: validation,
      stylesData: stylesData,
      exportResult: exportResult,
      statistics: {
        layerCount: exportResult.layerCount,
        dataSize: exportResult.dataSize,
        fileName: exportResult.fileName,
        containerName: stylesData.container ? stylesData.container.name : 'N/A',
        containerType: stylesData.container ? stylesData.container.type : 'N/A'
      }
    };

  } catch (error) {
    return {
      success: false,
      error: error.message,
      type: 'unknown_error'
    };
  }
};

/**
 * 验证图层选择是否有效
 * @param {Object} sketchContext - Sketch 上下文对象
 * @returns {Object} 验证结果
 */
const validateLayerSelection = (sketchContext) => {
  const selectedLayers = sketchContext.selection;
  if (!selectedLayers || selectedLayers.length === 0) {
    return {
      valid: false,
      message: '没有选中的图层'
    };
  }

  console.log('selectedLayers', selectedLayers);
  console.log('selectedLayers.length', selectedLayers.length);

  const layer = selectedLayers[0];
  console.log('layer', layer);
  const isContainer = layer.type === 'Group' || layer.type === 'Artboard';

  if (isContainer) {
    return {
      valid: true,
      message: `选中了${layer.type}类型的容器: ${layer.name}`,
      layerType: layer.type,
      layerName: layer.name
    };
  }

  // 检查是否有父级容器
  let parent = layer.parent;
  while (parent) {
    if (parent.type === 'Group' || parent.type === 'Artboard') {
      return {
        valid: true,
        message: `选中了${parent.type}类型的父级容器: ${parent.name}`,
        layerType: parent.type,
        layerName: parent.name,
        selectedLayer: layer.name
      };
    }
    parent = parent.parent;
  }

  return {
    valid: false,
    message: '选中的图层不在任何编组或框架内'
  };
};

/**
 * 快速获取原始样式（仅获取，不导出）
 * @param {Object} sketchContext - Sketch 上下文对象
 * @returns {Object} 样式数据或错误信息
 */
const quickGetOriginalStyles = (sketchContext) => {
  const validation = validateLayerSelection(sketchContext);
  if (!validation.valid) {
    return {
      success: false,
      error: validation.message
    };
  }

  const stylesData = getSelectedLayerOriginalStyles(sketchContext);
  if (stylesData.error) {
    return {
      success: false,
      error: stylesData.error
    };
  }

  return {
    success: true,
    data: stylesData,
    validation: validation
  };
};

/**
 * 快速导出样式（仅导出，不验证）
 * @param {Object} sketchContext - Sketch 上下文对象
 * @param {Object} options - 导出选项
 * @returns {Object} 导出结果
 */
const quickExportStyles = (sketchContext, options = {}) => {
  return exportOriginalStyles(sketchContext, {
    includeMetadata: true,
    format: 'pretty',
    ...options
  });
};

/**
 * 获取样式统计信息
 * @param {Object} sketchContext - Sketch 上下文对象
 * @returns {Object} 统计信息
 */
const getStylesStats = (sketchContext) => {
  return getStylesStatistics(sketchContext);
};

/**
 * 导出样式到剪贴板
 * @param {Object} sketchContext - Sketch 上下文对象
 * @returns {Object} 导出结果
 */
const exportStylesToClipboardFunc = (sketchContext) => {
  return exportStylesToClipboard(sketchContext);
};

// 保留原有的管理器类（向后兼容）
class OriginalStylesManager {
  constructor(context) {
    this.context = context;
  }

  getStyles() {
    return getSelectedLayerOriginalStyles(this.context);
  }

  exportToFile(options = {}) {
    return exportOriginalStyles(this.context, options);
  }

  exportToClipboard() {
    return exportStylesToClipboardFunc(this.context);
  }

  getStatistics() {
    return getStylesStatistics(this.context);
  }

  validateSelection() {
    return validateLayerSelection(this.context);
  }
}

const createOriginalStylesManager = (context) => {
  return new OriginalStylesManager(context);
};

/**
 * 完全自包含的原始样式处理函数
 * 在Sketch插件中直接调用，处理所有逻辑包括文件导出
 * @param {Object} sketch - Sketch API对象
 * @param {Object} fs - 文件系统模块
 * @param {Object} path - 路径模块
 * @returns {Object} 处理结果
 */
const processOriginalStyles = (sketch, fs, path) => {
  try {
    // 1. 获取当前文档和选择
    const document = sketch.getSelectedDocument();
    const selection = document.selectedLayers;

    if (!selection || selection.length === 0) {
      sketch.UI.message('请先选择一个编组或框架');
      return {
        success: false,
        error: '没有选中的图层'
      };
    }
    console.log('selection', selection.layers);
    

    // 2. 创建上下文对象
    const sketchContext = { selection };


    // 3. 一键获取并导出原始样式
    const result = getAndExportOriginalStyles(sketchContext);

    if (result.success) {
      // 4. 导出到插件根目录
      const filePath = path.join(process.cwd(), result.exportResult.fileName);
      fs.writeFileSync(filePath, result.exportResult.fileContent, 'utf8');

      // 5. 显示成功消息
      sketch.UI.message(`原始样式已导出到: ${result.exportResult.fileName}`);

      // 6. 输出统计信息
      console.log('导出统计:', {
        图层数量: result.statistics.layerCount,
        文件大小: result.statistics.dataSize + ' bytes',
        容器名称: result.statistics.containerName,
        容器类型: result.statistics.containerType
      });

      return {
        success: true,
        fileName: result.exportResult.fileName,
        statistics: result.statistics
      };
    } else {
      // 7. 显示错误消息
      sketch.UI.message('导出失败: ' + result.error);
      return {
        success: false,
        error: result.error
      };
    }

  } catch (error) {
    const errorMessage = '处理原始样式时发生错误: ' + error.message;
    sketch.UI.message(errorMessage);
    return {
      success: false,
      error: errorMessage
    };
  }
};

export {
  // 主要功能函数（推荐使用）
  getAndExportOriginalStyles,    // 一键获取并导出（完整流程）
  quickGetOriginalStyles,        // 快速获取样式
  quickExportStyles,             // 快速导出样式
  validateLayerSelection,        // 验证选择
  getStylesStats,                // 获取统计信息
  exportStylesToClipboardFunc,   // 导出到剪贴板
  processOriginalStyles,         // 完全自包含的处理函数

  // 向后兼容的函数
  OriginalStylesManager,
  createOriginalStylesManager,
  getSelectedLayerOriginalStyles,
  exportOriginalStyles,
  exportStylesToClipboard,
  getStylesStatistics
}; 