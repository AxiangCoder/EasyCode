### **核心文档和页面属性**

* `_class`: 对象的类型标识，此处的 `"page"` 表明这是一个 Sketch 页面对象。
* `do_objectID`: 对象的唯一标识符（ID），用于在整个 Sketch 文档中引用和追踪此页面。
* `name`: 页面在 Sketch 软件中显示的名称，例如 `"页面 1"`。
* `nameIsFixed`: 布尔值，表示页面名称是否被锁定，无法在软件界面中更改。
* `frame`: 页面在画布上的位置和大小。对于页面本身，`x` 和 `y` 通常为 0，`width` 和 `height` 也会被忽略，因为页面大小由其内容决定。
    * `_class`: 字段类型，这里是 `"rect"`（矩形）。
    * `constrainProportions`: 布尔值，是否锁定长宽比。
    * `height`, `width`, `x`, `y`: 高度、宽度、x 坐标和 y 坐标。
* `layers`: 页面上所有子图层的数组。这是页面最重要的部分，它定义了画布上的所有内容。每个子图层都是一个对象，有自己的一套属性。

---

### **通用图层属性 (页面和子图层共享)**

<!-- * `booleanOperation`: 布尔运算类型。通常用于形状合并，`-1` 表示没有布尔运算。 -->
<!-- * `isFixedToViewport`: 布尔值，图层在滚动时是否固定在视口中。 -->
<!-- * `isFlippedHorizontal`, `isFlippedVertical`: 布尔值，图层是否水平或垂直翻转。 -->
<!-- * `isLocked`: 布尔值，图层在软件中是否被锁定。 -->
<!-- * `isTemplate`: 布尔值，是否为模板图层。 -->
* `isVisible`: 布尔值，图层是否可见。
<!-- * `hasCustomPrototypeVisibility`: 布尔值，是否自定义了原型可见性。 -->
* `hasExplicitConstraints`: 布尔值，是否具有明确的布局约束。
* `horizontalSizing`, `verticalSizing`: 定义图层在父容器改变大小时如何调整水平和垂直尺寸。
* `horizontalPins`, `verticalPins`: 描述图层固定的水平和垂直边缘。
* `prototypeVisibility`: 原型可见性设置。
* `resizingConstraint`: 整数，将水平和垂直的尺寸调整约束编码为一个值。
* `resizingType`: 尺寸调整类型，`0` 表示无调整。
* `rotation`: 图层的旋转角度。
* `shouldBreakMaskChain`: 布尔值，是否中断蒙版链。
* `exportOptions`: 导出选项，定义了图层的导出格式、比例等。
    * `_class`: 类型 `"exportOptions"`。
    * `exportFormats`: 导出格式数组，包含文件格式 (`png`、`jpg` 等) 和缩放比例 (`@1x`)。

---

### **样式和外观属性**

* `style`: 描述图层外观样式的一个对象，包含以下子字段：
    * `_class`: 类型 `"style"`。
    * `blurs`: 模糊效果数组。
    * `borders`: 描边样式数组。
    * `fills`: 填充样式数组。对于 `group` 类型的图层，它定义了背景填充。
        * `isEnabled`: 布尔值，填充是否启用。
        * `fillType`: 填充类型，`0` 为纯色填充，`1` 为渐变。
        * `color`: 颜色对象，由 `red`、`green`、`blue` 和 `alpha` (透明度) 四个分量组成，取值范围是 0 到 1。
    * `contextSettings`: 上下文设置，如混合模式 (`blendMode`) 和不透明度 (`opacity`)。
    * `shadows`: 阴影效果数组。
    * `endMarkerType`, `miterLimit`, `startMarkerType`, `windingRule`: 矢量路径和描边相关的属性。
    * `borderOptions`: 描边选项，如虚线样式 (`dashPattern`) 和线帽样式 (`lineCapStyle`)。

---

### **编组 (Group) 和形状 (Rectangle) 特有属性**

在 `layers` 数组中，您可以看到一个 `_class` 为 `"group"` 的对象，它代表一个编组。这个编组内部又包含了三个 `_class` 为 `"rectangle"` 的对象。

#### **编组 (Group) 属性**

* `resizesContent`: 布尔值，编组的尺寸是否随其子内容自动调整。
* `hasBackgroundColor`: 布尔值，编组是否具有背景色。
* `backgroundColor`: 如果 `hasBackgroundColor` 为 `true`，此字段定义背景颜色。
* `hasClickThrough`: 布尔值，鼠标事件是否能穿透编组作用于其内部图层。

#### **矩形 (Rectangle) 属性**

* `edited`: 布尔值，是否被编辑过。
* `isClosed`: 布尔值，路径是否闭合。
* `pointRadiusBehaviour`: 点半径行为。
* `points`: 形状的顶点数组。每个点都包含坐标 (`point`)、圆角半径 (`cornerRadius`) 和曲线信息 (`curveFrom`, `curveTo`)。
* `needsConvertionToNewRoundCorners`, `hasConvertedToNewRoundCorners`: 布尔值，与旧版 Sketch 的圆角处理方式兼容性相关。

---

### **辅助和布局属性**

* `clippingMaskMode`, `hasClippingMask`: 剪裁蒙版设置。
* `groupLayout`: 编组内的布局方式。`MSImmutableFreeformGroupLayout` 表示自由布局。
* `horizontalRulerData`, `verticalRulerData`: 标尺数据，包含基准位置和辅助线 (`guides`)。
* `prototypeViewport`: 原型视口设置，定义了原型预览的设备或屏幕尺寸。

总而言之，这个 JSON 文件是一个完整的、可机器读取的页面描述，它精确地记录了设计文件中的每个视觉元素及其所有属性，使得 Sketch 文件的版本控制、自动化处理和第三方集成成为可能。