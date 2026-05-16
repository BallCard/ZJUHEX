# 部署指南

## 环境要求

- Node.js 20+
- Python 3.10+ (仅后端需要)
- 8GB+ RAM (用于embedding模型)

---

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

---

## CI/CD 自动部署 (GitHub Actions)

项目配置了完整的 CI/CD 流水线，推送到 `main`/`master` 分支自动触发：

### 流水线阶段

| 阶段 | 说明 | 触发条件 |
|------|------|----------|
| **Frontend Lint & Type Check** | TypeScript 类型检查 | Push/PR |
| **Frontend Build** | Vite 生产构建 | Push/PR |
| **Backend Tests** | Python pytest 单元测试 | Push/PR |
| **Deploy to GitHub Pages** | 自动部署前端到 Pages | Push main/master |
| **Post-Deploy Smoke Test** | 验证部署站点可访问 | 部署完成后 |
| **E2E Tests** | Playwright 端到端测试 | 定时/手动触发 |

### 触发条件

- Push 到 `main` 或 `master` 分支
- Pull Request 到 `main` 或 `master`
- 手动触发 (`workflow_dispatch`)
- 每周日定时触发 (`schedule`)

### 所需 Secrets

在 GitHub 仓库 Settings → Secrets and variables → Actions 中配置：

| Secret | 说明 | 必需 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥（后端测试） | 是 |

### 查看部署状态

访问 GitHub 仓库的 Actions 标签页查看流水线状态。

---

## 生产环境部署

### GitHub Pages（当前配置）

推送到 `main`/`master` 分支后自动部署前端到 GitHub Pages。

**部署地址**: `https://BallCard.github.io/ZJUHEX`

### Railway（后端 API）

后端通过 Railway 部署，配置在 `railway.json` 和 `Procfile` 中。

```bash
# 部署到 Railway
# 1. 在 Railway 中关联 GitHub 仓库
# 2. 添加环境变量 DEEPSEEK_API_KEY
# 3. 自动部署
```

### 手动构建

```bash
cd src/frontend_new
npm run build
# 构建产物在 dist/ 目录
```

### Vercel / Netlify

```bash
# Vercel
vercel --prod

# Netlify
netlify deploy --prod --dir=src/frontend_new/dist
```

---

## 本地测试

### 运行前端构建

```bash
cd src/frontend_new
npm run build      # 生产构建
npm run lint       # TypeScript 类型检查
```

### 运行 E2E 测试

```bash
cd src/frontend_new
npx playwright install --with-deps chromium
npm run test       # 运行所有 E2E 测试
```

### 运行后端测试

```bash
pip install pytest
pytest tests/ -v --tb=short
```

---

## 常见问题

### Q1: npm install 失败

```bash
# 清理缓存
rm -rf node_modules package-lock.json
npm install
```

### Q2: 构建失败

```bash
# 检查 TypeScript 错误
npm run lint
```

### Q3: GitHub Pages 部署失败

1. 检查仓库 Settings → Pages → Source 为 "GitHub Actions"
2. 确认 workflow 有 `pages:write` 和 `id-token:write` 权限
3. 查看 Actions 日志定位问题

### Q4: Playwright 测试失败

```bash
# 重新安装浏览器
npx playwright install --with-deps chromium
```

---

## 技术栈

### 前端 (src/frontend_new)
- **Framework**: React 19 + TypeScript
- **Build**: Vite 6
- **Styling**: Tailwind CSS 4
- **Graph**: Cytoscape.js
- **Animation**: Framer Motion
- **Testing**: Playwright

### 后端 (src/backend)
- **Framework**: FastAPI
- **PDF 解析**: PyMuPDF
- **向量检索**: FAISS
- **LLM**: DeepSeek API

### CI/CD
- **Platform**: GitHub Actions
- **Deploy**: GitHub Pages (前端)
- **Testing**: Playwright (E2E), pytest (后端)
