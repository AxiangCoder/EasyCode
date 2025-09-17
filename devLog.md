## 2025.8.4

今天用的例子是区块链核验平台
目的，导出选中的编组，layer 或者 frame 的原始样式及其子元素的样式

问题：在实践过程中，发现无法获取到选中的编组
已解决：document.selection 获取的并不是一个数组，需要使用官方方法遍历取到

```js
selection.forEach(layer => log(layer.id));

selection.map(layer => layer.id);

selection.reduce((initial, layer) => {
  initial += layer.name;
  return initial;
}, '');
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
6. corners 对应的是 border-radius
7. 布局方式

## 2025.8.16

已经完成 border 的开发及单元测试，但是多了个问题，圆角无法识别，在测试中，我设置了圆角，但是没有 corners 属性

1. blendingMode(混合模式，暂不处理)
2. blurs
3. fills
4. borders（已完成）
5. shadows
6. corners 对应的是 border-radius
7. 布局方式

问题：

1. 思路错了，不应该是通过插件的形式来处理，应该直接将 .sketch 文件进行解压，然后根据 json 来进行样式布局
2. document.json 对应的应该是获取插件中的 document 文档
3. document.json 中 的 page 字段，对应的应该是 pages 目录下的 json 文件，这个目录下的 json 文件应该是只有一个

## 2025.8.21

今天转变思路，将之前开发的东西，作为 _src 来备份，新的 src 中，将采用服务端的开发方式，模拟从前端接收到 .skecth 文件中的 page.json, 并解析该文件，需要保留之前开发的 sketchToCss 目录，及 utils/exportToJson

以后，front-end-plugin 为插件开发，service 为服务器解析开发


## 2025.9.16
简单布局及所有元素都显示出来 完成
todo：
1. 移动端适配
2. PC 端大屏和中屏自适应
3. 绝对定位到底是 写 left 还是 right，top 还是 buttom
4. flex 布局和离散元素的判断还是有点问题
5. 还未测试grid 布局
7. 椭圆形元素现在还是方形
8. 单页面dsl 到项目dsl 组装
