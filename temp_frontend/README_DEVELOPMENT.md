# 知识拓扑分析平台 - 技术开发文档

## 1. 项目概述
本平台是一款基于医疗/生理学知识图谱的交互式分析工具，旨在通过 RAG (检索增强生成) 引擎将非结构化教材数据转化为结构化的语义网络。

## 2. 核心技术栈
- **Frontend**: React 18 (Functional Components, Hooks)
- **Styling**: Tailwind CSS + Framer Motion (用于丝滑动效)
- **Graph Engine**: Cytoscape.js (处理复杂拓扑布局与交互)
- **Icons**: Lucide React

## 3. 核心功能模块实现

### A. 拓扑图谱计算渲染 (KnowledgeGraph.tsx)
- **布局算法**: 采用 `cose` 布局实现力导向分布，通过调节 `nodeRepulsion` (400,000) 确保节点不会在复杂关系下产生视觉重叠。
- **高亮逻辑**:
  - `applyHighlight`: 使用 `closedNeighborhood()` 获取当前节点及其所有相邻邻居，应用 `highlight` 类，其余元素添加 `dimmed` 类实现暗化效果。
  - **缩放曲线**: 节点大小与字体大小根据 `node.degree()` (连接度) 动态计算：
    - `width/height`: `24 + Math.min(degree * 4, 30)`px
    - `font-size`: `base (10) + scale (degree * 1.5) + categoryBoost`

### B. 语义检测器 (Semantic Inspector)
- 位于右侧的滑出式面板。
- 接收从 `KnowledgeGraph` 传出的 `detailedNeighbors` 数据。
- **关联集群**: 不仅列出邻居名称，还展示其语义定义，帮助用户在不切换焦点的情况下理解知识背景。

### C. 资源与观测系统
- **解析资源**: 模拟了 RAG 系统的文件入库与提取状态。
- **系统观测**: 通过 Framer Motion 实现的动态度量仪表盘，展示认知密度与链路稳定性等元数据。

## 4. 后端对接指南
如需接入真实的 RAG 后端（如 Python/FastAPI），请重点关注 `App.tsx` 中的 `handleSearch` 函数：
1. **输入**: 用户在 Omnibar 输入的自然语言查询。
2. **处理**: 后端应返回 `answer` (简述) 和 `citations` (带页码和置信度的切片)。
3. **图谱联动**: 后端可同步返回相关的 `graph_delta` 段落，通过更新 `graphData` 来实时补全图谱。

## 5. UI 设计规范
- **字体**: Serif (衬线体) 应用于标题和叙述文本，体现学术严肃感；Sans (无衬线) 应用于数据与 UI 控件。
- **颜色系统**: 
  - 核心机制: `#D97757` (Rust)
  - 评价指标: `#3B82F6` (Blue)
  - 基础理论: `#8B5CF6` (Purple)
  - 临床表现: `#EF4444` (Red)
