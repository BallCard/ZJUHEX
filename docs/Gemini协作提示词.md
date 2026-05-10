# Gemini前端优化协作提示词

## 项目背景

你正在协助优化一个**医学教材知识整合系统**的前端界面。这是一个5小时黑客松项目，当前P0阶段已完成基础流水线验证，现在进入P1阶段，需要将前端从"功能演示"提升到"可信演示"。

## 当前状态

### 已完成（P0）
- ✅ 后端API完整（FastAPI，10个端点）
- ✅ 基础前端（单HTML文件，`src/frontend/index.html`）
- ✅ 知识图谱可视化（Cytoscape.js）
- ✅ RAG问答功能
- ✅ 端到端测试通过

### 当前问题
1. **无进度反馈**: 知识图谱构建需30-45秒，用户看不到进度
2. **交互不足**: 图谱节点无法点击查看详情
3. **引用不清晰**: RAG答案的引用来源展示简陋
4. **错误处理缺失**: API失败时前端无明确提示

## 你的任务

优化前端界面，重点解决以下4个问题：

### 任务1: 添加进度轮询显示（优先级：高）

**需求**:
- 用户点击"构建知识图谱"后，显示进度条或百分比
- 每2秒轮询`GET /api/jobs/{job_id}/progress`获取进度
- 显示格式："处理中 15/30 (50%)"
- 完成后自动跳转到结果展示

**API响应格式**:
```json
{
  "status": "processing" | "completed" | "failed",
  "progress": 15,
  "total": 30,
  "error": "错误信息（仅失败时）"
}
```

**实现建议**:
```javascript
async function pollProgress(jobId) {
    const progressDiv = document.getElementById('progress');
    
    const interval = setInterval(async () => {
        const resp = await fetch(`http://localhost:8000/api/jobs/${jobId}/progress`);
        const data = await resp.json();
        
        if (data.status === 'completed') {
            clearInterval(interval);
            progressDiv.innerHTML = '✓ 完成';
            loadGraph(jobId);
        } else if (data.status === 'failed') {
            clearInterval(interval);
            progressDiv.innerHTML = `✗ 失败: ${data.error}`;
        } else {
            const percent = Math.round((data.progress / data.total) * 100);
            progressDiv.innerHTML = `处理中 ${data.progress}/${data.total} (${percent}%)`;
        }
    }, 2000);
}
```

---

### 任务2: 图谱节点交互增强（优先级：高）

**需求**:
- 点击节点显示详情面板（右侧或弹窗）
- 详情包含：
  - 知识点名称
  - 完整定义
  - 来源（教材名、章节、页码）
  - 关联节点列表（前置依赖、应用场景等）

**节点数据格式**:
```json
{
  "id": "node_001",
  "name": "动作电位",
  "definition": "细胞受到刺激后，膜电位发生的一次快速而可逆的倒转",
  "category": "核心概念",
  "source_page": 35,
  "source_chunk": "chunk_35_2",
  "textbook": "03_生理学"
}
```

**实现建议**:
```javascript
// Cytoscape.js节点点击事件
cy.on('tap', 'node', (evt) => {
    const node = evt.target.data();
    
    // 获取关联节点
    const neighbors = cy.nodes(`#${node.id}`).neighborhood('node');
    const neighborNames = neighbors.map(n => n.data('label')).join(', ');
    
    // 显示详情面板
    document.getElementById('nodeDetail').innerHTML = `
        <h3>${node.label}</h3>
        <p><strong>定义:</strong> ${node.definition}</p>
        <p><strong>来源:</strong> ${node.textbook} 第${node.source_page}页</p>
        <p><strong>类别:</strong> ${node.category}</p>
        <p><strong>关联节点:</strong> ${neighborNames || '无'}</p>
    `;
    document.getElementById('nodeDetail').style.display = 'block';
});
```

---

### 任务3: RAG引用展示优化（优先级：中）

**需求**:
- RAG答案下方清晰展示引用来源
- 每个引用包含：教材名、页码、原文片段（前100字）
- 引用可点击展开查看完整原文

**API响应格式**:
```json
{
  "question": "什么是动作电位？",
  "answer": "动作电位是细胞受到刺激后...",
  "citations": [
    {
      "textbook": "03_生理学",
      "page": 35,
      "content": "动作电位是细胞受到刺激后，膜电位发生的一次快速而可逆的倒转...",
      "relevance_score": 0.92
    }
  ]
}
```

**实现建议**:
```html
<div id="answer">
    <h3>回答</h3>
    <p id="answerText"></p>
    
    <h4>引用来源</h4>
    <div id="citations"></div>
