import sketch from 'sketch'
// documentation: https://developer.sketchapp.com/reference/api/
import { generateStyleTree } from './styleTree/generateStyleTree'
import fs from '@skpm/fs'
import path from '@skpm/path'

export default function () {
  const document = sketch.getSelectedDocument()
  const page = document.pages[0];
  const login = page.layers[0]
  
  const styleTree = generateStyleTree(login)

  // 导出到插件根目录
  const filePath = path.join(process.cwd(), 'styleTree.json')
  fs.writeFileSync(filePath, JSON.stringify(styleTree, null, 2), 'utf8')

  sketch.UI.message('样式树已导出到插件目录 styleTree.json')
}