# 学科知识整合智能体

AI全栈黑客松赛题项目 - 医学教材知识整合系统

## 项目简介

本系统能够自动加载医学教材，构建知识图谱，识别知识点重叠与互补，将内容整合压缩到不超过原始体量30%的精华版本，并提供基于RAG的精准问答功能。

**当前版本**: P2 (v2.0) - 完整功能版本

**核心能力**:
- 单教材知识整合（P0/P1）
- 跨教材知识对齐与去重（P2）
- 交互式知识图谱可视化（P2）
- 配置化系统设计（P2）

## 功能特性

### 核心功能
- ✅ PDF教材解析（PyMuPDF）
- ✅ 知识图谱构建（LLM提取）
- ✅ 语义去重整合（sentence-transformers + 余弦相似度0.90）
- ✅ 压缩比计算（≤30%目标）
- ✅ RAG精准问答（FAISS + DeepSeek，带引用来源）
- ✅ 整合报告生成（Markdown格式）

### P2新增功能
- ✅ **跨教材整合**: 支持多教材上传和跨教材语义对齐
- ✅ **知识图谱可视化**: Cytoscape.js交互式图谱（点击、缩放、拖拽）
- ✅ **配置化设计**: 所有参数可通过.env配置
- ✅ **并发安全**: 文件锁保护状态更新
- ✅ **统一日志**: logging模块统一日志格式
- ✅ **输入验证**: 关键参数范围校验

### Web界面
- ✅ 单教材/跨教材模式切换
- ✅ 多文件上传支持
- ✅ 实时进度显示
- ✅ 交互式图谱可视化
- ✅ 节点详情查看

## 技术栈

**后端**
- FastAPI - Web框架
- PyMuPDF (fitz) - PDF解析
- sentence-transformers - 语义嵌入 (paraphrase-multilingual-MiniLM-L12-v2)
- FAISS - 向量检索
- DeepSeek API - LLM知识提取和问答生成

**前端**
- 单HTML文件 - 无构建步骤
- 原生JavaScript - Fetch API
- Cytoscape.js - 知识图谱可视化
- 响应式CSS - 渐变紫色主题

## 环境依赖

- **Python 3.10+**
- DeepSeek API密钥

## 快速开始

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
```

### 3. 配置环境变量

编辑 `.env` 文件：

```env
# API Configuration
DEEPSEEK_API_KEY=your_key_here
```

### 4. 启动后端服务

```bash
cd src/backend
uvicorn main:app --reload --port 8000
```

后端服务运行在 `http://localhost:8000`

API文档: `http://localhost:8000/docs`

### 5. 启动前端

直接在浏览器中打开:
```
src/frontend/index.html
```

或使用本地服务器:
```bash
cd src/frontend
python -m http.server 3000
```

前端运行在 `http://localhost:3000`

## 使用说明

### 单教材模式

1. **选择模式**: 选择"单教材模式"
2. **上传教材**: 点击上传区域，选择单个PDF文件
3. **运行流水线**: 点击"运行整合流水线"按钮
   - 解析文档 → 构建知识图谱 → 去重整合 → 生成报告 → 建立RAG索引
4. **查看图谱**: 点击"查看知识图谱"，交互式浏览知识结构
5. **查看报告**: 点击"查看报告"查看详细整合报告
6. **知识问答**: 输入问题，系统返回带引用来源的回答

### 跨教材整合模式

1. **选择模式**: 选择"跨教材整合模式"
2. **上传教材**: 点击上传区域，选择多个PDF文件（2-7本）
3. **运行流水线**: 点击"运行跨教材整合流水线"按钮
   - 解析所有教材 → 构建各教材图谱 → 跨教材语义对齐 → 生成整合报告
4. **查看图谱**: 查看跨教材整合后的知识图谱（节点标注来源教材）
5. **查看报告**: 查看跨教材整合报告（包含各教材贡献度、重复知识点、互补知识点）

### 图谱交互

- **缩放**: 鼠标滚轮缩放图谱
- **拖拽**: 拖拽节点调整布局
- **点击节点**: 查看节点详情（定义、来源、关联节点）
- **搜索**: 搜索框快速定位知识点
- **布局切换**: 切换不同布局算法（cose、circle、grid）

## 项目结构

