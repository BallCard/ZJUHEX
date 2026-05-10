// Demo data from real parsing results (03_生理学.pdf)
// 658 nodes, 607 edges extracted from actual textbook (50 chunks processed)

import graph50chunks from './graph_50chunks.json';

export const demoGraphData = graph50chunks;

// Legacy demo data (15 nodes, 12 edges) - kept for reference
export const legacyDemoGraphData = [
  {
    "data": {
      "id": "node_0",
      "label": "生理学",
      "category": "concept",
      "definition": "研究人体正常生理功能的科学，为医学提供正常参考值范围",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_1",
      "label": "医学",
      "category": "concept",
      "definition": "临床诊断、治疗、康复等实践领域，依赖生理学知识",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_2",
      "label": "细胞",
      "category": "concept",
      "definition": "构成人体最基本的结构和功能单位",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_3",
      "label": "组织",
      "category": "concept",
      "definition": "由不同细胞群构成的结构层次",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_4",
      "label": "器官",
      "category": "concept",
      "definition": "由多种组织有机组合构成的结构",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_5",
      "label": "系统",
      "category": "concept",
      "definition": "功能相关的器官组成的体系，各司其职并互相配合",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_6",
      "label": "消化系统",
      "category": "concept",
      "definition": "从外界摄取食物并进行消化和吸收的系统",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_7",
      "label": "循环系统",
      "category": "concept",
      "definition": "以血液为载体运输营养物质至全身的系统",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_8",
      "label": "呼吸系统",
      "category": "concept",
      "definition": "从外界摄取氧气并排出二氧化碳的系统",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_9",
      "label": "肾脏",
      "category": "concept",
      "definition": "通过滤过、重吸收和分泌排泄功能排出代谢产物的器官",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_10",
      "label": "神经和内分泌系统",
      "category": "concept",
      "definition": "对机体生理活动发挥调节和整合作用的系统",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_11",
      "label": "心电生理",
      "category": "concept",
      "definition": "研究心脏电活动的生理学分支",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_12",
      "label": "经导管射频消融技术",
      "category": "concept",
      "definition": "治疗心律失常的临床技术",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_13",
      "label": "诺贝尔生理学或医学奖",
      "category": "concept",
      "definition": "诺贝尔基金会设立的奖项，表彰生理学与医学领域的贡献",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "node_14",
      "label": "新陈代谢",
      "category": "concept",
      "definition": "细胞进行生命活动所需能量和原料的代谢过程",
      "textbook": "03_生理学.pdf",
      "source_page": 25,
      "source_chunk": "chunk_17",
      "neighbors": []
    }
  },
  {
    "data": {
      "id": "edge_0",
      "source": "node_0",
      "target": "node_1"
    }
  },
  {
    "data": {
      "id": "edge_1",
      "source": "node_0",
      "target": "node_11"
    }
  },
  {
    "data": {
      "id": "edge_2",
      "source": "node_11",
      "target": "node_12"
    }
  },
  {
    "data": {
      "id": "edge_3",
      "source": "node_2",
      "target": "node_3"
    }
  },
  {
    "data": {
      "id": "edge_4",
      "source": "node_3",
      "target": "node_4"
    }
  },
  {
    "data": {
      "id": "edge_5",
      "source": "node_4",
      "target": "node_5"
    }
  },
  {
    "data": {
      "id": "edge_6",
      "source": "node_6",
      "target": "node_14"
    }
  },
  {
    "data": {
      "id": "edge_7",
      "source": "node_7",
      "target": "node_6"
    }
  },
  {
    "data": {
      "id": "edge_8",
      "source": "node_8",
      "target": "node_14"
    }
  },
  {
    "data": {
      "id": "edge_9",
      "source": "node_9",
      "target": "node_14"
    }
  },
  {
    "data": {
      "id": "edge_10",
      "source": "node_10",
      "target": "node_5"
    }
  },
  {
    "data": {
      "id": "edge_11",
      "source": "node_0",
      "target": "node_13"
    }
  }
];

export const demoRAGResponses: Record<string, {
  question: string;
  answer: string;
  citations: Array<{
    textbook: string;
    page: number;
    content: string;
    relevance_score: number;
  }>;
}> = {
  "生理学": {
    question: "什么是生理学？",
    answer: "生理学是研究人体正常生理功能的科学，为医学提供正常参考值范围。\n\n生理学研究的核心内容包括：\n\n1. **人体结构层次**：从细胞、组织、器官到系统的层次化组织\n2. **主要系统功能**：\n   - 消化系统：摄取食物并进行消化和吸收\n   - 循环系统：以血液为载体运输营养物质\n   - 呼吸系统：摄取氧气并排出二氧化碳\n   - 肾脏：通过滤过、重吸收和分泌排泄代谢产物\n3. **调节机制**：神经和内分泌系统对机体生理活动的调节和整合\n4. **新陈代谢**：细胞进行生命活动所需能量和原料的代谢过程\n\n生理学知识是医学临床诊断、治疗、康复等实践领域的基础。",
    citations: [
      {
        textbook: "03_生理学.pdf",
        page: 25,
        content: "生理学是研究人体正常生理功能的科学，为医学提供正常参考值范围。人体由细胞、组织、器官和系统组成，各系统相互配合维持生命活动。",
        relevance_score: 0.98
      },
      {
        textbook: "03_生理学.pdf",
        page: 25,
        content: "消化系统从外界摄取食物并进行消化和吸收，循环系统以血液为载体运输营养物质至全身，呼吸系统从外界摄取氧气并排出二氧化碳。",
        relevance_score: 0.92
      },
      {
        textbook: "03_生理学.pdf",
        page: 25,
        content: "神经和内分泌系统对机体生理活动发挥调节和整合作用，维持内环境稳态。",
        relevance_score: 0.88
      }
    ]
  },
  "心电生理": {
    question: "什么是心电生理？",
    answer: "心电生理是研究心脏电活动的生理学分支。\n\n**研究内容**：\n- 心脏电信号的产生和传导机制\n- 心肌细胞的电生理特性\n- 心律的调控机制\n\n**临床应用**：\n心电生理学的发展催生了经导管射频消融技术，这是一种治疗心律失常的临床技术。通过导管将射频能量传递到心脏特定部位，消融异常电活动的组织，从而治疗心律失常。\n\n**学术地位**：\n心电生理学的研究成果多次获得诺贝尔生理学或医学奖，体现了该领域对医学发展的重要贡献。",
    citations: [
      {
        textbook: "03_生理学.pdf",
        page: 25,
        content: "心电生理是研究心脏电活动的生理学分支，为理解心律失常的发生机制提供理论基础。",
        relevance_score: 0.96
      },
      {
        textbook: "03_生理学.pdf",
        page: 25,
        content: "经导管射频消融技术是治疗心律失常的临床技术，基于心电生理学原理，通过消融异常电活动组织达到治疗目的。",
        relevance_score: 0.91
      }
    ]
  },
  "default": {
    question: "",
    answer: "这是基于真实解析的生理学教材演示数据（146个概念节点，136条关系边）。\n\n**数据来源**：\n- 教材：03_生理学.pdf\n- 处理：前10个文档块\n- 提取：162个原始节点\n- 去重：146个整合节点（去重率9.88%）\n- 压缩比：0.78%（远超≤30%目标）\n\n**功能演示**：\n您可以尝试询问：\n- 什么是生理学？\n- 什么是心电生理？\n- 人体有哪些主要系统？\n\n或者点击图谱中的节点查看详细定义。连接真实后端可获得完整的AI问答功能。",
    citations: []
  }
};
