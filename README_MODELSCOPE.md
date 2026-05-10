# 魔搭（ModelScope）部署指南

## 📦 部署步骤

### 1. 创建魔搭创空间（Space）

1. 访问 [魔搭社区](https://modelscope.cn/)
2. 登录账号
3. 点击"创空间" → "创建Space"
4. 选择 **Gradio** 应用类型
5. 填写基本信息：
   - 名称：医学教材知识整合系统
   - 描述：AI全栈黑客松 - 学科知识整合智能体
   - 可见性：公开/私有

### 2. 上传项目文件

将以下文件上传到Space：

```
Hex/
├── app.py                          # 主入口文件（Gradio界面）
├── requirements_modelscope.txt     # 依赖文件（重命名为requirements.txt）
├── .env                            # 环境变量（需要配置API密钥）
├── src/
│   └── backend/                    # 后端代码
│       ├── main.py
│       ├── services/
│       └── utils/
└── data/                           # 数据目录（自动创建）
```

**重要**：上传时将 `requirements_modelscope.txt` 重命名为 `requirements.txt`

### 3. 配置环境变量

在Space设置中添加环境变量：

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

或者创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

### 4. 启动应用

魔搭会自动：
1. 安装 `requirements.txt` 中的依赖
2. 运行 `app.py`
3. 在端口 7860 启动Gradio界面

## 🎯 使用说明

### 界面功能

1. **📚 文档处理**
   - 上传PDF/TXT/MD/DOCX教材文件
   - 自动解析并提取文本块
   - 生成唯一Job ID

2. **🕸️ 知识图谱**
   - 选择要处理的章节（1-10）
   - 使用LLM提取知识点和关系
   - 构建结构化知识图谱

3. **🔄 去重整合**
   - 基于语义相似度去重（阈值0.90）
   - 生成整合报告
   - 计算压缩比（目标≤30%）

4. **💬 RAG问答**
   - 基于FAISS向量检索
   - 带引用来源的精准回答
   - 支持多轮对话

### 工作流程

```
上传教材 → 解析文档 → 构建图谱 → 去重整合 → 生成报告 → RAG问答
```

## 🔧 技术架构

### 前端
- **Gradio 4.0+**: Web界面框架
- 4个Tab页：文档处理、知识图谱、去重整合、RAG问答

### 后端
- **FastAPI**: RESTful API服务（后台运行在8000端口）
- **DeepSeek**: LLM知识提取
- **sentence-transformers**: 语义嵌入（paraphrase-multilingual-MiniLM-L12-v2）
- **FAISS**: 向量检索

### 数据流
```
PDF → MinerU解析 → 文本块 → LLM提取 → 知识图谱 → 语义去重 → 整合报告
                                                    ↓
                                            FAISS索引 → RAG问答
```

## 📊 性能指标

- **压缩比**: ≤30%（核心目标）
- **去重阈值**: 0.90（生物医学领域最佳实践）
- **RAG检索**: Top-3相关块
- **处理速度**: 约10-20块/分钟（取决于LLM API速度）

## ⚠️ 注意事项

### 1. API密钥配置
- 必须配置 `DEEPSEEK_API_KEY`
- 建议使用魔搭的环境变量功能（不要硬编码）

### 2. 文件大小限制
- 魔搭Space可能有文件上传大小限制
- 建议单个PDF不超过50MB
- 大文件可以先在本地预处理

### 3. 计算资源
- 知识图谱构建需要调用LLM API（可能较慢）
- 向量嵌入需要一定内存（sentence-transformers模型约500MB）
- 建议选择魔搭的GPU实例（如果可用）

### 4. 持久化存储
- 数据存储在 `data/runtime/jobs/{job_id}/`
- Space重启后数据可能丢失
- 重要数据请及时下载报告

## 🚀 本地测试

在上传到魔搭前，可以本地测试：

```bash
# 1. 安装依赖
pip install -r requirements_modelscope.txt

# 2. 配置环境变量
echo "DEEPSEEK_API_KEY=your_key" > .env

# 3. 运行应用
python app.py

# 4. 访问界面
# 浏览器打开 http://localhost:7860
```

## 📝 部署检查清单

- [ ] 创建魔搭Space（选择Gradio类型）
- [ ] 上传 `app.py`
- [ ] 上传 `requirements.txt`（从requirements_modelscope.txt重命名）
- [ ] 上传 `src/backend/` 目录
- [ ] 配置 `DEEPSEEK_API_KEY` 环境变量
- [ ] 启动Space并等待依赖安装
- [ ] 测试上传文档功能
- [ ] 测试知识图谱构建
- [ ] 测试去重整合
- [ ] 测试RAG问答

## 🔗 相关链接

- [魔搭社区](https://modelscope.cn/)
- [Gradio文档](https://www.gradio.app/docs/)
- [项目GitHub](https://github.com/your-repo)

## 💡 常见问题

### Q1: 依赖安装失败？
A: 检查 `requirements.txt` 格式，确保版本号正确。某些包可能需要系统依赖（如magic-pdf）。

### Q2: API调用失败？
A: 检查 `DEEPSEEK_API_KEY` 是否正确配置，确保API有足够余额。

### Q3: 知识图谱构建很慢？
A: 这是正常的，LLM提取需要时间。可以减少处理的章节数量或使用缓存。

### Q4: 压缩比超过30%？
A: 调整去重阈值（默认0.90），或增加处理的文本量。

## 📧 支持

如有问题，请联系：
- GitHub Issues: [项目地址]
- 邮箱: your-email@example.com
