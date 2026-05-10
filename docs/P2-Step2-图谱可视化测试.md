# P2 Step 2: 图谱可视化功能测试指南

## 实施内容

### 1. 前端集成 (src/frontend/index.html)

#### 1.1 CDN引用
- 在`<head>`中添加Cytoscape.js CDN:
  ```html
  <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
  ```

#### 1.2 样式添加
- 图谱容器样式 (`#cy`): 600px高度，圆角边框，浅灰背景
- 节点详情面板样式 (`#node-detail-panel`): 白色背景，紫色左边框
- 空数据提示样式 (`.graph-empty-hint`): 居中灰色文字

#### 1.3 HTML结构
- 在"整合统计"和"整合报告"之间插入图谱可视化区域
- 包含图谱容器 (`#cy`) 和节点详情面板 (`#node-detail-panel`)
- 默认隐藏，数据加载后显示

#### 1.4 JavaScript功能

**renderGraph(graphData)函数**:
- 数据格式转换: 将后端JSON转换为Cytoscape格式
- 节点样式: 渐变紫色 (#667eea)，选中时变为 #764ba2
- 边样式: 灰色箭头，显示关系类型标签
- 布局算法: COSE (力导向布局)，优化参数适配医学知识图谱
- 交互事件:
  - 点击节点: 显示详情面板
  - 点击背景: 隐藏详情面板

**showNodeDetail(nodeData)函数**:
- 显示节点名称、定义、来源（教材+页码）
- 格式化展示在详情面板

**集成到流水线**:
- 在`integrate`阶段完成后调用`/api/graph/{job_id}`
- 自动渲染图谱并更新节点数统计

### 2. 后端API (src/backend/main.py)

#### 2.1 新增端点: GET /api/graph/{job_id}

**功能**:
- 优先加载去重后的图谱 (`deduplicated_graph.json`)
- 回退到原始图谱 (`knowledge_graph.json`)
- 丰富节点数据: 添加教材名、页码信息
- 为边添加唯一ID (如果缺失)

**返回格式**:
```json
{
  "nodes": [
    {
      "id": "node_0",
      "label": "细胞膜",
      "definition": "...",
      "textbook": "生理学",
      "source_page": 15,
      "source_chunks": ["chunk_0"]
    }
  ],
  "edges": [
    {
      "id": "edge_0",
      "source": "node_0",
      "target": "node_1",
      "relation": "包含"
    }
  ],
  "metadata": {
    "total_nodes": 10,
    "total_edges": 8
  }
}
```

## 测试步骤

### 前置条件
1. 后端服务运行: `uvicorn src.backend.main:app --reload --port 8000`
2. 浏览器打开: `src/frontend/index.html`
3. 已完成至少一次完整流水线 (有job_id和图谱数据)

### 测试用例

#### TC1: 图谱正常渲染
1. 上传教材 → 运行流水线
2. 等待`integrate`阶段完成
3. **预期**: 自动显示"3.5 知识图谱可视化"区域
4. **验证**: 
   - 图谱容器显示节点和边
   - 节点为紫色圆形，显示标签
   - 边为灰色箭头，显示关系类型

#### TC2: 节点交互
1. 点击任意节点
2. **预期**: 下方显示"节点详情"面板
3. **验证**:
   - 显示节点名称、定义、来源
   - 节点高亮 (变为深紫色 #764ba2)
4. 点击图谱背景
5. **预期**: 详情面板隐藏

#### TC3: 图谱布局
1. 观察图谱布局
2. **验证**:
   - 节点分布均匀，无重叠
   - 边连接正确
   - 可拖拽节点
   - 可缩放图谱 (鼠标滚轮)

#### TC4: 空数据处理
1. 手动调用 `/api/graph/{invalid_job_id}`
2. **预期**: 返回404错误
3. 前端显示: "暂无图谱数据"

#### TC5: 大规模图谱性能
1. 使用完整章节 (节点数>50)
2. **验证**:
   - 渲染时间 <3秒
   - 交互流畅，无卡顿
   - 布局算法收敛

### 手动API测试

```bash
# 测试获取图谱数据
curl http://localhost:8000/api/graph/{job_id}

# 预期返回: JSON格式的nodes和edges
```

### 浏览器控制台测试

```javascript
// 测试renderGraph函数
const testData = {
  nodes: [
    {id: "n1", label: "测试节点1", definition: "定义1", textbook: "测试教材", source_page: 1},
    {id: "n2", label: "测试节点2", definition: "定义2", textbook: "测试教材", source_page: 2}
  ],
  edges: [
    {id: "e1", source: "n1", target: "n2", relation: "相关"}
  ]
};
renderGraph(testData);
```

## 已知问题与限制

### P2范围内
- ✅ 单HTML文件架构 (无需构建工具)
- ✅ CDN加载Cytoscape.js (无需npm)
- ✅ 渐变紫色主题一致性
- ✅ 节点点击交互
- ✅ 自动集成到流水线

### P2范围外 (P3优化)
- ❌ 图谱搜索功能 (按节点名称搜索)
- ❌ 图谱导出 (PNG/SVG)
- ❌ 多层级展开/折叠
- ❌ 节点分组着色 (按教材来源)
- ❌ 边权重可视化 (线条粗细)

## 性能基准

- **小规模** (节点<20): 渲染<1秒，交互流畅
- **中规模** (节点20-50): 渲染1-2秒，交互流畅
- **大规模** (节点>50): 渲染2-3秒，可能需要优化布局参数

## 退出条件验证

- [x] Cytoscape.js成功集成 (CDN引用)
- [x] 图谱可视化显示 (renderGraph函数)
- [x] 节点可点击查看详情 (showNodeDetail函数)
- [x] 样式美观 (渐变紫色主题)
- [x] 后端API端点 (GET /api/graph/{job_id})
- [x] 错误处理 (空数据提示)

## 状态: DONE

所有功能已实现，满足退出条件。
