
/**
 * 将 Sketch 图层的边框样式转换为 Tailwind CSS 类名
 * @param {Object} layer - Sketch 图层对象
 * @returns {string} - Tailwind CSS 类名字符串
 */
/**
 * 将 Sketch 图层的边框样式转换为 Tailwind CSS 类名
 * @param {Object} layer - Sketch 图层对象
 * @returns {string} - Tailwind CSS 类名字符串
 */
const bordersToCss = (layer) => {
  // 检查是否有样式和边框
  if (!layer.style?.borders || layer.style.borders.length === 0) {
    return '';
  }

  const classes = [];
  
  // 获取第一个边框样式
  const border = layer.style.borders[0];
  
  // 检查边框是否启用
  if (!border.enabled) {
    return '';
  }

  // 处理边框宽度
  const borderWidth = Math.round(border.thickness);
  if (borderWidth > 0) {
    // 处理边框位置
    if (border.position === 'Inside') {
      classes.push('border-inset');
    }
    classes.push(`border-[${borderWidth}px]`);
  }

  // 处理边框颜色
  if (border.color) {
    const color = border.color.toLowerCase();
    
    // 检查颜色是否包含透明度（8位十六进制）
    if (color.length === 9) {  // 例如 #3a5bcde0
      // 提取颜色部分（不包含透明度）
      const colorHex = color.slice(0, 7);
      // 提取透明度
      const alpha = parseInt(color.slice(7), 16) / 255;
      
      // 添加边框颜色
      classes.push(`border-[${colorHex}]`);

      // 只有当透明度不是 100% 时才添加透明度类
      if (alpha < 1) {
        classes.push(`border-opacity-[${Math.round(alpha * 100)}]`);
      }
    } else {  // 6位十六进制颜色（无透明度）
      classes.push(`border-[${color}]`);
    }
  }

  // 处理边框样式
  if (border.fillType === 'Color') {
    classes.push('border-solid');
  }

  // 处理圆角
  // 从 borderOptions 中获取圆角信息
  if (layer.style.borderOptions?.lineJoin === 'Round') {
    classes.push('rounded');
  }

  return classes.join(' ');
};

export default bordersToCss;