</div>

<script>
function displayAnswer(result) {
    document.getElementById('answerText').innerText = result.answer;
    
    const citationsHtml = result.citations.map((c, i) => `
        <div class="citation">
            <strong>[${i + 1}] ${c.textbook}, 第${c.page}页</strong>
            <p class="citation-preview">${c.content.substring(0, 100)}...</p>
            <button onclick="showFullCitation(${i})">查看完整原文</button>
        </div>
    `).join('');
    
    document.getElementById('citations').innerHTML = citationsHtml;
}
</script>

<style>
.citation {
    border-left: 3px solid #667eea;
    padding-left: 10px;
    margin: 10px 0;
}
.citation-preview {
    color: #666;
    font-size: 0.9em;
}
</style>
```

---

### 任务4: 错误处理和状态提示（优先级：中）

**需求**:
- API调用失败时显示明确错误信息
- 长时间操作显示加载动画
- 成功操作显示确认提示（3秒后自动消失）

**实现建议**:
```javascript
async function apiCall(url, options = {}) {
    try {
        showLoading();
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        
        const data = await response.json();
        hideLoading();
        showSuccess('操作成功');
        return data;
        
    } catch (error) {
        hideLoading();
        showError(error.message);
        throw error;
    }
}

function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast error';
    toast.innerText = `✗ ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast success';
    toast.innerText = `✓ ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
```

```css
.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 4px;
    color: white;
    font-weight: bold;
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
}

.toast.error {
    background: #e74c3c;
}

.toast.success {
    background: #27ae60;
}

@keyframes slideIn {
    from {
        transform: translateX(400px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
```

---

## 技术约束

1. **保持单HTML文件**: 不引入构建工具，所有代码在`index.html`中
2. **使用CDN**: 外部库通过CDN引入（Cytoscape.js已引入）
3. **兼容性**: 支持Chrome/Edge最新版即可
4. **样式**: 保持现有渐变紫色主题（#667eea到#764ba2）
5. **响应式**: 不强制要求，桌面端优先

## API端点参考

```
GET  /api/health                    # 健康检查
POST /api/upload                    # 上传教材
POST /api/parse/{job_id}            # 解析教材
POST /api/build_graph/{job_id}      # 构建知识图谱
POST /api/integrate/{job_id}        # 跨教材整合
POST /api/rag/index/{job_id}        # 建立RAG索引
POST /api/rag/query/{job_id}        # RAG问答
GET  /api/jobs/{job_id}/status      # 查询任务状态
GET  /api/jobs/{job_id}/progress    # 查询任务进度（P1新增）
GET  /api/jobs/{job_id}/graph       # 获取知识图谱
GET  /api/report/{job_id}           # 获取整合报告
```

## 交付物

请提供优化后的`index.html`文件，包含：

1. ✅ 进度轮询功能
2. ✅ 图谱节点交互
3. ✅ RAG引用展示优化
4. ✅ 错误处理和状态提示

## 测试方法

1. 启动后端: `cd src/backend && uvicorn main:app --reload --port 8000`
2. 打开前端: `src/frontend/index.html`
3. 测试流程:
   - 上传`data/textbooks/03_生理学.pdf`
   - 点击"解析文档"
   - 点击"构建知识图谱"（观察进度显示）
   - 点击图谱节点（查看详情面板）
   - 输入问题测试RAG（查看引用展示）
   - 故意触发错误（如未上传文件就解析）测试错误提示

## 注意事项

- **不要改变API调用逻辑**: 保持与现有后端兼容
- **不要引入复杂框架**: 保持轻量级
- **优先功能完整性**: 美观度次要，功能可用性优先
- **保留现有功能**: 不要删除已有的上传、解析、整合等功能

---

## 当前`index.html`位置

文件路径: `D:\Workspace\competitions\Hex\src\frontend\index.html`

你可以直接读取该文件，在其基础上进行优化。

---

**开始时间**: 等待Claude完成P1 Step 4后通知你开始

**预计用时**: 30-45分钟

**协作方式**: Claude会在Step 4完成后将当前状态和API更新同步给你，你基于最新状态优化前端
