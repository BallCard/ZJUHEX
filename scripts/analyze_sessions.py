#!/usr/bin/env python3
"""分析Claude Code session对话记录"""
import json
import sys
from pathlib import Path
from datetime import datetime

def parse_jsonl(file_path):
    """解析JSONL文件"""
    messages = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
    return messages

def extract_user_messages(messages):
    """提取用户消息"""
    user_msgs = []
    for msg in messages:
        if isinstance(msg, dict):
            # 查找用户消息
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if isinstance(content, str):
                    user_msgs.append(content)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            user_msgs.append(item.get('text', ''))
    return user_msgs

def extract_assistant_actions(messages):
    """提取AI的关键操作"""
    actions = []
    for msg in messages:
        if isinstance(msg, dict):
            if msg.get('role') == 'assistant':
                content = msg.get('content', [])
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            # 工具调用
                            if item.get('type') == 'tool_use':
                                tool_name = item.get('name', '')
                                actions.append(f"Tool: {tool_name}")
                            # 文本输出
                            elif item.get('type') == 'text':
                                text = item.get('text', '')
                                if text and len(text) > 50:
                                    actions.append(f"Response: {text[:100]}...")
    return actions

def analyze_session(file_path):
    """分析单个session"""
    messages = parse_jsonl(file_path)
    if not messages:
        return None

    user_msgs = extract_user_messages(messages)
    actions = extract_assistant_actions(messages)

    return {
        'file': file_path.name,
        'total_messages': len(messages),
        'user_messages': user_msgs,
        'actions_count': len(actions),
        'sample_actions': actions[:10]  # 前10个操作
    }

def main():
    base_dir = Path(r"C:\Users\12855\.claude\projects\D--Workspace-competitions-Hex")

    # 今天9点到18点的session文件
    target_sessions = [
        "e8883037-934c-4f45-adc7-0237691592e9.jsonl",  # 08:56
        "2142b292-bac6-4f66-a97a-6927e8cc100a.jsonl",  # 10:24
        "f687d62d-dc99-40f1-b066-bb975d52e7c8.jsonl",  # 10:28
        "3751d50d-2a3f-4da2-8092-b5a7a96b9d36.jsonl",  # 11:43
        "6f1396be-161e-49ea-bdab-bc8c41513a39.jsonl",  # 11:47
        "1172fafc-f220-4bda-bdd7-aed6a51c9439.jsonl",  # 11:59
        "0ff9dcd9-fe92-493a-ac1e-43f7aa648700.jsonl",  # 13:47
        "eb6de183-d9f1-4038-afd9-842c40d7415c.jsonl",  # 16:25
        "626e0099-0c15-4317-b2cd-bf2e2668a72a.jsonl",  # 16:41
        "9d4d3ed9-6cd2-4c57-a22b-90adccd2f5f0.jsonl",  # 16:47
        "a5e27598-8f10-45df-9daa-5d0b3c7f6849.jsonl",  # 17:37
        "54e421ef-3434-42ee-9669-5ac6990415a4.jsonl",  # 17:59
        "af607259-911a-4055-bc39-56895caa764f.jsonl",  # 18:06
        "5438a2c4-115f-465e-977d-52570cd38903.jsonl",  # 18:10
    ]

    print("=" * 80)
    print("今日开发总结 - Session分析")
    print("=" * 80)
    print()

    for session_file in target_sessions:
        file_path = base_dir / session_file
        if not file_path.exists():
            continue

        print(f"\n{'='*80}")
        print(f"Session: {session_file}")
        print(f"{'='*80}")

        result = analyze_session(file_path)
        if result:
            print(f"总消息数: {result['total_messages']}")
            print(f"用户消息数: {len(result['user_messages'])}")
            print(f"\n用户请求:")
            for i, msg in enumerate(result['user_messages'][:5], 1):  # 只显示前5条
                print(f"  {i}. {msg[:200]}")
                if len(msg) > 200:
                    print(f"     ...")

            if len(result['user_messages']) > 5:
                print(f"  ... (还有 {len(result['user_messages']) - 5} 条消息)")

if __name__ == "__main__":
    main()
