# 快速部署指南

## 环境要求

- Node.js 20+
- Python 3.10+ (仅后端需要)
- 8GB+ RAM (用于embedding模型)

## 快速启动

### 1. 克隆仓库

```bash
git clone https://github.com/BallCard/ZJUHEX.git
cd ZJUHEX
```

### 2. 安装前端依赖

```bash
cd src/frontend_new
npm install
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

## 自动部署 (GitHub Actions)

项目配置了完整的CI/CD流程，推送到main/master分支自动触发：

### 流水线阶段

1. **Frontend Lint & Type Check** - TypeScript类型检查
2. **Frontend Build** - 构建生产版本
3. **Backend Tests** - Python单元测试
4. **Deploy to GitHub Pages** - 自动部署前端
5. **Post-Deploy Smoke Test** - 验证部署成功
6. **E2E Tests** (可选) - 端到端测试

### 触发条件

- Push到main/master分支
- Pull Request到main/master分支
- 手动触发 (workflow_dispatch)
- 定时触发 (schedule)

### 查看部署状态

访问 GitHub仓库的 Actions 标签页查看流水线状态。

## 生产环境部署

### GitHub Pages (当前配置)

推送到main/master分支后自动部署到GitHub Pages。

前端构建产物部署到 `src/frontend_new/dist/`。

### 手动部署

```bash
cd src/frontend_new
npm run build
# 构建产物在 dist/ 目录
```

### Vercel/Netlify

```bash
# Vercel
vercel --prod

# Netlify
netlify deploy --prod
```

## 常见问题

### Q1: npm install 失败

```bash
# 清理缓存
rm -rf node_modules package-lock.json
npm install
```

### Q2: 构建失败

```bash
# 检查TypeScript错误
npm run lint
```

### Q3: GitHub Pages 部署失败

1. 检查仓库Settings > Pages > Source配置
2. 确认workflow有pages:write权限
3. 查看Actions日志定位问题

## 技术栈

### 前端 (src/frontend_new)
- **Framework**: React 19 + TypeScript
- **Build**: Vite 6
- **Styling**: Tailwind CSS 4
- **Graph**: Cytoscape.js
- **Animation**: Framer Motion

### 后端 (src/backend) - 已废弃
- **Framework**: FastAPI
- **PDF解析**: PyMuPDF
- **向量检索**: FAISS
- **LLM**: DeepSeek API