# 快速部署指南

## 环境要求

- Python 3.10+
- 8GB+ RAM（用于加载embedding模型）
- DeepSeek API密钥

## 快速启动（5分钟）

### 1. 克隆仓库

```bash
git clone https://github.com/BallCard/ZJUHEX.git
cd ZJUHEX
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置API密钥

复制 `.env.example` 为 `.env`，并填入你的DeepSeek API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
DEEPSEEK_API_KEY=your_actual_key_here
```

### 4. 启动后端

```bash
cd src/backend
uvicorn main:app --reload --port 8000
```

后端服务运行在: http://localhost:8000

API文档: http://localhost:8000/docs

### 5. 打开前端

**方式1: 直接打开HTML文件**
```
在浏览器中打开: src/frontend/index.html
```

**方式2: 使用本地服务器（推荐）**
```bash
cd src/frontend
python -m http.server 3000
```
访问: http://localhost:3000

## 验证部署

### 测试后端API

```bash
# 测试根端点
curl http://localhost:8000/

# 预期输出:
# {"message":"Medical Textbook Knowledge Integration System","version":"1.0.0","status":"running"}
```

### 运行端到端测试

```bash
# 在项目根目录
python test_e2e.py
```

## 常见问题

### Q1: 后端启动失败 - "Field required: deepseek_api_key"

**原因**: 未配置.env文件或API密钥无效

**解决**:
1. 确认 `.env` 文件存在于项目根目录
2. 确认 `DEEPSEEK_API_KEY` 已正确填写
3. 重启后端服务

### Q2: 依赖安装失败

**原因**: pip版本过低或网络问题

**解决**:
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像（如果网络慢）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 前端无法连接后端

**原因**: 后端未启动或端口不匹配

**解决**:
1. 确认后端服务正在运行（访问 http://localhost:8000/docs）
2. 检查前端配置（默认连接 http://localhost:8000）
3. 检查防火墙设置

### Q4: 图谱无法渲染

**原因**: Cytoscape.js加载失败或数据格式错误

**解决**:
1. 检查浏览器控制台错误
2. 确认网络连接（Cytoscape.js从CDN加载）
3. 尝试刷新页面

## 生产部署建议

### 使用Gunicorn（生产环境）

```bash
pip install gunicorn

cd src/backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/ZJUHEX/src/frontend;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker部署（计划中）

```bash
# 构建镜像
docker build -t zjuhex .

# 运行容器
docker run -d -p 8000:8000 -p 3000:3000 --env-file .env zjuhex
```

## 性能优化

### 1. 预下载embedding模型

首次运行时会自动下载 `paraphrase-multilingual-MiniLM-L12-v2` 模型（约400MB）。

预下载：
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

### 2. 调整处理参数

编辑 `.env` 文件：
```env
# 增加处理块数（更完整的知识图谱，但更慢）
MAX_CHUNKS_DEFAULT=10

# 调整相似度阈值（更低=更多去重）
SIMILARITY_THRESHOLD=0.88
```

### 3. 使用GPU加速（可选）

```bash
# 安装GPU版本的FAISS
pip uninstall faiss-cpu
pip install faiss-gpu
```

## 监控和日志

### 查看日志

后端日志输出到控制台，格式：
```
2026-05-10 14:30:15 - parser - INFO - 开始解析PDF: 03_生理学.pdf
```

调整日志级别（`.env`）：
```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

### 监控API性能

访问 http://localhost:8000/docs 查看所有API端点和响应时间。

## 安全建议

1. **不要提交 `.env` 文件到Git**（已在.gitignore中排除）
2. **生产环境使用HTTPS**
3. **限制API访问频率**（可使用slowapi）
4. **定期更新依赖**：`pip list --outdated`

## 技术支持

- GitHub Issues: https://github.com/BallCard/ZJUHEX/issues
- 文档: `docs/` 目录
- 演示脚本: `docs/演示脚本.md`
- Agent架构说明: `docs/Agent架构说明.md`
