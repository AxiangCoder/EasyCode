/**
 * 广度优先遍历图层 (Breadth-First Search)
 * @param {Array} layers - 起始图层数组
 * @param {Function} callback - 对每个图层执行的回调函数
 */
const traverseLayersBFS = (layers = [], callback) => {
  // 检查输入是否有效
  if (!Array.isArray(layers) || !layers.length) {
    return;
  }

  // 1. 初始化一个队列，并将起始图层放入
  const queue = [...layers]; 

  // 2. 当队列不为空时，循环处理
  while (queue.length > 0) {
    // 3. 从队列头部取出一个图层
    const currentLayer = queue.shift(); 
    
    // 4. 对当前图层执行回调
    callback(currentLayer);

    // 5. 如果该图层有子图层，将所有子图层加入队列尾部
    if (currentLayer.layers && currentLayer.layers.length) {
      queue.push(...currentLayer.layers);
    }
  }
};
