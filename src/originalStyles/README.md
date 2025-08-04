# 原始样式获取和导出工具

这个目录包含了用于获取和导出Sketch图层原始样式的工具函数。

## 功能特性

- 🔍 **获取原始样式**：提取图层的所有原始样式属性
- 📁 **JSON导出**：将样式数据导出为JSON格式
- 📋 **剪贴板导出**：快速复制样式数据到剪贴板
- 📊 **统计分析**：提供样式数据的统计信息
- 🎯 **智能检测**：自动识别编组和框架容器

## 文件结构

```
originalStyles/
├── getOriginalStyles.js    # 核心样式获取函数
├── exportStyles.js         # 样式导出工具
├── index.js               # 主入口文件
└── README.md              # 使用说明
```

## 使用方法

### 1. 基本使用

```javascript
import { getOriginalStyles } from './originalStyles';

// 获取当前选中图层的原始样式
const styles = getOriginalStyles(context);
console.log(styles);
```

### 2. 使用管理器类

```javascript
import { createOriginalStylesManager } from './originalStyles';

// 创建管理器实例
const manager = createOriginalStylesManager(context);

// 获取样式
const styles = manager.getStyles();

// 导出到文件
const result = manager.exportToFile({
  includeMetadata: true,
  format: 'pretty'
});

// 导出到剪贴板
const clipboardResult = manager.exportToClipboard();

// 获取统计信息
const stats = manager.getStatistics();

// 快速导出（自动选择最佳方式）
const quickResult = manager.quickExport();
```

### 3. 验证选择

```javascript
const validation = manager.validateSelection();
if (validation.valid) {
  console.log('选择有效:', validation.message);
} else {
  console.log('选择无效:', validation.message);
}
```

## 导出的样式数据格式

### 基本结构

```json
{
  "container": {
    "id": "layer-id",
    "name": "容器名称",
    "type": "Group",
    "frame": {
      "x": 0,
      "y": 0,
      "width": 100,
      "height": 100
    },
    "style": {
      "fills": [...],
      "borders": [...],
      "shadows": [...],
      "innerShadows": [...],
      "textStyle": {...},
      "blur": {...},
      "blendMode": "Normal",
      "opacity": 1
    }
  },
  "children": [
    // 子图层的样式数据
  ],
  "metadata": {
    "totalLayers": 5,
    "layerTypes": {
      "Shape": 2,
      "Text": 3
    },
    "timestamp": "2024-01-01T00:00:00.000Z"
  }
}
```

### 支持的样式属性

- **填充 (Fills)**：颜色、渐变、图案、噪点
- **边框 (Borders)**：颜色、粗细、位置
- **阴影 (Shadows)**：外阴影和内阴影
- **文本样式 (Text Styles)**：字体、大小、行高、字间距
- **模糊效果 (Blur)**：高斯模糊、动感模糊
- **混合模式 (Blend Mode)**：图层混合模式
- **透明度 (Opacity)**：图层透明度

## API 参考

### OriginalStylesManager 类

#### 构造函数
- `constructor(context)` - 创建管理器实例

#### 方法
- `getStyles()` - 获取原始样式数据
- `exportToFile(options)` - 导出到JSON文件
- `exportToClipboard()` - 导出到剪贴板
- `getStatistics()` - 获取统计信息
- `quickExport()` - 快速导出
- `validateSelection()` - 验证选择

### 便捷函数

- `getOriginalStyles(context)` - 直接获取样式
- `exportStyles(context, options)` - 直接导出样式
- `createOriginalStylesManager(context)` - 创建管理器

## 使用场景

1. **设计系统分析**：提取组件的原始样式用于设计系统构建
2. **样式迁移**：将Sketch样式迁移到其他设计工具
3. **代码生成**：基于原始样式生成CSS代码
4. **样式审计**：分析设计文件的样式使用情况
5. **版本对比**：比较不同版本的样式差异

## 注意事项

- 确保在Sketch插件环境中使用
- 需要有效的图层选择才能获取样式数据
- 大型文件可能需要较长的处理时间
- 某些复杂的样式效果可能无法完全提取

## 错误处理

所有函数都包含错误处理机制，返回的结果对象包含：
- `success`: 操作是否成功
- `error`: 错误信息（如果失败）
- `timestamp`: 操作时间戳

```javascript
const result = manager.getStyles();
if (!result.error) {
  // 处理成功结果
} else {
  console.error('错误:', result.error);
}
``` 