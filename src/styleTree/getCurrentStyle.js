function getCurrentStyle(layer, options = {}) {
  if (!layer) return {};
  const style = layer.style || {};
  const css = {
    name: layer.name
  };
  const flexMode = options.flexMode === true;
  const parentSize = options.parentSize;

  // 1. frame 相关
  if (typeof layer.name === 'string' && layer.name.startsWith('/')) {
    // 页面级组件，宽高 100%，不管 flexMode
    css.width = '100%';
    css.height = '100%';
  } else if (layer.frame) {
    if (flexMode && parentSize && parentSize.width && parentSize.height) {
      css.maxWidth = ((layer.frame.width / parentSize.width) * 100).toFixed(2) + '%';
      css.maxHeight = ((layer.frame.height / parentSize.height) * 100).toFixed(2) + '%';
      css.flex = '1 1 auto';
      css.alignSelf = 'stretch';
    } else if (flexMode) {
      css.maxWidth = layer.frame.width + 'px';
      css.maxHeight = layer.frame.height + 'px';
      css.flex = '1 1 auto';
      css.alignSelf = 'stretch';
    } else {
      css.width = layer.frame.width + 'px';
      css.height = layer.frame.height + 'px';
    }
  }

  // 2. 通用样式
  if (typeof layer.opacity === 'number') {
    css.opacity = layer.opacity;
  }
  if (typeof layer.rotation === 'number' && layer.rotation !== 0) {
    css.transform = `rotate(${layer.rotation}deg)`;
  }

  // 3. 填充（只取第一个 enabled 的 fill）
  if (style.fills && style.fills.length > 0) {
    const fill = style.fills.find(f => f.enabled && f.fillType === 'Color');
    if (fill) {
      css.backgroundColor = fill.color;
    }
  }

  // 4. 边框（只取第一个 enabled 的 border）
  if (style.borders && style.borders.length > 0) {
    const border = style.borders.find(b => b.enabled);
    if (border) {
      css.borderWidth = border.thickness + 'px';
      css.borderColor = border.color;
      css.borderStyle = 'solid';
    }
  }

  // 5. 圆角
  if (typeof style.borderRadius === 'number' && style.borderRadius > 0) {
    css.borderRadius = style.borderRadius + 'px';
  }

  // 6. 阴影（只取第一个 enabled 的 shadow）
  if (style.shadows && style.shadows.length > 0) {
    const shadow = style.shadows.find(s => s.enabled);
    if (shadow) {
      css.boxShadow = `${shadow.offsetX}px ${shadow.offsetY}px ${shadow.blurRadius}px ${shadow.spread || 0}px ${shadow.color}`;
    }
  }

  // 7. 文本样式
  if (layer.type === 'Text' && layer.style) {
    if (layer.style.fontSize) css.fontSize = layer.style.fontSize + 'px';
    if (layer.style.fontFamily) css.fontFamily = layer.style.fontFamily;
    if (layer.style.textColor) css.color = layer.style.textColor;
    if (layer.style.fontWeight) css.fontWeight = layer.style.fontWeight;
    if (layer.style.lineHeight) css.lineHeight = layer.style.lineHeight + 'px';
    if (layer.style.letterSpacing) css.letterSpacing = layer.style.letterSpacing + 'px';
    if (layer.style.textAlign) css.textAlign = layer.style.textAlign;
  }

  // 8. 类型标记
  if (layer.type === 'Image' || layer.type === 'Bitmap') {
    css.type = 'img';
  } else {
    css.type = 'ele';
  }

  return css;
}

export default getCurrentStyle;
