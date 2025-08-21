/**
 * 获取当前点击的编组或框架
 * @param {Object} context - Sketch 上下文对象
 * @param {Object} event - 点击事件对象
 * @returns {Object|null} 返回点击的图层对象，如果没有找到则返回 null
 */
const getClickedLayer = (context, event) => {
  try {
    // 获取当前选中的图层
    const selectedLayers = context.selection;
    
    if (!selectedLayers || selectedLayers.length === 0) {
      console.log('没有选中的图层');
      return null;
    }

    // 获取第一个选中的图层
    const clickedLayer = selectedLayers[0];
    
    // 检查是否为编组或框架
    if (clickedLayer && (clickedLayer.type === 'Group' || clickedLayer.type === 'Artboard')) {
      console.log('点击的图层类型:', clickedLayer.type);
      console.log('图层名称:', clickedLayer.name);
      return clickedLayer;
    }
    
    // 如果不是编组或框架，尝试查找父级编组或框架
    let parentLayer = clickedLayer.parent;
    while (parentLayer) {
      if (parentLayer.type === 'Group' || parentLayer.type === 'Artboard') {
        console.log('找到父级编组/框架:', parentLayer.name);
        return parentLayer;
      }
      parentLayer = parentLayer.parent;
    }
    
    console.log('未找到编组或框架');
    return null;
    
  } catch (error) {
    console.error('获取点击图层时出错:', error);
    return null;
  }
};

/**
 * 获取当前点击的编组或框架（包含详细信息）
 * @param {Object} context - Sketch 上下文对象
 * @param {Object} event - 点击事件对象
 * @returns {Object|null} 返回包含详细信息的图层对象
 */
const getClickedLayerWithDetails = (context, event) => {
  const layer = getClickedLayer(context, event);
  
  if (!layer) {
    return null;
  }
  
  // 返回包含详细信息的对象
  return {
    layer: layer,
    name: layer.name,
    type: layer.type,
    frame: layer.frame,
    layers: layer.layers || [],
    childCount: layer.layers ? layer.layers.length : 0,
    isGroup: layer.type === 'Group',
    isArtboard: layer.type === 'Artboard',
    // 获取子图层信息
    children: layer.layers ? layer.layers.map(child => ({
      name: child.name,
      type: child.type,
      frame: child.frame
    })) : []
  };
};

/**
 * 检查图层是否为容器类型（编组或框架）
 * @param {Object} layer - 图层对象
 * @returns {Boolean} 是否为容器类型
 */
const isContainerLayer = (layer) => {
  return layer && (layer.type === 'Group' || layer.type === 'Artboard');
};

export { getClickedLayer, getClickedLayerWithDetails, isContainerLayer }; 