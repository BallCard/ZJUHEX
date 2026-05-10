# 学科知识整合智能体

AI全栈黑客松赛题项目 - 多教材知识整合系统

## 项目简介

本系统能够自动加载多本教材，构建知识图谱，识别跨教材的知识点重叠与互补，将内容整合压缩到不超过原始体量30%的精华版本，并提供基于RAG的精准问答功能。

## 功能特性

- ✅ 多格式教材加载（PDF/Markdown/TXT/DOCX）
- ✅ 知识图谱构建与可视化
- ✅ 跨教材知识整合与去重
- ✅ RAG精准问答（带引用来源）
- ✅ 多轮对话与迭代优化
- ✅ Web交互界面

## 技术栈

**后端**
- FastAPI - Web框架
- **MinerU (magic-pdf)** - 中文医学PDF解析（主引擎）
- Docling - PDF解析备用方案
- **BGE-M3 (FlagEmbedding)** - 多向量文本嵌入（dense+sparse+multi-vector）
- FAISS + BM25 - 混合检索（向量+关键词）
- LlamaIndex PropertyGraphIndex - 知识图谱构建
- LangGraph - Agent状态机编排
- text-dedup - MinHash去重
- LLMLingua - 动态压缩
- 通义千问/DeepSeek - 大模型调用

**前端**
- React + Ant Design - 前端框架
- Cytoscape.js - 知识图谱可视化（P0）
- AntV G6 - 高性能图谱可视化（P1优化）

## 环境依赖

- **Python 3.10+** (MinerU/Docling requirement)
- Node.js 16+

## 安装步骤

### 1. 克隆仓库

```bash
git clone <repository-url>
cd Hex
```

### 2. 后端环境配置

```bash
# 激活虚拟环境
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 下载BGE-M3模型（首次运行自动下载，也可预先下载）
python -c "from FlagEmbedding import BGEM3FlagModel; BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)"
```

### 3. 前端环境配置

```bash
cd src/frontend
npm install
```

### 4. 配置环境变量

创建 `.env` 文件：

```env
# LLM API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# 或使用国内API
DASHSCOPE_API_KEY=your_dashscope_key  # 通义千问
DEEPSEEK_API_KEY=your_deepseek_key

# 向量数据库配置
VECTOR_DB_PATH=./data/vector_db
```

## 运行命令

### 启动后端服务

```bash
cd src/backend
python main.py
# 或
uvicorn main:app --reload --port 8000
```

后端服务运行在 `http://localhost:8000`

### 启动前端服务

```bash
cd src/frontend
npm run dev
```

前端服务运行在 `http://localhost:3000`

## 使用说明

1. **上传教材**：在左侧教材管理区上传PDF/MD/TXT等格式的教材文件
2. **构建图谱**：系统自动解析教材并构建知识图谱
3. **查看可视化**：在中间区域查看知识图谱，支持缩放、拖拽、点击查看详情
4. **整合教材**：系统自动识别重复知识点并进行整合
5. **RAG问答**：在右侧问答区输入问题，获得带引用来源的回答
6. **多轮对话**：通过对话修改整合决策

## 项目结构

```
Hex/
├── .gitignore
├── README.md
├── requirements.txt
├── docs/
│   ├── 需求分析.md
│   ├── 系统设计.md
│   └── Agent架构说明.md
├── src/
│   ├── backend/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   └── models/
│   └── frontend/
│       ├── package.json
│       └── src/
├── report/
│   └── 整合报告.md
├── data/
│   └── textbooks/
└── textbooks/  # 测试教材（不上传到GitHub）
```

## 开发文档

详细的开发文档请查看：
- [需求分析](docs/需求分析.md)
- [系统设计](docs/系统设计.md)
- [Agent架构说明](docs/Agent架构说明.md)

## 部署

### Docker部署（推荐）

```bash
docker-compose up -d
```

### 魔搭创空间部署

参考 `deploy/` 目录下的部署脚本。

## 测试数据

本项目使用7本医学教材作为测试数据：
1. 局部解剖学
2. 组织学与胚胎学
3. 生理学
4. 医学微生物学
5. 病理学
6. 传染病学
7. 病理生理学

**注意**：教材PDF文件不包含在仓库中，需要单独上传。

## 许可证

MIT License

## 联系方式

- 作者：[Your Name]
- 学号：[Your Student ID]
- GitHub：[Repository URL]
- 部署链接：[Deployment URL]
