# 文档目录

本目录包含医学教材知识整合系统的完整设计文档和研究资料。

## 核心设计文档

### [需求分析.md](需求分析.md)
- 问题背景与核心目标
- 子问题分解（知识点粒度、重复判定、教学连贯性、压缩比、RAG分块）
- 技术约束与验收标准
- 风险与应对

### [系统设计.md](系统设计.md)
- 系统架构总览
- 技术选型与实现方案
- 数据流设计
- 关键模块详细设计

### [Agent架构说明.md](Agent架构说明.md)
- Agent编排架构
- 设计决策论证
- 单Agent vs 多Agent权衡
- HITL机制设计

## 研究资料

### [外部成熟项目参考.md](外部成熟项目参考.md)
**来源**: 用户提供的外部项目调研
**重点内容**:
- Docling文档解析方案
- HITL（Human-in-the-Loop）机制设计
- 章节识别策略

### [deep-research-report.md](deep-research-report.md)
**来源**: AI深度调研（英文）
**重点内容**:
- **关键结论**: "MinerU is the best current open-source parser for Chinese medical textbooks"
- Docling中文边界案例警告
- 动态压缩策略（保留完整图谱 + 检索时压缩）
- 最终技术栈推荐

### [医学教材知识整合系统：开源架构与核心技术全景调研报告.md](医学教材知识整合系统：开源架构与核心技术全景调研报告.md)
**来源**: 综合学术调研（中文）
**重点内容**:
- **生物医学去重阈值**: 0.90-0.92（而非通用的0.85）
- AntV G6性能分析（vs D3.js DOM瓶颈）
- LangGraph vs CrewAI vs AutoGen对比
- CMeKG中文医学知识图谱对齐

## 文档使用指南

### 快速开始
1. 先读 **需求分析.md** 了解问题定义
2. 再读 **系统设计.md** 了解技术方案
3. 最后读 **Agent架构说明.md** 了解编排逻辑

### 技术决策参考
当需要做技术选型时，按以下优先级参考：
1. **医学教材知识整合系统全景调研报告.md** - 领域特定最佳实践
2. **deep-research-report.md** - 开源方案综合评估
3. **外部成熟项目参考.md** - 工程实践经验

### 关键技术决策摘要

| 技术点 | 最终决策 | 依据来源 |
|--------|---------|---------|
| 文档解析 | MinerU (主) + Docling (备) | deep-research-report.md |
| 去重阈值 | 0.90-0.92 | 医学教材知识整合系统全景调研报告.md |
| 压缩策略 | 保留完整图谱 + 检索时动态压缩 | deep-research-report.md |
| Embedding | BGE-M3 (dense+sparse+multi-vector) | 医学教材知识整合系统全景调研报告.md |
| 可视化 | Cytoscape.js (P0) → AntV G6 (P1) | 医学教材知识整合系统全景调研报告.md |
| Agent编排 | LangGraph (状态机) | 医学教材知识整合系统全景调研报告.md |

## 更新记录

- **2026-05-10**: 创建文档索引，整合四个信源的研究成果
- **2026-05-10**: 完成MVP P0规划，固化到 `C:\Users\12855\.claude\plans\mvp-p0-cosmic-koala.md`
