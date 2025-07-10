# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).

# Markdown文档查看器

这是一个使用Vue 3和Vite构建的Markdown文档查看器，支持实时预览、搜索和暗黑模式。文档通过静态文件方式访问，无需服务器支持。

## 🚀 核心特性

### 📁 智能文档管理架构
- **开发环境**：使用软连接（symlink）关联源文档，避免文件重复
- **构建环境**：自动复制文件到构建目录，确保部署正常
- **Git友好**：自动忽略生成的文档文件，保持仓库整洁

### 🔧 功能特点

- 📝 Markdown文档实时预览
- 🔍 文档搜索功能
- 🌓 暗黑模式支持
- 📱 响应式设计
- 🚀 静态文件访问，无需服务器
- 🔗 开发环境软连接，避免文件重复
- 📋 构建时自动复制，确保部署正常

## 📋 快速开始

### 安装依赖
```bash
npm install
```

### 开发模式（软连接）
```bash
npm run dev
```
开发模式会：
1. 🔗 创建软连接指向 `../advices/` 目录
2. 🧹 自动清理旧文件
3. 📝 生成文档列表（list.json）
4. 🚀 启动开发服务器

### 构建模式（文件复制）
```bash
npm run build
```
构建模式会：
1. 📋 复制实际文件到 public 目录
2. 📦 打包生产版本
3. 🎯 适用于部署环境

## 📂 项目架构

### 目录结构
```
docs-viewer/
├── public/
│   └── advices/                 # 文档目录 (Git忽略)
│       ├── list.json           # 自动生成的文档索引
│       └── *.md               # 软连接（开发）/ 复制文件（构建）
├── src/
│   ├── components/            # Vue组件
│   ├── App.vue               # 主应用
│   └── main.js               # 入口文件
├── scripts/
│   └── generate-list.js      # 智能文档处理脚本
└── package.json              # 项目配置
```

### 🔄 文档处理流程

#### 开发环境 (软连接模式)
```bash
# 自动检测开发环境
NODE_ENV=development npm run dev

# 或显式指定软连接模式
npm run generate-list:dev
```

#### 构建环境 (复制模式)
```bash
# 生产构建
npm run build

# 或显式指定复制模式
npm run generate-list:build
```

## 🛠️ 可用命令

| 命令 | 功能 | 模式 |
|------|------|------|
| `npm run dev` | 开发服务器 | 软连接 |
| `npm run build` | 生产构建 | 复制文件 |
| `npm run generate-list:dev` | 生成软连接 | 开发 |
| `npm run generate-list:build` | 复制文件 | 构建 |
| `npm run preview` | 预览构建结果 | - |
| `npm run clean` | 清理构建文件 | - |

## 🔧 工作机制

### 1. 开发环境 - 软连接模式
```bash
🔧 运行模式: 软连接模式 (开发)
🧹 清理现有目录...
🔗 创建软连接...
   ✓ advice_20250710_063327.md -> ../../../advices/advice_20250710_063327.md
✅ 软连接模式完成
```

**优势：**
- ✅ 无文件重复，节省存储空间
- ✅ 源文件修改立即生效
- ✅ Git 忽略生成文件，保持仓库整洁
- ✅ 开发效率高

### 2. 构建环境 - 复制模式
```bash
🔧 运行模式: 复制模式 (构建)
🧹 清理现有目录...
📋 复制文件...
   ✓ advice_20250710_063327.md
✅ 复制模式完成
```

**优势：**
- ✅ 确保部署环境文件完整
- ✅ 兼容所有托管平台
- ✅ 无依赖外部文件
- ✅ 构建产物自包含

## 📝 文档管理

### 添加新文档
1. 在 `../advices/` 目录下添加 `.md` 文件
2. 文件命名格式：`advice_YYYYMMDD_HHMMSS.md`
3. 运行 `npm run generate-list:dev` 更新列表

### 文档格式要求
- 使用标准 Markdown 语法
- UTF-8 编码
- 建议包含标题和结构化内容

## 🔍 Git 配置

项目已配置 `.gitignore` 忽略以下文件：
```gitignore
# Public advices directory (soft links and copied files)
public/advices/*.md
public/advices/list.json

# Soft links (开发环境软连接文件)
public/advices/advice_*.md
```

这确保了：
- ✅ 源文档仅在 `advices/` 目录存储一份
- ✅ 生成的软连接和复制文件不被 Git 追踪
- ✅ 仓库保持清洁，无重复文件

## 🚀 部署说明

### Vercel 部署

#### 自动部署
1. 连接 GitHub 仓库到 Vercel
2. 设置构建命令：`npm run build`
3. 设置输出目录：`dist`
4. 自动部署成功 ✅

#### 本地测试
```bash
npm run build
npm run preview
```

### 其他平台
构建后的 `dist` 目录可部署到任何静态托管平台：
- Netlify
- GitHub Pages  
- 腾讯云 COS
- 阿里云 OSS
- AWS S3

## 🐛 故障排除

### 1. 软连接创建失败
**现象**：开发模式下文档加载失败
**解决**：
```bash
# 检查源文件是否存在
ls ../advices/

# 重新生成软连接
npm run generate-list:dev
```

### 2. 文档列表未更新
**现象**：新文档不显示
**解决**：
```bash
# 手动更新列表
npm run generate-list:dev
```

### 3. 构建后文档缺失
**现象**：部署后无法访问文档
**解决**：
```bash
# 确保构建前复制文件
npm run generate-list:build
npm run build
```

### 4. 权限问题 (macOS/Linux)
**现象**：软连接创建失败
**解决**：
```bash
# 检查目录权限
chmod 755 docs-viewer/public/
chmod 755 advices/
```

## 📊 性能优化

### 开发环境
- 软连接避免文件复制，提升启动速度
- 实时文件同步，无需手动刷新
- 最小化 Git 操作，减少版本控制开销

### 生产环境  
- 文件复制确保完整性
- 静态资源优化
- CDN 友好的文件结构

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

注意：
- 请勿提交 `docs-viewer/public/advices/` 目录下的文件
- 新功能请添加相应测试
- 遵循现有代码风格

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

## 🎯 最佳实践总结

### ✅ 推荐的工作流程

1. **开发阶段**
   ```bash
   npm run dev  # 使用软连接，实时同步
   ```

2. **测试构建**  
   ```bash
   npm run build
   npm run preview
   ```

3. **部署发布**
   ```bash
   git push origin main  # 自动触发 Vercel 部署
   ```

### 🚫 避免的操作

- ❌ 手动复制文档到 `public/advices/`
- ❌ 提交生成的软连接文件到 Git
- ❌ 在生产环境使用软连接模式
- ❌ 忽略 `list.json` 的自动生成

这个架构既保证了开发效率，又确保了部署可靠性，完美解决了文档重复存储的问题！ 🎉
