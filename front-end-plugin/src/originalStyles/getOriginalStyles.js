/**
 * 获取图层的原始样式属性
 * @param {Object} layer - Sketch 图层对象
 * @returns {Object} 包含所有原始样式属性的对象
 */
import path from '@skpm/path'

const getLayerOriginalStyles = (layer) => {
  if (!layer) {
    return null;
  }

  const styles = {
    // 基本信息
    id: layer.id,
    name: layer.name,
    type: layer.type,
    
    // 位置和尺寸
    frame: layer.frame ? {
      x: layer.frame.x,
      y: layer.frame.y,
      width: layer.frame.width,
      height: layer.frame.height
    } : null,
    
    // 变换属性
    transform: layer.transform ? {
      rotation: layer.transform.rotation,
      flippedHorizontally: layer.transform.flippedHorizontally,
      flippedVertically: layer.transform.flippedVertically
    } : null,
    
    // 样式属性
    style: {}
  };
  console.log(layer.name);
  if (layer.name === '矩形') {
    console.log('====================', layer.name);
    console.log(JSON.stringify (layer));
    console.log('====================', layer.name);

    
  }

  // 填充样式
  if (layer.style && layer.style.fills) {
    styles.style.fills = layer.style.fills.map(fill => ({
      fillType: fill.fillType,
      color: fill.color ? {
        red: fill.color.red,
        green: fill.color.green,
        blue: fill.color.blue,
        alpha: fill.color.alpha
      } : null,
      gradient: fill.gradient,
      pattern: fill.pattern,
      noiseIndex: fill.noiseIndex,
      noiseIntensity: fill.noiseIntensity,
      isEnabled: fill.isEnabled
    }));
  }

  // 边框样式
  if (layer.style && layer.style.borders) {
    styles.style.borders = layer.style.borders.map(border => ({
      fillType: border.fillType,
      color: border.color ? {
        red: border.color.red,
        green: border.color.green,
        blue: border.color.blue,
        alpha: border.color.alpha
      } : null,
      thickness: border.thickness,
      position: border.position,
      isEnabled: border.isEnabled
    }));
  }

  // 阴影样式
  if (layer.style && layer.style.shadows) {
    styles.style.shadows = layer.style.shadows.map(shadow => ({
      color: shadow.color ? {
        red: shadow.color.red,
        green: shadow.color.green,
        blue: shadow.color.blue,
        alpha: shadow.color.alpha
      } : null,
      offsetX: shadow.offsetX,
      offsetY: shadow.offsetY,
      blurRadius: shadow.blurRadius,
      spread: shadow.spread,
      isEnabled: shadow.isEnabled
    }));
  }

  // 内阴影样式
  if (layer.style && layer.style.innerShadows) {
    styles.style.innerShadows = layer.style.innerShadows.map(shadow => ({
      color: shadow.color ? {
        red: shadow.color.red,
        green: shadow.color.green,
        blue: shadow.color.blue,
        alpha: shadow.color.alpha
      } : null,
      offsetX: shadow.offsetX,
      offsetY: shadow.offsetY,
      blurRadius: shadow.blurRadius,
      spread: shadow.spread,
      isEnabled: shadow.isEnabled
    }));
  }

  // 文本样式（仅对文本图层）
  if (layer.type === 'Text' && layer.style && layer.style.textStyle) {
    styles.style.textStyle = {
      fontName: layer.style.textStyle.fontName,
      fontSize: layer.style.textStyle.fontSize,
      lineHeight: layer.style.textStyle.lineHeight,
      letterSpacing: layer.style.textStyle.letterSpacing,
      textAlign: layer.style.textStyle.textAlign,
      color: layer.style.textStyle.color ? {
        red: layer.style.textStyle.color.red,
        green: layer.style.textStyle.color.green,
        blue: layer.style.textStyle.color.blue,
        alpha: layer.style.textStyle.color.alpha
      } : null
    };
  }

  // 模糊效果
  if (layer.style && layer.style.blur) {
    styles.style.blur = {
      type: layer.style.blur.type,
      radius: layer.style.blur.radius,
      center: layer.style.blur.center,
      motionAngle: layer.style.blur.motionAngle,
      isEnabled: layer.style.blur.isEnabled
    };
  }

  // 混合模式
  if (layer.style && layer.style.blendMode) {
    styles.style.blendMode = layer.style.blendMode;
  }

  // 透明度
  if (layer.style && layer.style.opacity !== undefined) {
    styles.style.opacity = layer.style.opacity;
  }

  return styles;
};

/**
 * 递归获取容器及其所有子元素的原始样式
 * @param {Object} container - 容器图层（编组或框架）
 * @returns {Object} 包含容器和所有子元素样式的对象
 */