```
Hex/
├── src/
│   ├── backend/
│   │   ├── main.py              # FastAPI主应用
│   │   └── services/
│   │       ├── parser.py        # 文档解析
│   │       ├── knowledge_graph.py  # 知识图谱构建
│   │       ├── integration.py   # 去重整合
│   │       ├── report_generator.py  # 报告生成
│   │       └── rag.py           # RAG问答
│   └── frontend/
│       └── index.html           # 单页应用
├── data/
│   ├── textbooks/               # 教材文件（需手动添加）
│   └── runtime/jobs/{job_id}/   # 运行时状态
├── report/                      # 整合报告输出
├── docs/                        # 开发文档
│   ├── mvp-p0-implementation-plan.md
│   ├── Agent架构说明.md
│   └── 开发日志.md
└── requirements.txt             # Python依赖
```

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
### 单教材端点
| `/api/upload` | POST | 上传教材文件 |
| `/api/parse/{job_id}` | POST | 解析文档 |
| `/api/build_graph/{job_id}` | POST | 构建知识图谱 |
| `/api/integrate/{job_id}` | POST | 去重整合 |
| `/api/generate_report/{job_id}` | POST | 生成报告 |
| `/api/rag/index/{job_id}` | POST | 建立RAG索引 |
| `/api/rag/query/{job_id}` | POST | RAG问答 |
| `/api/status/{job_id}` | GET | 查询任务状态 |
| `/api/report/{job_id}` | GET | 获取报告内容 |
| `/api/graph/{job_id}` | GET | 获取图谱数据 |

### 跨教材端点（P2新增）
| `/api/upload_multiple` | POST | 上传多个教材文件 |
| `/api/parse_multiple/{job_id}` | POST | 解析所有教材 |
| `/api/build_graphs_multiple/{job_id}` | POST | 构建所有教材图谱 |
| `/api/cross_integrate/{job_id}` | POST | 跨教材整合 |
| `/api/cross_report/{job_id}` | GET | 获取跨教材报告 |
| `/api/cross_graph/{job_id}` | GET | 获取跨教材图谱 |
| `/api/jobs/{job_id}/progress` | GET | 查询后台任务进度 |

## 核心功能

### 1. 文档解析
- PyMuPDF提取PDF文本
- 段落级分块（500-800字符）
- 保留页码和来源信息

### 2. 知识图谱构建
- LLM提取概念和关系
- 关系类型：前置依赖、并列、包含、应用
- JSON格式存储（nodes + edges）

### 3. 语义去重
- sentence-transformers计算语义相似度
- 余弦相似度阈值0.90（生物医学领域）
- 聚类合并，保留所有来源引用

### 4. 压缩比计算
- 公式：(整合后字符数 / 原始字符数) × 100%
- 目标：≤30%
- 输出到 `report/整合报告_{job_id}.md`

### 5. RAG问答
- FAISS向量检索（top-3）
- DeepSeek生成回答
- 引用来源：教材名、页码、内容片段

### 6. 跨教材整合（P2）
- 多教材上传和解析
- 跨教材语义对齐（相似度阈值0.90）
- 知识点来源追踪（保留所有教材来源）
- 贡献度分析（各教材贡献节点数、独有知识点、共享知识点）
- 知识互补性分析

### 7. 知识图谱可视化（P2）
- Cytoscape.js交互式渲染
- 节点点击查看详情
- 关联节点导航
- 多种布局算法（cose、circle、grid、breadthfirst）
- 缩放、拖拽、搜索功能

## 开发文档

详细的开发文档请查看：
- [MVP P0实施计划](docs/mvp-p0-implementation-plan.md)
- [Agent架构说明](docs/Agent架构说明.md)
- [开发日志](docs/开发日志.md)

## 测试

### 端到端测试（推荐）

```bash
# 完整测试套件（单教材 + 跨教材 + 图谱可视化）
python test_e2e.py
```

### 单元测试

```bash
# 测试解析器
python test_parser.py

# 测试知识图谱
python test_knowledge_graph.py

# 测试去重
python test_integration.py

# 测试报告生成
python test_report.py

# 测试RAG
python test_rag.py

# 测试跨教材整合
python test_cross_textbook.py

# 测试语义相似度
python test_similarity.py
```

## 注意事项

### 必需配置
1. **DeepSeek API密钥**: 编辑 `.env` 文件设置 `DEEPSEEK_API_KEY`
2. **教材文件**: 将PDF文件放入 `data/textbooks/` 或通过前端上传

### 已知限制（当前版本）
- 默认处理前3个文档块（小样本验证，可通过max_chunks参数调整）
- 文件系统状态管理（非数据库）
- 顺序处理多教材（未并行化）
- 跨教材RAG未完全适配（需合并所有chunks建立统一索引）

### P3增强方向（生产级）
- PostgreSQL/MongoDB状态管理
- 多进程并行处理
- Docker容器化部署
- 增量更新机制
- HITL（Human-in-the-Loop）边界案例审核
- CMeKG中文医学知识图谱对齐

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

- 作者：BallCard
- 专业：大二力学专业
- GitHub：[Repository URL]

