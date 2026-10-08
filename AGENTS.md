# HEX 医学教材知识整合原型

- 当前为已归档 P2 原型；先读 README 与 `docs/ACCEPTANCE.md`，不重演旧 P0 比赛计划。
- 后端入口 `src/backend/main.py`；React/Vite 前端为 `src/frontend_new/`。
- `src/frontend/` 为早期单页参考；改变实现前确认目标版本。
- 环境与依赖按 README、`requirements.txt` 配置；密钥放环境变量，不提交 `.env`。
- 教材、凭据、向量库与运行数据不属于源码归档，不上传或据此宣称医学准确性。
- 任务中间结果在 `data/runtime/jobs/`；报告在 `report/`，保留输入来源与处理决策。
- 压缩比用实际整合内容与原文计算，不能把提示词压缩或目标值当交付结果。
- RAG 回答附教材、章节或页码引用；信息缺失时保留未知。
- 改架构时按需要更新 `docs/Agent架构说明.md`，解释数据流、技术取舍和真实限制。
- 后端验证 `python -m pytest tests -q`；语法检查 `python -m compileall -q src/backend`。
- 前端变更在 `src/frontend_new/` 执行 `npm run build`；说明未运行的验证与原因。
- 历史验收、线上链接和比赛时限不是当前运行结果或部署授权。
