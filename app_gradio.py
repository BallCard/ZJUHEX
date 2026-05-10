"""
Gradio wrapper for ModelScope deployment
将FastAPI后端包装成Gradio界面
"""
import gradio as gr
import requests
import json

# Railway后端API
API_BASE = "https://web-production-8f412.up.railway.app"

def upload_and_process(file):
    """上传并处理教材"""
    if file is None:
        return "请上传PDF文件"

    try:
        # 上传文件
        files = {'file': open(file.name, 'rb')}
        response = requests.post(f"{API_BASE}/api/upload", files=files)
        result = response.json()

        if response.status_code != 200:
            return f"上传失败: {result.get('detail', '未知错误')}"

        job_id = result['job_id']
        filename = result['filename']

        return f"✅ 上传成功！\n文件名: {filename}\nJob ID: {job_id}\n\n请使用此Job ID进行后续操作"

    except Exception as e:
        return f"错误: {str(e)}"

def parse_textbook(job_id):
    """解析教材"""
    try:
        response = requests.post(f"{API_BASE}/api/parse", json={"job_id": job_id})
        result = response.json()

        if response.status_code != 200:
            return f"解析失败: {result.get('detail', '未知错误')}"

        chunks = result.get('chunks_count', 0)
        total_chars = result.get('total_chars', 0)

        return f"✅ 解析完成！\n分块数: {chunks}\n总字符数: {total_chars}"

    except Exception as e:
        return f"错误: {str(e)}"

def build_knowledge_graph(job_id, max_chunks):
    """构建知识图谱"""
    try:
        response = requests.post(
            f"{API_BASE}/api/build_graph",
            json={"job_id": job_id, "max_chunks": max_chunks}
        )
        result = response.json()

        if response.status_code != 200:
            return f"构建失败: {result.get('detail', '未知错误')}"

        nodes = result.get('nodes_count', 0)
        edges = result.get('edges_count', 0)

        return f"✅ 知识图谱构建完成！\n节点数: {nodes}\n边数: {edges}"

    except Exception as e:
        return f"错误: {str(e)}"

def integrate_knowledge(job_id):
    """整合去重"""
    try:
        response = requests.post(f"{API_BASE}/api/integrate", json={"job_id": job_id})
        result = response.json()

        if response.status_code != 200:
            return f"整合失败: {result.get('detail', '未知错误')}"

        original = result.get('original_nodes', 0)
        deduplicated = result.get('deduplicated_nodes', 0)
        removed = result.get('removed_count', 0)

        return f"✅ 整合完成！\n原始节点: {original}\n去重后: {deduplicated}\n移除: {removed}"

    except Exception as e:
        return f"错误: {str(e)}"

def rag_query(job_id, question):
    """RAG问答"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rag/query",
            json={"job_id": job_id, "query": question}
        )
        result = response.json()

        if response.status_code != 200:
            return f"查询失败: {result.get('detail', '未知错误')}"

        answer = result.get('answer', '')
        sources = result.get('sources', [])

        output = f"📝 回答:\n{answer}\n\n📚 来源:\n"
        for i, source in enumerate(sources, 1):
            output += f"{i}. {source.get('textbook', 'Unknown')} - 第{source.get('page', 'N/A')}页\n"

        return output

    except Exception as e:
        return f"错误: {str(e)}"

# 创建Gradio界面
with gr.Blocks(title="医学教材知识整合系统") as demo:
    gr.Markdown("# 🏥 医学教材知识整合智能体")
    gr.Markdown("基于FastAPI + RAG的医学教材知识整合系统")

    with gr.Tab("1. 上传教材"):
        file_input = gr.File(label="上传PDF教材", file_types=[".pdf"])
        upload_btn = gr.Button("上传", variant="primary")
        upload_output = gr.Textbox(label="上传结果", lines=5)
        upload_btn.click(upload_and_process, inputs=[file_input], outputs=[upload_output])

    with gr.Tab("2. 解析教材"):
        parse_job_id = gr.Textbox(label="Job ID", placeholder="输入上一步获得的Job ID")
        parse_btn = gr.Button("解析", variant="primary")
        parse_output = gr.Textbox(label="解析结果", lines=5)
        parse_btn.click(parse_textbook, inputs=[parse_job_id], outputs=[parse_output])

    with gr.Tab("3. 构建知识图谱"):
        graph_job_id = gr.Textbox(label="Job ID")
        max_chunks_input = gr.Slider(minimum=5, maximum=50, value=10, step=5, label="处理块数")
        graph_btn = gr.Button("构建图谱", variant="primary")
        graph_output = gr.Textbox(label="构建结果", lines=5)
        graph_btn.click(build_knowledge_graph, inputs=[graph_job_id, max_chunks_input], outputs=[graph_output])

    with gr.Tab("4. 整合去重"):
        integrate_job_id = gr.Textbox(label="Job ID")
        integrate_btn = gr.Button("整合", variant="primary")
        integrate_output = gr.Textbox(label="整合结果", lines=5)
        integrate_btn.click(integrate_knowledge, inputs=[integrate_job_id], outputs=[integrate_output])

    with gr.Tab("5. RAG问答"):
        rag_job_id = gr.Textbox(label="Job ID")
        question_input = gr.Textbox(label="问题", placeholder="输入你的问题...")
        rag_btn = gr.Button("提问", variant="primary")
        rag_output = gr.Textbox(label="回答", lines=10)
        rag_btn.click(rag_query, inputs=[rag_job_id, question_input], outputs=[rag_output])

    gr.Markdown("---")
    gr.Markdown("💡 **使用说明**: 按照标签页顺序依次操作，每步完成后记录Job ID用于下一步")
    gr.Markdown("🔗 **后端API**: https://web-production-8f412.up.railway.app")
    gr.Markdown("📦 **GitHub**: https://github.com/BallCard/ZJUHEX")

if __name__ == "__main__":
    demo.launch()
