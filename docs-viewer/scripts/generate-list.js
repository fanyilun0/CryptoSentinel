import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// 获取当前文件的目录路径
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 检查命令行参数或环境变量来决定模式
const args = process.argv.slice(2);
const isDev = args.includes('--dev') || process.env.NODE_ENV === 'development';
const isSymlink = args.includes('--symlink') || isDev;

// 源目录和目标目录
const sourceDir = path.join(__dirname, '../../advices');
const targetDir = path.join(__dirname, '../public/advices');

console.log(`🔧 运行模式: ${isSymlink ? '软连接模式 (开发)' : '复制模式 (构建)'}`);

// 清理目标目录（如果存在）
if (fs.existsSync(targetDir)) {
  console.log('🧹 清理现有目录...');
  fs.rmSync(targetDir, { recursive: true, force: true });
}

// 确保目标目录存在
fs.mkdirSync(targetDir, { recursive: true });

// 读取源目录中的所有 .md 文件
const files = fs.readdirSync(sourceDir)
  .filter(file => file.endsWith('.md'))
  .map(file => ({
    name: file,
    title: file.replace('.md', '').replace(/_/g, ' ')
  }))
  .sort((a, b) => b.name.localeCompare(a.name)); // 按文件名降序排序

// 生成 list.json
const listJson = {
  files: files,
  generated: new Date().toISOString(),
  mode: isSymlink ? 'symlink' : 'copy'
};

// 写入 list.json
fs.writeFileSync(
  path.join(targetDir, 'list.json'),
  JSON.stringify(listJson, null, 2)
);

if (isSymlink) {
  // 开发模式：创建软连接
  console.log('🔗 创建软连接...');
  files.forEach(file => {
    const sourceFile = path.join(sourceDir, file.name);
    const targetFile = path.join(targetDir, file.name);
    
    try {
      // 创建相对路径的软连接
      const relativePath = path.relative(path.dirname(targetFile), sourceFile);
      fs.symlinkSync(relativePath, targetFile, 'file');
      console.log(`   ✓ ${file.name} -> ${relativePath}`);
    } catch (error) {
      console.warn(`   ⚠️ 软连接创建失败 ${file.name}:`, error.message);
      // 如果软连接失败，回退到复制
      fs.copyFileSync(sourceFile, targetFile);
      console.log(`   📋 回退到复制模式: ${file.name}`);
    }
  });
  console.log(`✅ 软连接模式完成，处理了 ${files.length} 个文件`);
} else {
  // 构建模式：复制文件
  console.log('📋 复制文件...');
  files.forEach(file => {
    const sourceFile = path.join(sourceDir, file.name);
    const targetFile = path.join(targetDir, file.name);
    fs.copyFileSync(sourceFile, targetFile);
    console.log(`   ✓ ${file.name}`);
  });
  console.log(`✅ 复制模式完成，处理了 ${files.length} 个文件`);
} 