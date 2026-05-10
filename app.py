"""
魔搭（ModelScope）部署入口文件
使用Gradio创建Web界面，集成医学教材知识整合系统
"""

import os
import sys
import json
import time
import gradio as gr
from pathlib import Path
import threading
import uvicorn
from fastapi import FastAPI

# 添加backend路径
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

# 导入FastAPI应用
from main import app as fastapi_app

# 导入服务
from services.parser import parse_textbook
from services.knowledge_graph import build_knowledge_graph
from services.integration import deduplicate_knowledge_graph
from services.report_generator import generate_integration_report
from services.rag import RAGPipeline
from utils.paths import get_job_dir, REPORT_DIR, ensure_directories

# 确保目录存在
ensure_directories()

# 全局变量存储当前job_id
current_job_id = None

# 启动FastAPI后端（在后台线程）
def start_fastapi_backend():
    """在后台线程启动FastAPI服务"""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")

# 启动后端线程
backend_thread = threading.Thread(target=start_fastapi_backend, daemon=True)
backend_thread.start()
time.sleep(2)  # 等待后端启动


def upload_and_parse(file):
    """上传并解析教材"""
    global current_job_id

    if file is None:
        return "❌ 请先上传文件", ""

    try:
        # 生成job_id
        import uuid
        job_id = str(uuid.uuid4())[:8]
        current_job_id = job_id

        # 创建job目录
        job_dir = get_job_dir(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = job_dir / Path(file.name).name
        import shutil
        shutil.copy(file.name, file_path)

        # 解析文档
        chunks = parse_textbook(str(file_path))

        if not chunks:
            return "❌ 文档解析失败：未提取到内容", ""

        # 保存chunks
        chunks_path = job_dir / "parsed_chunks.json"
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

        total_chars = sum(c.get("char_count", 0) for c in chunks)

        result = f"""✅ 文档解析成功！

**Job ID**: `{job_id}`
**文件名**: {Path(file.name).name}
**解析块数**: {len(chunks)}
**总字符数**: {total_chars:,}

请点击"构建知识图谱"继续下一步。
"""
        return result, job_id

    except Exception as e:
        return f"❌ 解析失败: {str(e)}", ""


def build_graph(job_id, chapter_num):
    """构建知识图谱"""
    if not job_id:
        return "❌ 请先上传并解析文档"

    try:
        # 加载chunks
        chunks_path = get_job_dir(job_id) / "parsed_chunks.json"
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        # 使用ContentDetector选择章节
        from services.content_detector import ContentDetector
        detector = ContentDetector()

        content_start_idx = detector.detect_content_start(chunks)
        content_chunks = chunks[content_start_idx:]
        chapter_chunks = detector.select_chapter(content_chunks, chapter_num=chapter_num)

        # 使用AsyncExtractor提取知识
        from services.async_extractor import AsyncExtractor
        extractor = AsyncExtractor(job_id)

        yield f"⏳ 正在提取知识点... (共{len(chapter_chunks)}个块)"

        extraction_results = extractor.extract_batch(chapter_chunks)

        # 构建图谱
        nodes = []
        edges = []
        node_id_counter = 0

        for result in extraction_results["results"]:
            if result.get("status") != "success":
                continue

            chunk_id = result["chunk_id"]

            for concept in result.get("concepts", []):
                nodes.append({
                    "id": f"node_{node_id_counter}",
                    "label": concept["name"],
                    "type": concept.get("type", "concept"),
                    "definition": concept.get("definition", ""),
                    "source_chunks": [chunk_id]
                })
                node_id_counter += 1

            for relation in result.get("relationships", []):
                source_node = next((n for n in nodes if n["label"] == relation["source"]), None)
                target_node = next((n for n in nodes if n["label"] == relation["target"]), None)

                if source_node and target_node:
                    edges.append({
                        "source": source_node["id"],
                        "target": target_node["id"],
                        "relation": relation["type"],
                        "description": relation.get("description", "")
                    })

        graph = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "chunks_processed": extraction_results["success_count"]
            }
        }

        # 保存图谱
        graph_path = get_job_dir(job_id) / "knowledge_graph.json"
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)

        result = f"""✅ 知识图谱构建成功！

**节点数**: {len(nodes)}
**边数**: {len(edges)}
**处理块数**: {extraction_results["success_count"]}
**缓存命中**: {extraction_results["cached_count"]}

请点击"去重整合"继续。
"""
        yield result

    except Exception as e:
        yield f"❌ 构建失败: {str(e)}"


