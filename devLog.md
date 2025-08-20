


## 2025.8.4
今天用的例子是区块链核验平台
目的，导出选中的编组，layer 或者 frame的原始样式及其子元素的样式

问题：在实践过程中，发现无法获取到选中的编组
已解决：document.selection获取的并不是一个数组，需要使用官方方法遍历取到
```js
selection.forEach(layer => log(layer.id))

selection.map(layer => layer.id)

selection.reduce((initial, layer) => {
  initial += layer.name
  return initial
}, '')
```


## 2025.8.5
今天已经成功使用这个方法，去创建 区块链核验平台 的登录表单
问题：
  1. 生成的样式和设计的样式不同，包括阴影不能正确识别
  2. 复杂样式的表单无法正确完成开发逻辑，需要写定

## 2025.8.11
今天发现一个问题，sketch 中的属性和 css 中的不一定能完全一一对应
现在需要一一处理的有：
1. blendingMode(混合模式，暂不处理)
2. blurs
3. fills
4. borders
5. shadows
6. corners对应的是border-radius
7. 布局方式

