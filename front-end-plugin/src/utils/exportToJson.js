import fs from '@skpm/fs'
import path from '@skpm/path'
const exportToJson = (data, fileName) => {
  try {
    const filePath = path.join(process.cwd(), fileName);
    if (typeof data === 'string')
      return fs.writeFileSync(filePath, data, 'utf8');
    return fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
  } catch (error) {
    console.error(error);
  }
}

export default exportToJson;