def integrate_and_report(job_id):
    """去重整合并生成报告"""
    if not job_id:
        return "❌ 请先构建知识图谱", ""

    try:
        # 加载图谱
        graph_path = get_job_dir(job_id) / "knowledge_graph.json"
        with open(graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)

        # 去重
        deduplicated = deduplicate_knowledge_graph(graph)

        # 保存去重后的图谱
        dedup_path = get_job_dir(job_id) / "deduplicated_graph.json"
        with open(dedup_path, 'w', encoding='utf-8') as f:
            json.dump(deduplicated, f, ensure_ascii=False, indent=2)

        # 加载chunks
        chunks_path = get_job_dir(job_id) / "parsed_chunks.json"
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        # 生成报告
        chapter_info = {
            "textbook": "上传的教材",
            "title": "第一章",
            "start_page": 1,
            "end_page": 50,
            "chunk_count": len(chunks),
            "processed_chunks": len(chunks)
        }

        report_path = generate_integration_report(chunks, graph, deduplicated, job_id, chapter_info)

        # 读取报告内容
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()

        # 计算压缩比
        original_chars = sum(len(c.get("content", "")) for c in chunks)
        deduplicated_chars = sum(
            len(node.get("definition", "")) + len(node["label"])
            for node in deduplicated["nodes"]
        )
        compression_ratio = (deduplicated_chars / original_chars * 100) if original_chars > 0 else 0

        result = f"""✅ 整合完成！

**原始节点**: {len(graph["nodes"])}
**去重后节点**: {len(deduplicated["nodes"])}
**压缩比**: {compression_ratio:.1f}%
**是否达标**: {'✅ 是' if compression_ratio <= 30 else '❌ 否'}

报告已生成，请查看下方内容。
"""

        return result, report_content

    except Exception as e:
        return f"❌ 整合失败: {str(e)}", ""


def build_rag_and_query(job_id, question):
    """构建RAG索引并查询"""
    if not job_id:
        return "❌ 请先完成前面的步骤"

    if not question:
        return "❌ 请输入问题"

    try:
        # 加载chunks
        chunks_path = get_job_dir(job_id) / "parsed_chunks.json"
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        # 构建RAG索引
        pipeline = RAGPipeline()
        pipeline.build_index(chunks)
        pipeline.save_index(job_id)

        # 查询
        result = pipeline.query(question, top_k=3)

        # 格式化输出
        answer = f"""**问题**: {result['question']}

**回答**: {result['answer']}

**引用来源**:
"""
        for i, citation in enumerate(result['citations'], 1):
            answer += f"\n{i}. 教材: {citation['textbook']}, 页码: {citation['page']}\n   内容: {citation['content'][:100]}...\n"

        return answer

    except Exception as e:
        return f"❌ 查询失败: {str(e)}"


# 创建Gradio界面
with gr.Blocks(title="医学教材知识整合系统", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏥 医学教材知识整合智能体

    **功能**: 对医学教材进行知识整合，构建可视化知识图谱，实现跨教材去重提纯和RAG精准问答。

    **目标**: 将教材压缩到不超过原始体量30%的精华版本，且教学效果不打折。
    """)

    with gr.Tab("📚 文档处理"):
        with gr.Row():
            with gr.Column():
                file_input = gr.File(label="上传教材文件 (PDF/TXT/MD/DOCX)", file_types=[".pdf", ".txt", ".md", ".docx"])
                parse_btn = gr.Button("📖 解析文档", variant="primary")

            with gr.Column():
                parse_output = gr.Textbox(label="解析结果", lines=10)
                job_id_state = gr.Textbox(label="Job ID (自动生成)", interactive=False)

        parse_btn.click(
            fn=upload_and_parse,
            inputs=[file_input],
            outputs=[parse_output, job_id_state]
        )

    with gr.Tab("🕸️ 知识图谱"):
        with gr.Row():
            with gr.Column():
                chapter_num = gr.Slider(minimum=1, maximum=10, value=1, step=1, label="选择章节")
                build_btn = gr.Button("🔨 构建知识图谱", variant="primary")

            with gr.Column():
                graph_output = gr.Textbox(label="构建结果", lines=10)

        build_btn.click(
            fn=build_graph,
            inputs=[job_id_state, chapter_num],
            outputs=[graph_output]
        )

    with gr.Tab("🔄 去重整合"):
        with gr.Row():
            with gr.Column():
                integrate_btn = gr.Button("🔄 去重整合并生成报告", variant="primary")

            with gr.Column():
                integrate_output = gr.Textbox(label="整合结果", lines=10)

        report_output = gr.Textbox(label="整合报告", lines=20)

        integrate_btn.click(
            fn=integrate_and_report,
            inputs=[job_id_state],
            outputs=[integrate_output, report_output]
        )

    with gr.Tab("💬 RAG问答"):
        with gr.Row():
            with gr.Column():
                question_input = gr.Textbox(label="输入问题", placeholder="例如：什么是细胞膜？")
                query_btn = gr.Button("🔍 查询", variant="primary")

            with gr.Column():
                answer_output = gr.Textbox(label="回答（带引用）", lines=15)

        query_btn.click(
            fn=build_rag_and_query,
            inputs=[job_id_state, question_input],
            outputs=[answer_output]
        )

    gr.Markdown("""
    ---
    **使用流程**:
    1. 📚 上传教材文件并解析
    2. 🕸️ 构建知识图谱（选择章节）
    3. 🔄 去重整合并查看报告
    4. 💬 使用RAG进行问答

    **技术栈**: FastAPI + DeepSeek + sentence-transformers + FAISS + Gradio
    """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
