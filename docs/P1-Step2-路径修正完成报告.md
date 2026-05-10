# P1 Step 2: 路径和状态管理修正 - 完成报告

## 任务目标

让运行结果不再依赖启动目录，所有路径使用项目根目录绝对路径。

## 完成状态

**DONE** - 所有目标已达成，测试全部通过。

---

## 实施内容

### 1. 创建统一路径管理模块

**文件**: `src/backend/utils/paths.py`

**核心功能**:
- 自动计算项目根目录（基于文件位置，向上3层）
- 定义所有关键路径常量（DATA_DIR, TEXTBOOKS_DIR, RUNTIME_DIR, JOBS_DIR, REPORT_DIR）
- 提供 `get_job_dir(job_id)` 辅助函数
- 提供 `ensure_directories()` 自动创建目录
- 模块导入时自动确保目录存在

**关键设计**:
```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
# utils -> backend -> src -> root
```

使用 `pathlib.Path` 而非字符串拼接，确保跨平台兼容性。

---

### 2. 更新所有服务文件

#### 修改的文件（3个）:

1. **`src/backend/main.py`**
   - 导入统一路径模块
   - 移除 `get_job_dir()` 本地实现
   - 使用 `REPORT_DIR` 替代硬编码 `"report/"`
   - 启动时调用 `ensure_directories()`

2. **`src/backend/services/rag.py`**
   - 导入 `get_job_dir`
   - `save_index()` 和 `load_index()` 使用统一路径
   - 移除硬编码 `f"data/runtime/jobs/{job_id}"`

3. **`src/backend/services/report_generator.py`**
   - 导入 `REPORT_DIR`
   - 使用 `REPORT_DIR` 替代硬编码 `Path("report")`

#### 未修改的文件（3个）:

- `src/backend/services/parser.py` - 无硬编码路径
- `src/backend/services/integration.py` - 无硬编码路径
- `src/backend/services/knowledge_graph.py` - 无硬编码路径

---

### 3. 编写测试验证

#### 单元测试: `tests/test_paths.py`

**测试覆盖**:
- 所有路径是否为绝对路径
- 路径是否指向正确的项目根目录
- 目录结构是否正确
- `get_job_dir()` 函数是否正确
- `ensure_directories()` 是否创建所有目录
- 从不同目录导入模块时路径是否仍然正确

**测试结果**: ✓ 全部通过

#### 集成测试: `tests/test_integration_paths.py`

**测试覆盖**:
- Job状态持久化（main.py）
- 报告生成路径（report_generator.py）
- RAG索引路径（rag.py）
- 从不同目录启动时的路径正确性

**测试结果**: ✓ 全部通过

---

## 验证结果

### 1. 路径独立性验证

从项目根目录启动:
```
PROJECT_ROOT: D:\Workspace\competitions\Hex
REPORT_DIR: D:\Workspace\competitions\Hex\report
```

从 `/tmp` 启动:
```
PROJECT_ROOT: D:\Workspace\competitions\Hex
REPORT_DIR: D:\Workspace\competitions\Hex\report
```

从 `C:/Windows/Temp` 启动:
```
PROJECT_ROOT: D:\Workspace\competitions\Hex
REPORT_DIR: D:\Workspace\competitions\Hex\report
```

**结论**: 路径完全独立于启动目录 ✓

### 2. 硬编码路径清除验证

搜索结果:
```bash
grep -r 'Path(f"data' src/backend  # 0 matches
grep -r 'Path(f"report' src/backend  # 0 matches
grep -r '"data/' src/backend  # 0 matches (除注释外)
grep -r '"report/' src/backend  # 0 matches (除注释外)
```

**结论**: 所有硬编码路径已清除 ✓

### 3. 服务集成验证

- Job状态保存到: `D:\Workspace\competitions\Hex\data\runtime\jobs\test_integration\state.json` ✓
- 报告生成到: `D:\Workspace\competitions\Hex\report\整合报告_test_report.md` ✓
- RAG索引保存到: `D:\Workspace\competitions\Hex\data\runtime\jobs\test_rag\` ✓

**结论**: 所有服务正确使用统一路径 ✓

---

## 技术亮点

### 1. 自动路径解析

使用 `Path(__file__).resolve().parent` 链式调用，无需手动配置项目根目录。

### 2. 模块导入时初始化

```python
# 模块导入时自动确保目录存在
ensure_directories()
```

避免运行时目录不存在错误。

### 3. 跨平台兼容

使用 `pathlib.Path` 而非字符串拼接，自动处理 Windows/Linux 路径分隔符差异。

### 4. 向后兼容

保持 API 不变（`get_job_dir(job_id)` 仍然可用），只是实现从本地函数改为导入统一模块。

---

## 影响范围

### 修改的文件（6个）

**新增**:
- `src/backend/utils/paths.py`
- `src/backend/utils/__init__.py`
- `tests/test_paths.py`
- `tests/test_integration_paths.py`

**修改**:
- `src/backend/main.py`
- `src/backend/services/rag.py`
- `src/backend/services/report_generator.py`

### 未修改的文件（3个）

- `src/backend/services/parser.py`
- `src/backend/services/integration.py`
- `src/backend/services/knowledge_graph.py`

---

## 退出条件检查

- [x] 从任意目录启动后端，路径都指向项目根目录
- [x] 前端和API读取同一套路径
- [x] 所有硬编码路径已替换
- [x] 使用 pathlib.Path 而非字符串拼接
- [x] 目录不存在时自动创建
- [x] 保持向后兼容，不破坏现有功能
- [x] 测试验证路径正确性

---

## 后续建议

### 可选优化（非必需）

1. **环境变量覆盖**: 允许通过环境变量 `HEX_PROJECT_ROOT` 覆盖自动检测的路径（用于特殊部署场景）

2. **路径验证**: 在 `ensure_directories()` 中添加写权限检查，提前发现权限问题

3. **日志记录**: 在路径模块导入时记录 PROJECT_ROOT，便于调试

### 不建议的做法

- ❌ 使用相对路径（会导致启动目录依赖）
- ❌ 使用 `os.getcwd()`（会随启动目录变化）
- ❌ 硬编码绝对路径（不可移植）

---

## 总结

**任务状态**: DONE

**核心成果**:
1. 创建统一路径管理模块，所有路径基于项目根目录
2. 更新3个服务文件使用统一路径
3. 清除所有硬编码路径
4. 编写单元测试和集成测试，验证路径独立性
5. 从任意目录启动后端，路径都正确指向项目根目录

**测试覆盖**:
- 单元测试: 7个测试用例 ✓
- 集成测试: 4个测试用例 ✓
- 路径独立性验证: 3个不同目录 ✓

**质量保证**:
- 使用 pathlib.Path 确保跨平台兼容
- 自动创建目录避免运行时错误
- 保持向后兼容不破坏现有功能
- 完整的测试覆盖确保可靠性

**可演示性**: 可从任意目录启动后端，所有功能正常工作。

---

*报告生成时间: 2026-05-10*
*执行者: Claude (Kiro)*
