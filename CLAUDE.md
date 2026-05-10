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

# Install dependencies (P0 minimal stack)
pip install -r requirements.txt

# Configure API keys
# Create .env file with:
# DEEPSEEK_API_KEY=your_key_here
```

### Running the Application

```bash
# Backend (FastAPI)
cd src/backend
uvicorn main:app --reload --port 8000

# Frontend (P0: Single HTML file)
# Open src/frontend/index.html in browser
```

## Project Structure

```
Hex/
├── src/
│   ├── backend/          # FastAPI后端
│   │   ├── main.py       # 主入口 + API路由
│   │   └── services/     # 业务逻辑
│   │       ├── parser.py           # 文档解析 (MinerU)
│   │       ├── knowledge_graph.py  # 知识图谱构建 (LLM提取)
│   │       ├── integration.py      # 去重整合 (sentence-transformers)
│   │       ├── report_generator.py # 整合报告生成
│   │       └── rag.py              # RAG问答 (FAISS + citations)
│   └── frontend/         # 前端
│       └── index.html    # P0: 单HTML文件 (Cytoscape.js)
├── docs/                 # 开发文档
│   ├── mvp-p0-implementation-plan.md  # 实施计划 (已优化)
│   ├── Agent架构说明.md               # 架构设计 (20分关键)
│   ├── 系统设计.md
│   ├── 需求分析.md
│   └── 开发日志.md                    # 过程性总结
├── report/               # 整合报告输出目录
│   └── 整合报告_{job_id}.md
├── data/
│   ├── textbooks/        # 教材文件（不上传GitHub）
│   └── runtime/          # 运行时状态
│       └── jobs/{job_id}/  # 每个任务的状态目录
│           ├── parsed_chunks.json
│           ├── knowledge_graph.json
│           ├── deduplicated_graph.json
│           ├── faiss.index
│           └── chunks_for_rag.json
└── 开发哲学.md           # 方法论约束
```

## Key Technical Decisions

### 1. P0 Scope Reduction (Based on Third-Party Review)
- **Demo target**: Single textbook (`03_生理学.pdf`) or first 20 pages
- **Rationale**: 5-hour constraint + empty codebase → prove concept with 1 textbook, document 7-textbook as P1
- **Impact**: Compression ratio still calculated, but on single-textbook deduplication

### 2. 文档解析策略
- **P0**: MinerU (magic-pdf) for Chinese medical PDFs
- **Fallback**: PyMuPDF if MinerU fails
- **Chunking**: Simple paragraph-based splitting (500-800 chars)

### 3. 知识图谱构建
- **P0**: Custom JSON structure (nodes + edges), no heavy framework
- **LLM提取**: Process first 10 chunks for demo (time constraint)
- **P1**: LlamaIndex PropertyGraphIndex + CMeKG alignment

### 4. 语义对齐算法
- **P0**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2) + cosine similarity
- **Threshold**: 0.90 (biomedical domain best practice)
- **P1**: MinHash + BGE-M3 + SemHash multi-stage pipeline

### 5. 压缩策略 (Critical - Addresses Review Finding 2)
- **P0**: Output real integrated content to `report/整合报告.md`
- **Calculation**: (整合后字数 / 原始字数) × 100% ≤ 30%
- **NOT**: Dynamic prompt compression (that's RAG optimization, not deliverable compression)

### 6. RAG Pipeline
- **P0**: FAISS vector-only retrieval (top-3)
- **Embedding**: sentence-transformers (same as deduplication)
- **Citations**: Manual tracking via chunk metadata (textbook, page, content)
- **P1**: BM25 + vector hybrid + bge-reranker-v2-m3 + Judge Model verification

### 7. 状态管理 (Addresses Review Finding 4)
- **P0**: Filesystem-based job directories (`data/runtime/jobs/{job_id}/`)
- **Rationale**: Zero dependencies, full traceability, easy debugging
- **P1**: PostgreSQL/MongoDB for production

### 8. Agent架构
- **P0**: Sequential pipeline (single-agent)
- **Rationale**: Time constraint + reliability > parallelism
- **P1**: LangGraph state machine + multi-agent (CrewAI/AutoGen)
- **Documentation**: Must explain design decisions in `docs/Agent架构说明.md` (20分关键)

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

- **P0 Demo Scope**: Single textbook (`03_生理学.pdf`) end-to-end pipeline
- **压缩比控制**: 整合后内容≤原始总字数的30%，输出到 `report/整合报告.md`
- **RAG引用**: 每个回答必须附带来源（教材名、章节、页码）
- **Agent架构文档**: 必须包含架构总览、设计决策论证、数据流、取舍权衡（20分关键）
- **状态持久化**: 所有中间结果保存到 `data/runtime/jobs/{job_id}/`
- **部署要求**: P0使用uvicorn直接运行，P1考虑Docker
- **提交物**: GitHub仓库链接 + 在线部署链接（如时间允许）

## Execution Philosophy (Human-in-Progress Mode)

### 三方约束
1. **开发哲学** (`开发哲学.md`): 闭环优先、可见输出、知道什么不做
2. **赛题要求**: 5小时、压缩≤30%、Agent架构20分
3. **第三方Review**: P0范围收缩、真实压缩比、状态持久化、安全上传

### 自驱动执行协议
- **严格按plan执行**: `docs/mvp-p0-implementation-plan.md` Phases 0-9
- **Checkpoint验证**: 每个Phase完成后必须通过验证命令
- **系统性调试**: 遇到bug >10min使用systematic-debugging skill
- **人工介入门槛**: 仅在blocked >15min、关键决策冲突、高风险操作时汇报
- **过程性总结**: 每个Phase完成后更新 `docs/开发日志.md`

### Multi-Agent协作
- **并行机会**: Frontend可在Backend Phase 6-8时并行开发
- **Review机会**: Phase 8完成后spawn review agent检查代码质量
- **文档机会**: Phase 8-9时并行编写Agent架构说明.md

### 验证标准
- **Minimum Viable Demo**: Upload → Parse → Graph → Dedup → Report (压缩比≤30%) → RAG (带引用)
- **文档完整性**: Agent架构说明.md + 开发日志.md + README.md
- **可演示性**: 至少一个textbook完整流程可演示

## Time Allocation (5小时)

**优化后时间表** (基于三方约束):

```
00:00-00:05  Phase 0: 预检查
00:05-00:20  Phase 1: 环境配置
00:20-00:50  Phase 2: 文档解析 (30min)
00:50-01:30  Phase 3: 知识图谱构建 (40min)
01:30-02:00  Phase 4: 去重整合 (30min)
02:00-02:25  Phase 5: 报告生成 (25min)
02:25-03:05  Phase 6: RAG流水线 (40min)
03:05-03:25  Phase 7: 可视化 (20min)
03:25-04:00  Phase 8: API端点 (35min)
04:00-04:20  Phase 9: 前端 (20min)
04:20-04:30  端到端测试 (10min)
---
04:30-05:00  调试缓冲 (30min)
```

**关键路径**: Parse → Graph → Dedup → Report (压缩比证明) + RAG (引用证明) + 可演示界面

**如果时间紧张**: 可砍Phase 7可视化（用JSON展示），可砍Phase 9前端（用curl演示API），但**绝不能砍**Report生成（压缩比是核心要求）

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

