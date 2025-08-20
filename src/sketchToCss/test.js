import sketch from 'sketch'
import bordersToCss from './bordersToCss'
import exportToJson from '../utils/exportToJson'



const iterate = (item, callback) => {
  let children = []
  if (item.layers.length > 0) {
    children = item.layers.map(layer => {
      return iterate(layer, callback)
    })
  }
  return {
    name: item.name,
    style: {
      ...callback(item),
    },
    children
  };
}
const test = () => {
  const document = sketch.getSelectedDocument()
  const page = document.pages[0];
  exportToJson(page, 'page.json');
  const style = iterate(page, (layer) => {
    return {
      border: bordersToCss(layer)
    }
  })
  exportToJson(style, 'style.json');

}



export default test;

