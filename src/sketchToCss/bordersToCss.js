/**
 * 将Sketch图层的边框属性转换为Tailwind CSS风格的字符串
 * @param {Object} layer - Sketch图层对象（Layer, Group, Artboard, Shape, Image, Text等）
 * @returns {string} Tailwind CSS风格的边框样式字符串
 */
const bordersToCss = (layer) => {
  if (!layer || !layer.style || !layer.style.borders) {
    return '';
  }

  const borders = layer.style.borders;
  if (!Array.isArray(borders) || borders.length === 0) {
    return '';
  }

  // 获取第一个边框（Sketch通常只使用第一个边框）
  const border = borders[0];
  if (!border || !border.isEnabled) {
    return '';
  }

  const cssClasses = [];

  // 边框宽度
  if (border.thickness && border.thickness > 0) {
    const thickness = Math.round(border.thickness);
    cssClasses.push(`border-[${thickness}px]`);
  } else {
    cssClasses.push('border-0');
  }

  // 边框样式
  cssClasses.push('border-solid'); // Sketch默认使用实线边框

  // 边框颜色
  if (border.color) {
    const { red, green, blue, alpha } = border.color;
    if (red !== undefined && green !== undefined && blue !== undefined) {
      // 转换为RGB值（0-255）
      const r = Math.round(red * 255);
      const g = Math.round(green * 255);
      const b = Math.round(blue * 255);
      
      if (alpha !== undefined && alpha < 1) {
        // 有透明度，使用rgba
        const a = Math.round(alpha * 100) / 100; // 保留两位小数
        cssClasses.push(`border-[rgba(${r},${g},${b},${a})]`);
      } else {
        // 无透明度，使用rgb
        cssClasses.push(`border-[rgb(${r},${g},${b})]`);
      }
    }
  } else {
    // 默认黑色边框
    cssClasses.push('border-black');
  }

  // 边框位置（Sketch的边框位置）
  if (border.position) {
    switch (border.position) {
      case 'Inside':
        // Tailwind CSS默认是外边框，Inside需要特殊处理
        cssClasses.push('border-inset');
        break;
      case 'Center':
        // 居中边框，Tailwind CSS默认行为
        break;
      case 'Outside':
        // 外边框，Tailwind CSS默认行为
        break;
      default:
        // 默认居中
        break;
    }
  }

  return cssClasses.join(' ');
};

export default bordersToCss;
