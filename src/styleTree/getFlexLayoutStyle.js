function getFlexLayoutStyle(currentLayer, layout = {}, columnCount, rowCount) {
  const children = currentLayer.layers;
  const parentFrame = currentLayer.frame;

  // 生成的布局对象
  const genLayout = { display: 'flex' };

  // 计算 padding
  const leftPadding = Math.min(...children.map(l => l.frame.x - parentFrame.x));
  const topPadding = Math.min(...children.map(l => l.frame.y - parentFrame.y));
  const rightPadding = Math.min(...children.map(l => (parentFrame.x + parentFrame.width) - (l.frame.x + l.frame.width)));
  const bottomPadding = Math.min(...children.map(l => (parentFrame.y + parentFrame.height) - (l.frame.y + l.frame.height)));
  genLayout.padding = `${topPadding}px ${rightPadding}px ${bottomPadding}px ${leftPadding}px`;

  // 只有一行，是水平 Flex
  if (rowCount === 1) {
    genLayout.flexDirection = 'row';
    const sortedLayers = [...children].sort((a, b) => a.frame.x - b.frame.x);
    let gap = 0;
    if (sortedLayers.length > 1) {
      gap = sortedLayers[1].frame.x - (sortedLayers[0].frame.x + sortedLayers[0].frame.width);
      // 百分比方式
      gap = parentFrame.width > 0 ? (gap / parentFrame.width) * 100 : 0;
      genLayout.gap = `${gap.toFixed(2)}%`;
    } else {
      genLayout.gap = '0%';
    }

    // 推断 justify-content
    const first = sortedLayers[0];
    const last = sortedLayers[sortedLayers.length - 1];
    const spaceLeft = first.frame.x - parentFrame.x;
    const spaceRight = (parentFrame.x + parentFrame.width) - (last.frame.x + last.frame.width);
    if (spaceLeft === 0 && spaceRight === 0) {
      genLayout.justifyContent = 'space-between';
    } else if (spaceLeft === 0) {
      genLayout.justifyContent = 'flex-start';
    } else if (spaceRight === 0) {
      genLayout.justifyContent = 'flex-end';
    } else {
      // 有 padding 时，居中处理
      genLayout.justifyContent = 'center';
    }

    // 推断 align-items
    const yList = sortedLayers.map(l => l.frame.y);
    const minY = Math.min(...yList);
    const maxY = Math.max(...yList);
    if (minY === maxY && minY === parentFrame.y + topPadding) {
      genLayout.alignItems = 'flex-start';
    } else if (minY === maxY && minY === parentFrame.y + parentFrame.height - sortedLayers[0].frame.height - bottomPadding) {
      genLayout.alignItems = 'flex-end';
    } else {
      // 居中或拉伸
      genLayout.alignItems = 'center';
    }
  }
  // 只有一列，是垂直 Flex
  else {
    genLayout.flexDirection = 'column';
    const sortedLayers = [...children].sort((a, b) => a.frame.y - b.frame.y);
    let gap = 0;
    if (sortedLayers.length > 1) {
      gap = sortedLayers[1].frame.y - (sortedLayers[0].frame.y + sortedLayers[0].frame.height);
      // 百分比方式
      gap = parentFrame.height > 0 ? (gap / parentFrame.height) * 100 : 0;
      genLayout.gap = `${gap.toFixed(2)}%`;
    } else {
      genLayout.gap = '0%';
    }

    // 推断 justify-content
    const first = sortedLayers[0];
    const last = sortedLayers[sortedLayers.length - 1];
    const totalChildrenHeight = sortedLayers.reduce((sum, l) => sum + l.frame.height, 0) + (sortedLayers.length - 1) * (parentFrame.height * gap / 100);
    const spaceTop = first.frame.y - parentFrame.y;
    const spaceBottom = (parentFrame.y + parentFrame.height) - (last.frame.y + last.frame.height);
    if (spaceTop === 0 && spaceBottom === 0) {
      genLayout.justifyContent = 'space-between';
    } else if (spaceTop === 0) {
      genLayout.justifyContent = 'flex-start';
    } else if (spaceBottom === 0) {
      genLayout.justifyContent = 'flex-end';
    } else {
      // 有 padding 时，居中处理
      genLayout.justifyContent = 'center';
    }

    // 推断 align-items
    const xList = sortedLayers.map(l => l.frame.x);
    const minX = Math.min(...xList);
    const maxX = Math.max(...xList);
    if (minX === maxX && minX === parentFrame.x + leftPadding) {
      genLayout.alignItems = 'flex-start';
    } else if (minX === maxX && minX === parentFrame.x + parentFrame.width - sortedLayers[0].frame.width - rightPadding) {
      genLayout.alignItems = 'flex-end';
    } else {
      genLayout.alignItems = 'center';
    }
  }

  // children 字段，长度为 columnCount * rowCount，每个元素为 { flex: '1 1 auto' }
  const expectedChildrenCount = columnCount * rowCount;
  const childrenLayouts = [];
  for (let i = 0; i < expectedChildrenCount; i++) {
    childrenLayouts.push({ flex: '1 1 auto' });
  }
  genLayout.children = childrenLayouts;

  // 合并传入 layout，传入 layout 优先级高
  return { ...genLayout, ...layout };
}

export {
  getFlexLayoutStyle
}