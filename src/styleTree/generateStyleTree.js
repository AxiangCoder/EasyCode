import getCurrentStyle from './getCurrentStyle'
import { getFlexLayoutStyle } from './getFlexLayoutStyle'
import { getGridLayoutStyle } from './getGridLayoutStyle'

const generateStyleTree = (currentLayer, parentLayoutType = 'block', parentSize = null) => {
  // 当前节点尺寸
  const currentSize = currentLayer.frame
    ? { width: currentLayer.frame.width, height: currentLayer.frame.height }
    : parentSize;
    
    

  // 叶子节点（无子 layers）
  if (!currentLayer.layers) {
    // mode 控制宽高类型，flexMode 下传递 parentSize
    const style = getCurrentStyle(
      currentLayer,
      {
        flexMode: parentLayoutType === 'flex',
        parentSize: parentLayoutType === 'flex' ? parentSize : null
      }
    );
    return {
      style,
      children: []
    }
  }
  
  // 容器节点
  const { layers } = currentLayer;
  const xList = layers.map(layer => layer.frame.x);
  const yList = layers.map(layer => layer.frame.y);
  const uniqueXList = [...new Set(xList)].sort((a, b) => a - b);
  const uniqueYList = [...new Set(yList)].sort((a, b) => a - b);
  const columnCount = uniqueXList.length;
  const rowCount = uniqueYList.length;

  let style, layoutType;
  if (columnCount > 1 && rowCount > 1) {
    style = getGridLayoutStyle(layers, uniqueXList, uniqueYList);
    layoutType = 'grid';
  } else {
    style = getFlexLayoutStyle(currentLayer, getCurrentStyle(currentLayer, { flexMode: parentLayoutType === 'flex', parentSize: parentSize }), columnCount, rowCount);
    layoutType = 'flex';
  }

  // 递归处理子节点，先按 x 升序，再按 y 升序
  const sortedLayers = [...layers].sort((a, b) => {
    if (a.frame.x !== b.frame.x) {
      return a.frame.x - b.frame.x;
    }
    return a.frame.y - b.frame.y;
  });
  const children = sortedLayers.map(child => generateStyleTree(child, layoutType, currentSize));

  return {
    style,
    children
  }
}

export { generateStyleTree };