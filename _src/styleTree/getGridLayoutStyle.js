
function getGridLayoutStyle(layers, uniqueXList, uniqueYList) {
  const layout = { display: 'grid' };

  // 从第一行的图层计算 grid-template-columns
  const firstRowLayers = layers
    .filter(layer => layer.frame.y === uniqueYList[0])
    .sort((a, b) => a.frame.x - b.frame.x);
  layout.gridTemplateColumns = firstRowLayers
    .map(layer => `${layer.frame.width}px`)
    .join(' ');

  // 从第一列的图层计算 grid-template-rows
  const firstColLayers = layers
    .filter(layer => layer.frame.x === uniqueXList[0])
    .sort((a, b) => a.frame.y - b.frame.y);
  layout.gridTemplateRows = firstColLayers
    .map(layer => `${layer.frame.height}px`)
    .join(' ');

  // 计算行列间距
  const columnGap = firstRowLayers.length > 1
    ? firstRowLayers[1].frame.x - (firstRowLayers[0].frame.x + firstRowLayers[0].frame.width)
    : 0;
  const rowGap = firstColLayers.length > 1
    ? firstColLayers[1].frame.y - (firstColLayers[0].frame.y + firstColLayers[0].frame.height)
    : 0;

  if (rowGap === columnGap) {
    layout.gap = `${rowGap}px`;
  } else {
    layout.gap = `${rowGap}px ${columnGap}px`;
  }

  return layout;
}

export {
  getGridLayoutStyle
}