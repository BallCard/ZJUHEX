# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI全栈黑客松 - 学科知识整合智能体**

开发一个AI智能体，对7本医学教材进行知识整合：构建可视化知识图谱、跨教材去重提纯、RAG精准问答。

**核心目标**：将7本教材压缩到不超过原始体量30%的精华版本，且教学效果不打折。

**比赛时长**：5小时

## 核心功能模块

1. **多格式教材加载**：PDF/MD/TXT/DOCX解析，章节结构识别
2. **知识图谱构建**：LLM提取知识点，识别关系（前置依赖、并列、包含、应用）
3. **知识图谱可视化**：交互式图谱（点击、缩放、拖拽、搜索）
4. **跨教材整合**：语义对齐，去重提纯，压缩比≤30%
5. **RAG问答**：文档分块→向量嵌入→检索→带引用来源的回答
6. **多轮对话**：教师通过对话修改整合决策
7. **Web界面**：SPA单页应用

## Development Setup

### Environment Setup

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Backend (FastAPI)
cd src/backend
uvicorn main:app --reload --port 8000

# Frontend
cd src/frontend
npm run dev
```

## Project Structure

```
Hex/
├── src/
│   ├── backend/          # FastAPI后端
│   │   ├── main.py       # 主入口
│   │   ├── api/          # API路由
│   │   ├── services/     # 业务逻辑
│   │   │   ├── parser.py       # 文档解析
│   │   │   ├── knowledge_graph.py  # 知识图谱构建
│   │   │   ├── integration.py      # 跨教材整合
│   │   │   └── rag.py              # RAG问答
│   │   └── models/       # 数据模型
│   └── frontend/         # React/Vue前端
├── docs/                 # 开发文档
│   ├── 需求分析.md
│   ├── 系统设计.md
│   └── Agent架构说明.md
├── report/               # 整合报告
└── data/                 # 数据目录
    └── textbooks/        # 教材文件（不上传GitHub）
```

## Key Technical Decisions

### 1. 文档解析策略
- PDF：PyMuPDF，章节识别通过字体大小+正则匹配
- 分块大小：500-800字，重叠50-100字

### 2. 知识图谱构建
- LLM提取：每章节单独调用，输出JSON格式
- 关系类型：prerequisite（前置依赖）、parallel（并列）、contains（包含）、applies_to（应用）

### 3. 语义对齐算法
- 方案1：Embedding相似度（快速，阈值0.85+）
- 方案2：LLM判断（准确，成本高）
- 推荐：两种结合（先Embedding筛选，再LLM确认）

### 4. RAG Pipeline
- Embedding模型：sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2 或 BGE-small-zh)
- 向量数据库：FAISS（轻量）或ChromaDB
- 检索：top-5相关chunk
- 加分项：混合检索（向量+BM25）+ Rerank

### 5. Agent架构
- 需在`docs/Agent架构说明.md`中详细论证设计决策
- 评分看合理性和论证深度，不看Agent数量

## API Endpoints

```
POST /api/upload          # 上传教材文件
POST /api/parse           # 解析教材
POST /api/build_graph     # 构建知识图谱
POST /api/integrate       # 跨教材整合
POST /api/rag/index       # 建立向量索引
POST /api/rag/query       # RAG问答
POST /api/chat            # 多轮对话
GET  /api/report          # 获取整合报告
```

## Development Guidelines

### 代码规范
- 使用类型注解（Python typing）
- 函数拆分合理，单一职责
- 关键逻辑添加注释
- 错误处理完善

### 文档要求
- 每个功能模块需在`docs/系统设计.md`中说明技术选型理由
- Agent架构必须在`docs/Agent架构说明.md`中论证设计决策
- 整合报告需包含：压缩比、决策摘要、典型案例、教学完整性说明

### 测试数据
- 7本医学教材位于`textbooks/`目录
- 教材不上传GitHub（已在.gitignore中排除）
- 系统需支持前端上传教材文件

## Evaluation Criteria (100分)

- A. 文档完整性与可复现性：15分
- B. 功能实现完整度：25分
- C. 知识图谱可视化创新性：13分
- D. Agent架构设计：20分（核心评分点）
- E. 代码质量与工程规范：17分
- F. 创新与自由发挥：10分

## Important Notes

- **压缩比控制**：整合后内容≤原始总字数的30%
- **RAG引用**：每个回答必须附带来源（教材名、章节、页码）
- **Agent架构文档**：必须包含架构总览、设计决策论证、数据流、取舍权衡
- **部署要求**：必须提供公网可访问的部署链接
- **提交物**：GitHub仓库链接 + 在线部署链接

## Time Allocation (5小时)

- 前30分钟：搭建项目骨架
- 第1-3小时：实现P0功能（优先级：文件解析→图谱构建→RAG→对话）
- 第3-4小时：写文档（Agent架构说明 > 需求分析 > 整合报告 > README）
- 第4-4.5小时：部署上线
- 最后30分钟：检查提交、查缺补漏

## Useful Commands

```bash
# 测试PDF解析
python -c "import fitz; doc = fitz.open('textbooks/03_生理学.pdf'); print(len(doc))"

# 测试向量检索
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'); print('OK')"

# 启动开发服务器
uvicorn src.backend.main:app --reload --port 8000
```

## References

- 赛题文档：`第一届AI全栈黑客松赛题.pdf`
- 赛题总结：`赛题总结.md`
- 教材目录：`textbooks/`（7本医学教材）

