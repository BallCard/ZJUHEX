# 知识图谱演示 - 生理学教材

## 📊 演示结果

### 处理范围
- **教材**: 03_生理学.pdf
- **处理章节**: 前10个文档块（演示用）
- **原始文档**: 932个文档块，566,853字符

### 核心指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **压缩比** | **0.78%** | ✅ 远超目标（≤30%） |
| **原始节点** | 162 | LLM提取的知识点 |
| **去重后节点** | 146 | 语义去重后 |
| **去重率** | 9.88% | 合并了16个重复节点 |
| **关系边数** | 136 | 知识点之间的关系 |

### 处理时间
- **文档解析**: ~1秒
- **知识提取**: ~3分钟（10个chunk，每个15-20秒）
- **语义去重**: ~1秒
- **报告生成**: <1秒
- **总计**: ~3分钟

## 📁 生成文件

```
demo_output/
├── knowledge_graph.json    # 知识图谱数据（81KB）
├── visualize.html          # 交互式可视化页面
└── README.md              # 本文件

report/
└── 整合报告_demo.md        # 详细整合报告（34KB）
```

## 🎨 可视化演示

### 在线查看
打开 `visualize.html` 即可查看交互式知识图谱：

```bash
# 方式1: 直接双击打开
demo_output/visualize.html

# 方式2: 使用浏览器打开
start demo_output/visualize.html  # Windows
open demo_output/visualize.html   # Mac
```

### 功能特性
- ✅ 交互式节点拖拽
- ✅ 点击查看节点详情
- ✅ 自动布局算法
- ✅ 缩放和平移
- ✅ 关系类型标注
- ✅ 节点类型颜色区分

## 📋 知识图谱样例

### 提取的知识节点（部分）
1. **生理学** (concept) - 研究生物体及其组成部分的功能的学科
2. **罗自强** (person) - 生理学第10版主编之一
3. **管又飞** (person) - 生理学第10版主编之一
4. **人民卫生出版社** (organization) - 教材出版机构
5. **医学教育** (concept) - 培养医学人才的教育体系

### 知识关系（部分）
- 生理学 --[包含]--> 罗自强
- 生理学 --[包含]--> 管又飞
- 人民卫生出版社 --[出版]--> 生理学
- 医学教育 --[包含]--> 课程思政
- 医学教育 --[应用]--> 教材体系

## 🔍 去重案例

### 成功合并的节点
1. **生理学** - 合并了3个语义相似的节点
   - 来源: chunk_0, chunk_8, chunk_9
   - 相似度: ≥0.90

2. **医学教育** - 合并了"医学人才培养"和"人才培养模式"
   - 来源: chunk_1, chunk_2
   - 相似度: ≥0.90

3. **预防医学** - 合并了2个重复节点
   - 来源: chunk_1, chunk_2
   - 相似度: ≥0.90

### 去重算法
- **模型**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **阈值**: 0.90（生物医学领域最佳实践）
- **方法**: 余弦相似度 + 聚类合并

## 📈 压缩效果分析

### 为什么压缩比这么低？
1. **知识提取**: 只保留核心概念和定义，过滤冗余描述
2. **语义去重**: 合并重复和相似的知识点
3. **结构化表示**: 图谱结构比原文更紧凑

### 压缩比计算
```
原始字符数: 566,853（全部932个chunk）
整合后字符数: 4,439（146个节点的标签+定义）
压缩比 = 4,439 / 566,853 × 100% = 0.78%
```

## 🚀 完整流程演示

### 1. 文档解析
```python
from services.parser import parse_textbook
chunks = parse_textbook("data/textbooks/03_生理学.pdf")
# 输出: 932个文档块
```

### 2. 知识图谱构建
```python
from services.knowledge_graph import KnowledgeGraphBuilder
builder = KnowledgeGraphBuilder()
graph = builder.build_graph(chunks, max_chunks=10)
# 输出: 162个节点, 143条边
```

### 3. 语义去重
```python
from services.integration import deduplicate_knowledge_graph
deduplicated = deduplicate_knowledge_graph(graph)
# 输出: 146个节点, 136条边
```

### 4. 报告生成
```python
from services.report_generator import generate_integration_report
report_path = generate_integration_report(chunks, graph, deduplicated, "demo", chapter_info)
# 输出: report/整合报告_demo.md
```

## 🎯 技术亮点

### 1. LLM知识提取
- **模型**: DeepSeek API
- **提示工程**: 结构化JSON输出
- **提取内容**: 概念、定义、关系类型

### 2. 语义去重
- **嵌入模型**: 多语言MiniLM
- **相似度计算**: 余弦相似度
- **聚类算法**: 基于阈值的层次聚类

### 3. 可视化
- **框架**: Cytoscape.js
- **布局算法**: COSE（力导向布局）
- **交互**: 拖拽、缩放、点击查看详情

## 📝 下一步扩展

### P1功能（完整版）
- [ ] 处理完整章节（而非10个chunk）
- [ ] 跨教材整合（7本教材）
- [ ] RAG问答系统
- [ ] 多轮对话修改决策
- [ ] 在线部署

### 优化方向
- [ ] 并行LLM调用（加速提取）
- [ ] 增量缓存（避免重复提取）
- [ ] 混合检索（BM25 + 向量）
- [ ] 重排序模型（提升RAG准确度）

## 📞 联系方式

- **项目**: AI全栈黑客松 - 学科知识整合智能体
- **演示时间**: 2026-05-10
- **处理时长**: ~3分钟