const getContainerOriginalStyles = (container) => {
  if (!container) {
    return null;
  }
  console.log(1);
  
  const result = {
    id: container.id,
    name: container.name,
    type: container.type,
    frame: container.frame ? {
      x: container.frame.x,
      y: container.frame.y,
      width: container.frame.width,
      height: container.frame.height
    } : null,
    style: getLayerOriginalStyles(container).style,
    children: [],
    metadata: {
      totalLayers: 0,
      layerTypes: {},
      timestamp: new Date().toISOString()
    }
  };
  
  console.log(2);
  // 递归处理子图层
  if (container.layers && container.layers.length > 0) {
    result.children = container.layers.map(child => {
      // 统计图层类型
      if (child.type) {
        result.metadata.layerTypes[child.type] = (result.metadata.layerTypes[child.type] || 0) + 1;
      }
      result.metadata.totalLayers++;
      
      // 递归处理子元素：如果子元素也是容器，则递归获取其子元素
      if (child.type === 'Group' || child.type === 'Artboard') {
        return getContainerOriginalStyles(child);
      } else {
        // 叶子节点：返回完整的图层信息
        return {
          id: child.id,
          name: child.name,
          type: child.type,
          frame: child.frame ? {
            x: child.frame.x,
            y: child.frame.y,
            width: child.frame.width,
            height: child.frame.height
          } : null,
          style: getLayerOriginalStyles(child).style,
          children: [] // 叶子节点没有子元素
        };
      }
    });
  }

  return result;
};

/**
 * 获取当前选中图层的原始样式（JSON格式）
 * @param {Object} context - Sketch 上下文对象
 * @returns {Object} 包含原始样式的JSON对象
 */
const getSelectedLayerOriginalStyles = (context) => {
  const selectedLayers = context.selection;
  
  if (!selectedLayers || selectedLayers.length === 0) {
    throw new Error('没有选中的图层');
  }

  // 使用 forEach 获取第一个选中的图层
  let clickedLayer = null;
  selectedLayers.forEach(layer => {
    if (!clickedLayer) {
      clickedLayer = layer;
    }
  });

  // 检查第一个元素是否存在
  if (!clickedLayer) {
    throw new Error('选中的图层无效或为空');
  }
  
  // 检查是否为容器类型
  if (clickedLayer.type === 'Group' || clickedLayer.type === 'Artboard') {
    return getContainerOriginalStyles(clickedLayer);
  }
  
  // 如果不是容器，查找父级容器
  let parentLayer = clickedLayer.parent;
  while (parentLayer) {
    if (parentLayer.type === 'Group' || parentLayer.type === 'Artboard') {
      return getContainerOriginalStyles(parentLayer);
    }
    parentLayer = parentLayer.parent;
  }
  
  // 如果都没有找到容器，返回单个图层的样式（也支持递归）
  return {
    id: clickedLayer.id,
    name: clickedLayer.name,
    type: clickedLayer.type,
    frame: clickedLayer.frame ? {
      x: clickedLayer.frame.x,
      y: clickedLayer.frame.y,
      width: clickedLayer.frame.width,
      height: clickedLayer.frame.height
    } : null,
    style: getLayerOriginalStyles(clickedLayer).style,
    children: clickedLayer.layers && clickedLayer.layers.length > 0 ? 
      clickedLayer.layers.map(child => {
        if (child.type === 'Group' || child.type === 'Artboard') {
          return getContainerOriginalStyles(child);
        } else {
          return {
            id: child.id,
            name: child.name,
            type: child.type,
            frame: child.frame ? {
              x: child.frame.x,
              y: child.frame.y,
              width: child.frame.width,
              height: child.frame.height
            } : null,
            style: getLayerOriginalStyles(child).style,
            children: []
          };
        }
      }) : [],
    note: '单个图层样式',
    timestamp: new Date().toISOString()
  };
};

/**
 * 递归打印图层结构（用于调试）
 * @param {Object} node - 图层节点
 * @param {number} depth - 当前深度
 */
const debugPrintLayerStructure = (node, depth = 0) => {
  const indent = '  '.repeat(depth);
  console.log(`${indent}${node.type}: ${node.name} (${node.children ? node.children.length : 0} children)`);
  
  if (node.children && node.children.length > 0) {
    node.children.forEach(child => {
      debugPrintLayerStructure(child, depth + 1);
    });
  }
};

export { 
  getLayerOriginalStyles, 
  getContainerOriginalStyles, 
  getSelectedLayerOriginalStyles,
  debugPrintLayerStructure
}; 