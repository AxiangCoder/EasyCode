import sketch from 'sketch'
// documentation: https://developer.sketchapp.com/reference/api/
import { generateStyleTree } from './src/styleTree/generateStyleTree'
import fs from '@skpm/fs'
import path from '@skpm/path'
import { processOriginalStyles } from './src/originalStyles'
import { bordersToCss } from './sketchToCss/bordersToCss'
import test from './sketchToCss/test'
export default function () {
  /* const document = sketch.getSelectedDocument()
  const page = document.pages[0];
  const login = page.layers[0]

  console.log(login);
  
  
  
  const styleTree = generateStyleTree(login)

  // 导出到插件根目录
  const filePath = path.join(process.cwd(), 'styleTree.json')
  fs.writeFileSync(filePath, JSON.stringify(styleTree, null, 2), 'utf8') 
  sketch.UI.message('样式树已导出到插件目录 styleTree.json')
  */

  // 处理原始样式（所有逻辑都在 originalStyles 中完成）

  // processOriginalStyles(sketch, fs, path)
  test()
  
  console.log('end');
  
}