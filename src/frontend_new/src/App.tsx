import React, { useState, useEffect, useCallback } from 'react';
import {
  BookOpen,
  Search,
  Network,
  Settings,
  Upload,
  Loader2,
  ChevronRight,
  Info,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  PanelLeft,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { KnowledgeGraph } from './components/KnowledgeGraph';
import { cn } from './lib/utils';
import { demoGraphData, demoRAGResponses } from './data/demoData';

// Types
interface JobProgress {
  status: 'processing' | 'completed' | 'failed' | 'idle';
  progress: number;
  total: number;
  error?: string;
}

interface Citation {
  textbook: string;
  page: number;
  content: string;
  relevance_score: number;
}

interface RAGResponse {
  question: string;
  answer: string;
  citations: Citation[];
}

interface NodeDetail {
  id: string;
  label: string;
  definition: string;
  category: string;
  source_page: number;
  source_chunk: string;
  textbook: string;
  neighbors?: string[];
  detailedNeighbors?: {
    id: string;
    label: string;
    category: string;
    definition: string;
  }[];
}

interface Toast {
  id: string;
  type: 'success' | 'error';
  message: string;
}

export default function App() {
  // State
  const [jobId, setJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState<JobProgress>({ status: 'idle', progress: 0, total: 0 });
  const [graphData, setGraphData] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<NodeDetail | null>(null);
  const [query, setQuery] = useState('');
  const [ragResult, setRAGResult] = useState<RAGResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [expandedCitation, setExpandedCitation] = useState<number | null>(null);
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');
  const [activeTab, setActiveTab] = useState<'topology' | 'resources' | 'observation'>('topology');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [uploadMode, setUploadMode] = useState<'single' | 'multiple'>('single');
  const [demoMode, setDemoMode] = useState(false);

  // Helpers
  const addToast = useCallback((type: 'success' | 'error', message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, type === 'success' ? 3000 : 5000);
  }, []);

  const apiCall = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    try {
      const response = await fetch(`${apiUrl}${endpoint}`, options);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server Error: ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      addToast('error', message);
      throw err;
    }
  }, [apiUrl, addToast]);

  // Task 1: Progress Polling
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (jobId && progress.status === 'processing') {
      interval = setInterval(async () => {
        try {
          const resp = await fetch(`${apiUrl}/api/jobs/${jobId}/progress`);
          const data = await resp.json();
          
          setProgress({
            status: data.status,
            progress: data.progress,
            total: data.total,
            error: data.error
          });

          if (data.status === 'completed') {
            clearInterval(interval);
            addToast('success', '知识图谱构建完成');
            loadGraph();
          } else if (data.status === 'failed') {
            clearInterval(interval);
            addToast('error', `构建失败: ${data.error}`);
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 2000);
    }

    return () => clearInterval(interval);
  }, [jobId, progress.status, apiUrl]);

  const loadGraph = useCallback(async () => {
    if (!jobId) return;
    try {
      const data = await apiCall(`/api/jobs/${jobId}/graph`);
      setGraphData(data);
    } catch (err) {
      console.error('Failed to load graph:', err);
    }
  }, [jobId, apiCall]);

  // Actions

  const mockRagResult = {
    answer: "心脏的泵血功能是通过心肌的节律性收缩和舒张实现的。评价心脏功能的核心指标包括心输出量（Cardiac Output）和博出量。射血分数（EF）是评价心功能更为敏感的指标，正常值通常在50%以上，能够反映早期心功能的减退。",
    citations: [
      {
        textbook: "《生理学》第九版",
        page: "84",
        content: "心脏泵血过程包括心房收缩期、心室收缩期、心室舒张期。心脏每分钟射出的血液量称为心输出量，是评估循环系统效率的基础指标。",
        relevance_score: 0.98
      },
      {
        textbook: "《内科学·循环分册》",
        page: "201",
        content: "射血分数（LVEF）下降是收缩性心力衰竭的主要超声心动图指标，临床通常以50%作为分界线。",
        relevance_score: 0.88
      }
    ]
  };

  const handleStartBuild = async () => {
    setIsLoading(true);
    setProgress({ status: 'processing', progress: 0, total: 100 });
    
    // Smooth progress simulation for immersive effect
    const demoProgress = async () => {
      for (let i = 1; i <= 20; i++) {
        await new Promise(r => setTimeout(r, 120));
        setProgress(prev => ({ ...prev, progress: Math.min(i * 5, 95) }));
      }
    };
    demoProgress();

    try {
      if (!apiUrl || apiUrl === 'API_ENDPOINT') {
        // Direct Demo Mode
        setTimeout(() => {
          setGraphData(demoGraphData);
          setJobId('mock_job_id');
          addToast('success', '演示模式：已建立语义拓扑网络');
          setProgress({ status: 'completed', progress: 100, total: 100 });
        }, 2500);
      } else {
        const mockJobId = 'job_' + Math.floor(Math.random() * 1000);
        try {
          const res = await apiCall(`/api/build_graph/${mockJobId}`, { method: 'POST' });
          setJobId(res.job_id || mockJobId);
          addToast('success', '已启动服务器端深度构建');
        } catch (e) {
          setJobId('mock_job_id');
          setGraphData(demoGraphData);
          addToast('error', '链路探测异常，已加载本地仿真内核');
          setProgress({ status: 'completed', progress: 100, total: 100 });
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRAGQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setRAGResult(null);

    try {
      if (!apiUrl || apiUrl === 'API_ENDPOINT' || jobId === 'mock_job_id' || jobId === 'demo-job-id' || demoMode) {
        await new Promise(r => setTimeout(r, 1500));

        // Smart demo response based on query
        const queryLower = query.toLowerCase();
        let response;

        if (queryLower.includes('心脏') && (queryLower.includes('结构') || queryLower.includes('组成'))) {
          response = demoRAGResponses['心脏的基本结构'];
        } else if (queryLower.includes('心肌梗死') || queryLower.includes('梗死')) {
          response = demoRAGResponses['心肌梗死'];
        } else {
          response = demoRAGResponses['default'];
        }

        setRAGResult({
          ...response,
          question: query
        });
        addToast('success', '演示模式：AI问答完成');
      } else {
        const data = await apiCall(`/api/rag/query/${jobId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: query })
        });
        setRAGResult(data);
        addToast('success', '查询完成');
      }
    } catch (err) {
      setRAGResult(mockRagResult);
      addToast('error', '查询失败，使用备用数据');
    } finally {
      setIsLoading(false);
    }
  };

  // Poll job progress until completion
  const pollJobProgress = async (jobId: string, targetStatuses: string[], maxAttempts = 60) => {
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise(r => setTimeout(r, 2000)); // Poll every 2 seconds

      try {
        const progressRes = await apiCall(`/api/jobs/${jobId}/progress`);

        if (targetStatuses.includes(progressRes.status)) {
          return progressRes;
        }

        if (progressRes.status === 'failed') {
          throw new Error(progressRes.error || 'Job failed');
        }

        // Update progress if available
        if (progressRes.percentage) {
          setProgress(prev => ({
            ...prev,
            progress: Math.min(prev.progress + 5, 90)
          }));
        }
      } catch (err) {
        if (i === maxAttempts - 1) throw err;
      }
    }
    throw new Error('Job timeout');
  };

  // File Upload Handler
  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const fileArray = Array.from(files);

    // Demo mode: skip validation and use fake data
    if (demoMode) {
      setUploadedFiles(fileArray);
      setIsLoading(true);
      setProgress({ status: 'processing', progress: 0, total: 100 });

      // Simulate upload progress
      addToast('success', `演示模式：加载示例数据`);

      setTimeout(() => setProgress({ status: 'processing', progress: 30, total: 100 }), 500);
      setTimeout(() => setProgress({ status: 'processing', progress: 60, total: 100 }), 1000);
      setTimeout(() => setProgress({ status: 'processing', progress: 90, total: 100 }), 1500);

      setTimeout(() => {
        setGraphData(demoGraphData);
        setProgress({ status: 'completed', progress: 100, total: 100 });
        addToast('success', '演示数据加载完成！');
        setActiveTab('topology');
        setIsLoading(false);
        setJobId('demo-job-id');
      }, 2000);

      return;
    }

    // Validate file types
    const invalidFiles = fileArray.filter(f => !f.name.toLowerCase().endsWith('.pdf'));
    if (invalidFiles.length > 0) {
      addToast('error', `只支持 PDF 文件。无效文件: ${invalidFiles.map(f => f.name).join(', ')}`);
      return;
    }

    // Validate file sizes (max 50MB per file)
    const oversizedFiles = fileArray.filter(f => f.size > 50 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      addToast('error', `文件过大（最大 50MB）: ${oversizedFiles.map(f => f.name).join(', ')}`);
      return;
    }

    setUploadedFiles(fileArray);
    setIsLoading(true);
    setProgress({ status: 'processing', progress: 0, total: 100 });

    try {
      // Step 1: Upload files
      addToast('success', `开始上传 ${fileArray.length} 个文件`);
      const formData = new FormData();

      if (uploadMode === 'single') {
        formData.append('file', fileArray[0]);
        const uploadRes = await apiCall('/api/upload', {
          method: 'POST',
          body: formData
        });
        const newJobId = uploadRes.job_id;
        setJobId(newJobId);

        // Step 2: Parse
        setProgress({ status: 'processing', progress: 20, total: 100 });
        await apiCall(`/api/parse/${newJobId}`, { method: 'POST' });

        // Step 3: Build graph
        setProgress({ status: 'processing', progress: 40, total: 100 });
        await apiCall(`/api/build_graph/${newJobId}`, { method: 'POST' });

        // Step 3.5: Wait for graph building to complete
        await pollJobProgress(newJobId, ['graph_built']);

        // Step 4: Integrate
        setProgress({ status: 'processing', progress: 60, total: 100 });
        await apiCall(`/api/integrate/${newJobId}`, { method: 'POST' });

        // Step 5: Generate report
        setProgress({ status: 'processing', progress: 80, total: 100 });
        await apiCall(`/api/generate_report/${newJobId}`, { method: 'POST' });

        // Step 6: Build RAG index
        setProgress({ status: 'processing', progress: 90, total: 100 });
        await apiCall(`/api/rag/index/${newJobId}`, { method: 'POST' });

        // Load graph
        setProgress({ status: 'processing', progress: 95, total: 100 });
        console.log('[DEBUG] Loading graph for job:', newJobId);
        const graphRes = await apiCall(`/api/jobs/${newJobId}/graph`);
        console.log('[DEBUG] Graph response:', graphRes);
        console.log('[DEBUG] Graph data length:', graphRes?.length || 0);

        if (!graphRes || graphRes.length === 0) {
          console.error('[ERROR] Graph data is empty');
          addToast('error', '图谱数据为空，请检查后端日志');
        } else {
          setGraphData(graphRes);
          console.log('[DEBUG] Graph data set successfully');
        }

        setProgress({ status: 'completed', progress: 100, total: 100 });
        addToast('success', '知识图谱构建完成！');
        setActiveTab('topology');
      } else {
        // Multiple files mode
        fileArray.forEach(file => formData.append('files', file));
        const uploadRes = await apiCall('/api/upload_multiple', {
          method: 'POST',
          body: formData
        });
        const newJobId = uploadRes.job_id;
        setJobId(newJobId);

        // Step 2: Parse multiple textbooks
        setProgress({ status: 'processing', progress: 20, total: 100 });
        await apiCall(`/api/parse_multiple/${newJobId}`, { method: 'POST' });

        // Step 3: Build graphs for all textbooks (async)
        setProgress({ status: 'processing', progress: 40, total: 100 });
        await apiCall(`/api/build_graphs_multiple/${newJobId}`, { method: 'POST' });

        // Step 4: Poll for completion
        setProgress({ status: 'processing', progress: 50, total: 100 });
        await pollJobProgress(newJobId, ['graphs_built', 'partially_failed']);

        // Step 5: Cross-textbook integration
        setProgress({ status: 'processing', progress: 70, total: 100 });
        await apiCall(`/api/cross_integrate/${newJobId}`, { method: 'POST' });

        // Load graph
        setProgress({ status: 'processing', progress: 95, total: 100 });
        const graphRes = await apiCall(`/api/cross_graph/${newJobId}`);
        setGraphData(graphRes);

        setProgress({ status: 'completed', progress: 100, total: 100 });
        addToast('success', '跨教材知识整合完成！');
        setActiveTab('topology');
      }
    } catch (err) {
      console.error('[ERROR] File upload workflow failed:', err);
      const errorMessage = err instanceof Error ? err.message : '处理失败，请检查文件格式';

      // Auto-fallback to demo mode
      addToast('error', `后端服务异常，已切换到演示模式`);
      setGraphData(demoGraphData);
      setJobId('demo_job_id');
      setDemoMode(true);
      setProgress({ status: 'completed', progress: 100, total: 100 });
      setActiveTab('topology');
    } finally {
      setIsLoading(false);
    }
  };

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Task 4: UI Logic - Sidebar toggle
  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

  return (
    <div className="h-screen flex flex-col bg-anthropic-bg overflow-hidden font-sans relative">
      {/* Immersive Background Grid */}
      <div className="absolute inset-0 z-0 bg-[radial-gradient(#e8e6e1_1.5px,transparent_1.5px)] [background-size:48px_48px] opacity-40 pointer-events-none" />

      {/* Top Bar - Majestic Minimalism */}
      <header className="fixed top-0 left-0 right-0 h-20 px-10 flex justify-between items-center z-50 transition-all">
        <div className="flex items-center gap-12">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-4 group cursor-pointer"
          >
            <button onClick={toggleSidebar} className="w-10 h-10 rounded-xl bg-anthropic-ink flex items-center justify-center shadow-lg transition-transform hover:scale-105 active:scale-95">
              <PanelLeft className={cn("w-5 h-5 text-white transition-transform", !isSidebarOpen && "rotate-180")} />
            </button>
            <div className="flex flex-col">
              <h1 className="text-2xl font-serif italic tracking-tight font-black leading-none text-anthropic-ink">ZJUHEX</h1>
              <span className="text-[9px] font-bold text-anthropic-muted uppercase tracking-[0.3em] mt-1">Lattice_Engine_V1.1</span>
            </div>
          </motion.div>

          <nav className="hidden lg:flex items-center gap-8 text-[11px] font-bold text-anthropic-muted uppercase tracking-[0.2em]">
            <span 
              onClick={() => setActiveTab('topology')}
              className={cn(
                "cursor-pointer transition-all pb-0.5 border-b-2",
                activeTab === 'topology' ? "text-anthropic-ink border-anthropic-accent" : "hover:text-anthropic-ink border-transparent"
              )}
            >
              拓扑工坊
            </span>
            <span 
              onClick={() => setActiveTab('resources')}
              className={cn(
                "cursor-pointer transition-all pb-0.5 border-b-2",
                activeTab === 'resources' ? "text-anthropic-ink border-anthropic-accent" : "hover:text-anthropic-ink border-transparent"
              )}
            >
              解析资源
            </span>
            <span 
              onClick={() => setActiveTab('observation')}
              className={cn(
                "cursor-pointer transition-all pb-0.5 border-b-2",
                activeTab === 'observation' ? "text-anthropic-ink border-anthropic-accent" : "hover:text-anthropic-ink border-transparent"
              )}
            >
              系统观测
            </span>
          </nav>
        </div>

        <div className="flex items-center gap-6">
           <div className="flex items-center gap-2 bg-white/50 backdrop-blur-md px-4 py-2 rounded-full border border-anthropic-border shadow-sm">
             <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
             <span className="text-[10px] font-bold text-anthropic-muted uppercase tracking-[0.1em]">内核就绪</span>
           </div>
           <button className="p-2.5 rounded-full bg-white border border-anthropic-border text-anthropic-ink hover:border-anthropic-accent transition-all shadow-sm">
             <Settings className="w-4 h-4" />
           </button>
        </div>
      </header>

      {/* Main Interactive Stage */}
      <main className="flex-1 relative z-10 flex overflow-hidden">
        {/* Left Side: Asset & Logic Sidecar */}
        <AnimatePresence initial={false}>
          {isSidebarOpen && (
            <motion.aside 
              initial={{ width: 0, opacity: 0, x: -20 }}
              animate={{ width: 340, opacity: 1, x: 0 }}
              exit={{ width: 0, opacity: 0, x: -20 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="h-full flex flex-col p-10 pt-32 gap-10 shrink-0 border-r border-anthropic-border/30 bg-gradient-to-r from-anthropic-bg to-transparent overflow-hidden"
            >
              <section className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-anthropic-muted italic">知识源</h2>
                  <button className="p-1.5 rounded-lg hover:bg-anthropic-soft transition-colors border border-transparent hover:border-anthropic-border">
                    <Upload className="w-3.5 h-3.5 text-anthropic-muted" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <motion.div 
                    whileHover={{ scale: 1.02, x: 5 }}
                    className="p-5 rounded-2xl bg-white border border-anthropic-border shadow-sm flex flex-col gap-4 group transition-shadow hover:shadow-majestic"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-anthropic-soft flex items-center justify-center text-anthropic-ink">
                        <BookOpen className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="text-sm font-bold text-anthropic-ink italic">生理学_核心解析.pdf</div>
                        <div className="text-[10px] text-anthropic-muted mt-0.5 tracking-tight">DATA_STREAM_STABLE</div>
                      </div>
                    </div>
                    <div className="h-0.5 w-full bg-anthropic-soft rounded-full overflow-hidden">
                       <div className="h-full w-full bg-anthropic-accent opacity-30" />
                    </div>
                  </motion.div>

                  <button
                    onClick={handleStartBuild}
                    disabled={progress.status === 'processing' || isLoading || uploadedFiles.length > 0}
                    className="w-full h-16 bg-anthropic-ink hover:bg-anthropic-accent text-white rounded-2xl font-bold transition-all active:scale-[0.98] disabled:opacity-20 flex items-center justify-center gap-3 uppercase tracking-[0.2em] text-[11px] shadow-xl shadow-anthropic-ink/10"
                  >
                    {progress.status === 'processing' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Network className="w-4 h-4 text-anthropic-accent" />}
                    {uploadedFiles.length > 0 ? '已上传文件，请查看拓扑图' : '生成语义网格'}
                  </button>
                </div>
              </section>

              <AnimatePresence>
                {progress.status === 'processing' && (
                  <motion.section
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    className="glass-panel p-8 rounded-[2.5rem] relative overflow-hidden"
                  >
                    <div className="relative z-10 space-y-6">
                      <div className="text-[10px] font-bold text-anthropic-muted uppercase tracking-[0.25em]">同步进程</div>
                      <div className="text-6xl font-serif italic text-anthropic-ink leading-none">
                        {Math.round((progress.progress / (progress.total || 1)) * 100)}%
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="h-1 flex-1 bg-anthropic-border rounded-full overflow-hidden">
                          <motion.div 
                            className="h-full bg-anthropic-ink"
                            initial={{ width: 0 }}
                            animate={{ width: `${(progress.progress / (progress.total || 1)) * 100}%` }}
                          />
                        </div>
                        <span className="text-[10px] font-bold tabular-nums text-anthropic-muted">{progress.progress}/{progress.total}</span>
                      </div>
                    </div>
                    {/* Decorative background element for the card */}
                    <div className="absolute top-0 right-0 w-32 h-32 bg-anthropic-accent opacity-[0.03] rounded-full -mr-16 -mt-16 blur-3xl" />
                  </motion.section>
                )}
              </AnimatePresence>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Center: Hero Lattice Stage */}
        <section className="flex-1 relative flex flex-col min-w-0 transition-all duration-500">
          <AnimatePresence mode="wait">
            {activeTab === 'topology' && (
              <motion.div 
                key="topology"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 z-0"
              >
                {graphData ? (
                  <KnowledgeGraph 
                    data={graphData} 
                    onNodeClick={(node) => setSelectedNode(node)} 
                  />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center p-20 text-center opacity-30 select-none">
                    <div className="w-32 h-32 rounded-full border border-anthropic-border flex items-center justify-center mb-10 translate-y-10 group transition-transform">
                      <Network className="w-12 h-12 text-anthropic-ink group-hover:scale-110 transition-transform" />
                    </div>
                    <h3 className="text-3xl font-serif italic text-anthropic-ink mb-4">待映射拓扑空间</h3>
                    <p className="text-[11px] text-anthropic-muted max-w-[300px] font-bold uppercase tracking-[0.3em] leading-relaxed">
                      建立源数据关联后，此处将呈现交互式语义节点网络
                    </p>
                  </div>
                )}
              </motion.div>
            )}

            {activeTab === 'resources' && (
              <motion.div 
                key="resources"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="absolute inset-0 z-10 p-12 pt-32 overflow-y-auto custom-scrollbar"
              >
                <div className="max-w-5xl mx-auto space-y-12">
                  <header className="space-y-4">
                    <span className="text-[10px] font-bold text-anthropic-accent uppercase tracking-[0.4em] italic">Knowledge Sources</span>
                    <h2 className="text-5xl font-serif italic text-anthropic-ink">解析资源库</h2>
                  </header>

                  <div className="grid grid-cols-1 gap-6">
                    {/* Upload Mode Toggle */}
                    <div className="glass-panel p-6 rounded-3xl space-y-4">
                      <h3 className="text-[11px] font-black text-anthropic-muted uppercase tracking-[0.3em]">上传模式</h3>
                      <div className="flex gap-4">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="radio"
                            name="uploadMode"
                            value="single"
                            checked={uploadMode === 'single'}
                            onChange={(e) => setUploadMode(e.target.value as 'single' | 'multiple')}
                            className="w-4 h-4"
                          />
                          <span className="text-sm text-anthropic-ink">单教材模式</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="radio"
                            name="uploadMode"
                            value="multiple"
                            checked={uploadMode === 'multiple'}
                            onChange={(e) => setUploadMode(e.target.value as 'single' | 'multiple')}
                            className="w-4 h-4"
                          />
                          <span className="text-sm text-anthropic-ink">跨教材整合模式</span>
                        </label>
                      </div>
                    </div>

                    {/* Uploaded Files Display */}
                    {uploadedFiles.length > 0 && (
                      <div className="glass-panel p-6 rounded-3xl space-y-4">
                        <h3 className="text-[11px] font-black text-anthropic-muted uppercase tracking-[0.3em]">已上传文件</h3>
                        <div className="space-y-2">
                          {uploadedFiles.map((file, idx) => (
                            <div key={idx} className="flex items-center gap-3 p-3 bg-anthropic-soft rounded-xl">
                              <BookOpen className="w-4 h-4 text-anthropic-accent" />
                              <span className="text-sm text-anthropic-ink flex-1">{file.name}</span>
                              <span className="text-xs text-anthropic-muted">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {[
                      { name: '生理学_核心解析.pdf', size: '12.4 MB', entities: 42, status: 'Completed', date: '2026-05-09' },
                      { name: '内科学_循环系统.pdf', size: '18.2 MB', entities: 31, status: 'Completed', date: '2026-05-10' },
                      { name: '生化学_能量代谢.pdf', size: '8.7 MB', entities: 12, status: 'Processing', date: '2026-05-10' }
                    ].map((doc, i) => (
                      <motion.div 
                        key={i}
                        whileHover={{ y: -4 }}
                        className="glass-panel p-8 rounded-3xl flex items-center justify-between group cursor-pointer transition-shadow hover:shadow-majestic"
                      >
                        <div className="flex items-center gap-8">
                          <div className="w-16 h-16 rounded-2xl bg-anthropic-soft flex items-center justify-center text-anthropic-ink group-hover:scale-105 transition-transform">
                            <BookOpen className="w-8 h-8" />
                          </div>
                          <div className="space-y-1">
                            <h4 className="text-xl font-serif italic text-anthropic-ink">{doc.name}</h4>
                            <div className="flex items-center gap-4 text-[10px] font-bold text-anthropic-muted uppercase tracking-widest">
                              <span>{doc.size}</span>
                              <div className="w-1 h-1 rounded-full bg-anthropic-border" />
                              <span>{doc.entities} EXTRACTED_ENTITIES</span>
                              <div className="w-1 h-1 rounded-full bg-anthropic-border" />
                              <span className="text-anthropic-accent">{doc.date}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-6">
                          <div className={cn(
                            "px-4 py-1.5 rounded-full text-[9px] font-bold uppercase tracking-widest border",
                            doc.status === 'Completed' ? "bg-green-50 text-green-700 border-green-200" : "bg-blue-50 text-blue-700 border-blue-200 animate-pulse"
                          )}>
                            {doc.status}
                          </div>
                          <ChevronRight className="w-5 h-5 text-anthropic-muted group-hover:translate-x-1 transition-transform" />
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div className="p-12 border-2 border-dashed border-anthropic-border rounded-[3rem] flex flex-col items-center justify-center text-center gap-6 opacity-60 hover:opacity-100 transition-opacity cursor-pointer"
                      onClick={() => document.getElementById('fileInput')?.click()}
                    >
                      <input
                        id="fileInput"
                        type="file"
                        accept=".pdf"
                        multiple={uploadMode === 'multiple'}
                        onChange={(e) => handleFileUpload(e.target.files)}
                      className="hidden"
                    />
                    <div className="w-16 h-16 rounded-full bg-anthropic-soft flex items-center justify-center">
                      <Upload className="w-6 h-6 text-anthropic-ink" />
                    </div>
                    <div className="space-y-1">
                      <h4 className="text-lg font-serif italic text-anthropic-ink">上传新知识源</h4>
                      <p className="text-[10px] font-bold text-anthropic-muted uppercase tracking-[0.2em]">
                        {uploadMode === 'single' ? '支持单个 PDF 文件' : '支持多个 PDF 文件（跨教材整合）'}
                      </p>
                    </div>
                  </div>

                  <div
                    className="p-12 border-2 border-anthropic-accent rounded-[3rem] flex flex-col items-center justify-center text-center gap-6 bg-anthropic-accent/5 hover:bg-anthropic-accent/10 transition-all cursor-pointer"
                    onClick={() => {
                      setGraphData(demoGraphData);
                      setJobId('demo_job_id');
                      setDemoMode(true);
                      setActiveTab('topology');
                      addToast('success', '演示模式已激活');
                    }}
                  >
                    <div className="w-16 h-16 rounded-full bg-anthropic-accent/20 flex items-center justify-center">
                      <Network className="w-6 h-6 text-anthropic-accent" />
                    </div>
                    <div className="space-y-1">
                      <h4 className="text-lg font-serif italic text-anthropic-ink">演示模式</h4>
                      <p className="text-[10px] font-bold text-anthropic-accent uppercase tracking-[0.2em]">
                        快速加载示例知识图谱
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              </motion.div>
            )}

            {activeTab === 'observation' && (
              <motion.div 
                key="observation"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="absolute inset-0 z-10 p-12 pt-32 overflow-y-auto custom-scrollbar"
              >
                <div className="max-w-5xl mx-auto space-y-12">
                  <header className="space-y-4">
                    <span className="text-[10px] font-bold text-anthropic-accent uppercase tracking-[0.4em] italic">System Monitoring</span>
                    <h2 className="text-5xl font-serif italic text-anthropic-ink">系统观测态势</h2>
                  </header>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                     {[
                       { label: '内核响应时延', value: '142ms', trend: '-12%', status: 'stable' },
                       { label: '认知节点密度', value: '1,492', sub: 'Nodes/Vol', status: 'optimal' },
                       { label: '逻辑关联链路', value: '4,021', sub: 'Edges/Vol', status: 'active' }
                     ].map((metric, i) => (
                       <div key={i} className="glass-panel p-8 rounded-3xl space-y-4">
                         <div className="text-[10px] font-bold text-anthropic-muted uppercase tracking-[0.2em]">{metric.label}</div>
                         <div className="flex items-end gap-3">
                           <div className="text-4xl font-serif italic text-anthropic-ink leading-none">{metric.value}</div>
                           <div className="text-[10px] font-bold text-anthropic-accent tabular-nums mb-1">{metric.trend || metric.sub}</div>
                         </div>
                         <div className="h-1 w-full bg-anthropic-soft rounded-full overflow-hidden">
                           <motion.div 
                             initial={{ width: 0 }}
                             animate={{ width: '70%' }}
                             className="h-full bg-anthropic-ink"
                           />
                         </div>
                       </div>
                     ))}
                  </div>

                  <div className="space-y-6">
                    <h3 className="text-[11px] font-black text-anthropic-muted uppercase tracking-[0.3em] flex items-center gap-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-anthropic-accent" /> 实时计算流水
                    </h3>
                    <div className="glass-panel rounded-[2rem] overflow-hidden">
                      <div className="p-4 bg-anthropic-ink text-[10px] font-mono text-white/40 flex gap-10">
                        <span className="w-32">TIMESTAMP</span>
                        <span className="w-24">MODULE</span>
                        <span>LOG_STREAM_EMISSION</span>
                      </div>
                      <div className="p-6 font-mono text-[11px] space-y-3 bg-white">
                        {[
                          { time: '06:45:21.402', mod: 'LATTICE', msg: 'Init knowledge mesh reconstruction: cluster_04' },
                          { time: '06:45:22.012', mod: 'COGNITIVE', msg: 'Resolving semantic ambiguity in "射血分数"' },
                          { time: '06:45:22.591', mod: 'RAG_CORE', msg: 'Indexing vector space sub-dimension: cv_system_prime' },
                          { time: '06:45:23.109', mod: 'UI_RENDER', msg: 'Graph stabilization complete. Nodes: 12, Edges: 18' },
                          { time: '06:45:24.001', mod: 'SYSTEM', msg: 'Periodic heart-beat check: SUCCESS' }
                        ].map((log, i) => (
                          <div key={i} className="flex gap-10 opacity-70 hover:opacity-100 transition-opacity">
                            <span className="w-32 tabular-nums text-anthropic-muted">{log.time}</span>
                            <span className="w-24 font-bold text-anthropic-accent">[{log.mod}]</span>
                            <span className="text-anthropic-ink">{log.msg}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Floating Omnibar - Search Engine Interface */}
          <div className="absolute bottom-12 left-1/2 -translate-x-1/2 w-full max-w-2xl px-6 z-40">
             <motion.form 
               onSubmit={handleRAGQuery}
               layout
               className="glass-panel p-2 rounded-3xl flex items-center gap-2 group transition-all focus-within:ring-4 focus-within:ring-anthropic-accent/5"
             >
                <div className="pl-6 pr-2 text-anthropic-muted group-focus-within:text-anthropic-accent transition-colors">
                  <Search className="w-5 h-5" />
                </div>
                <input 
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="询问任何医学知识关联..."
                  className="flex-1 bg-transparent border-none focus:outline-none py-4 text-base font-medium text-anthropic-ink placeholder:text-anthropic-muted/50"
                />
                <button 
                  type="submit"
                  disabled={isLoading}
                  className="px-8 h-12 bg-anthropic-ink hover:bg-anthropic-accent text-white rounded-2xl font-bold transition-all active:scale-95 disabled:opacity-20 uppercase text-[10px] tracking-widest shadow-lg shadow-anthropic-ink/10"
                >
                  {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : '语义检索'}
                </button>
             </motion.form>
          </div>

          {/* RAG Overlay Drawer */}
          <AnimatePresence>
            {ragResult && (
              <motion.div 
                initial={{ opacity: 0, y: 100 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 100 }}
                className="absolute inset-0 z-30 pointer-events-none flex flex-col justify-end p-12 pb-36"
              >
                <div className="glass-panel p-10 rounded-[3rem] w-full max-w-5xl mx-auto shadow-2xl pointer-events-auto max-h-[80%] overflow-y-auto custom-scrollbar relative">
                  <button 
                    onClick={() => setRAGResult(null)}
                    className="absolute top-8 right-8 p-3 rounded-full hover:bg-anthropic-soft transition-colors border border-anthropic-border"
                  >
                    <X className="w-4 h-4 text-anthropic-muted" />
                  </button>
                  
                  <div className="max-w-4xl space-y-12">
                    <div className="space-y-4">
                       <span className="text-[10px] font-bold text-anthropic-accent uppercase tracking-[0.4em] italic">核心认知解答</span>
                       <h2 className="text-3xl font-serif italic text-anthropic-ink leading-snug text-balance">
                         {ragResult.answer}
                       </h2>
                    </div>

                    <div className="space-y-8 pt-10 border-t border-anthropic-border">
                       <h3 className="text-[11px] font-black text-anthropic-muted uppercase tracking-[0.3em] flex items-center gap-3">
                         <div className="w-1.5 h-1.5 rounded-full bg-anthropic-accent" /> 引用资源实证
                       </h3>
                       <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                          {ragResult.citations.map((citation, idx) => (
                             <motion.div 
                               key={idx} 
                               whileHover={{ scale: 1.01 }}
                               className="p-8 bg-anthropic-soft/50 border border-anthropic-border rounded-3xl group cursor-default transition-all hover:bg-white"
                             >
                                <div className="flex justify-between items-start mb-6">
                                   <div className="flex flex-col">
                                      <span className="text-xs font-bold text-anthropic-ink italic mb-1">{citation.textbook}</span>
                                      <span className="text-[10px] font-bold text-anthropic-muted uppercase tracking-widest opacity-60">页码 P.{citation.page}</span>
                                   </div>
                                   <div className="px-3 py-1 bg-white border border-anthropic-border rounded-full text-[9px] font-bold text-anthropic-muted tabular-nums">
                                      {Math.round(citation.relevance_score * 100)}%_VAL
                                   </div>
                                </div>
                                <p className={cn(
                                   "text-[13px] leading-relaxed text-anthropic-ink opacity-70 font-medium transition-all",
                                   expandedCitation === idx ? "" : "line-clamp-4"
                                )}>
                                   {citation.content}
                                </p>
                                <button 
                                  onClick={() => setExpandedCitation(expandedCitation === idx ? null : idx)}
                                  className="mt-6 text-[10px] font-bold text-anthropic-muted hover:text-anthropic-accent uppercase tracking-widest transition-colors flex items-center gap-2 group/btn"
                                >
                                  {expandedCitation === idx ? '收起溯源详情' : '展开全文验证'}
                                  <ChevronRight className={cn("w-3 h-3 transition-transform", expandedCitation === idx && "rotate-90")} />
                                </button>
                             </motion.div>
                          ))}
                       </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>

        {/* Right Side: Semantic Inspector Drawer */}
        <AnimatePresence>
          {selectedNode && (
            <motion.aside 
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 150 }}
              className="w-[450px] h-full bg-white border-l border-anthropic-border p-12 pt-32 overflow-y-auto shrink-0 z-50 relative shadow-2xl"
            >
              <button 
                onClick={() => setSelectedNode(null)}
                className="absolute top-10 right-10 p-3 rounded-full hover:bg-anthropic-soft transition-colors border border-anthropic-border"
              >
                <X className="w-5 h-5 text-anthropic-muted" />
              </button>

              <div className="space-y-12">
                <div className="space-y-4">
                   <div className="text-[10px] font-bold uppercase tracking-[0.4em] text-anthropic-accent italic opacity-80">{selectedNode.category}</div>
                   <h3 className="text-5xl font-serif italic text-anthropic-ink leading-[1.1] text-balance">{selectedNode.label}</h3>
                </div>
                
                <div className="space-y-10">
                  <div className="space-y-4">
                     <h4 className="text-[11px] font-bold text-anthropic-muted uppercase tracking-[0.3em] border-b border-anthropic-border pb-3">语义核心定义</h4>
                     <p className="text-xl text-anthropic-ink leading-relaxed font-serif italic text-balance">"{selectedNode.definition}"</p>
                  </div>

                  <div className="grid grid-cols-2 gap-8">
                     <div className="space-y-2">
                        <span className="text-[9px] font-bold text-anthropic-muted uppercase tracking-widest block opacity-50">溯源依据</span>
                        <span className="text-xs font-bold text-anthropic-ink italic block leading-snug">{selectedNode.textbook}</span>
                     </div>
                     <div className="space-y-2">
                        <span className="text-[9px] font-bold text-anthropic-muted uppercase tracking-widest block opacity-50">偏移位置</span>
                        <span className="text-xs font-bold text-anthropic-ink block tabular-nums">Page_{selectedNode.source_page}</span>
                     </div>
                  </div>

                  <div className="space-y-6">
                    <h4 className="text-[11px] font-bold text-anthropic-muted uppercase tracking-[0.3em] border-b border-anthropic-border pb-3 flex justify-between items-center">
                      关联节点集群
                      <span className="text-[9px] opacity-40 font-mono tracking-normal">{(selectedNode.detailedNeighbors?.length || selectedNode.neighbors?.length || 0)} UNI_NODES</span>
                    </h4>
                    <div className="flex flex-col gap-4">
                      {selectedNode.detailedNeighbors && selectedNode.detailedNeighbors.length > 0 ? (
                        selectedNode.detailedNeighbors.map((n, i) => (
                          <motion.div 
                            key={i} 
                            whileHover={{ scale: 1.02, x: 4 }}
                            className="p-5 bg-anthropic-soft/30 hover:bg-white border border-anthropic-border rounded-2xl transition-all cursor-default group"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <span className="text-sm font-bold text-anthropic-ink italic">{n.label}</span>
                              <span className="text-[8px] font-bold text-anthropic-muted uppercase tracking-widest px-2 py-0.5 bg-white border border-anthropic-border rounded-full">
                                {n.category}
                              </span>
                            </div>
                            <p className="text-[11px] text-anthropic-muted leading-relaxed line-clamp-2 italic group-hover:line-clamp-none transition-all">
                              {n.definition}
                            </p>
                          </motion.div>
                        ))
                      ) : selectedNode.neighbors && selectedNode.neighbors.length > 0 ? (
                        <div className="flex flex-wrap gap-2.5">
                          {selectedNode.neighbors.map((n, i) => (
                            <motion.span 
                              key={i} 
                              whileHover={{ scale: 1.05 }}
                              className="px-3.5 py-2 bg-anthropic-soft text-anthropic-ink rounded-xl text-xs font-bold italic border border-anthropic-border hover:bg-anthropic-paper transition-all cursor-default shadow-sm"
                            >
                              {n}
                            </motion.span>
                          ))}
                        </div>
                      ) : (
                        <div className="w-full py-8 text-center border-2 border-dashed border-anthropic-border rounded-3xl text-[10px] text-anthropic-muted font-bold uppercase tracking-[0.2em] italic">末端认知节点</div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="pt-10 flex gap-4">
                   <button className="flex-1 py-5 bg-anthropic-ink hover:bg-anthropic-accent text-white rounded-[2rem] text-xs font-bold uppercase tracking-[0.2em] transition-all shadow-xl shadow-anthropic-ink/10 flex items-center justify-center gap-3">
                     <ExternalLink className="w-4 h-4" /> 导出报告
                   </button>
                   <button className="p-5 border border-anthropic-border hover:bg-anthropic-soft rounded-[2rem] transition-colors">
                     <Info className="w-5 h-5 text-anthropic-muted" />
                   </button>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>
      </main>

      {/* Floating System Notifications */}
      <div className="fixed top-24 right-10 z-[100] flex flex-col gap-4 pointer-events-none">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 50, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 20, scale: 0.9 }}
              className={cn(
                "glass-panel flex items-center gap-5 px-8 py-5 rounded-[2rem] shadow-2xl w-[380px] pointer-events-auto",
                toast.type === 'error' && "border-red-200"
              )}
            >
              <div className={cn(
                "w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-sm",
                toast.type === 'success' ? "bg-anthropic-ink text-white" : "bg-red-50 text-white"
              )}>
                {toast.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
              </div>
              <div className="flex-1">
                <div className="text-[9px] font-bold uppercase tracking-[0.3em] text-anthropic-muted mb-1 leading-none">系统状态更新</div>
                <div className="text-[13px] font-bold leading-tight italic text-anthropic-ink">{toast.message}</div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Decorative Footer Detail */}
      <footer className="fixed bottom-6 right-10 z-0 select-none">
         <div className="flex items-center gap-6 text-[9px] font-bold text-anthropic-muted uppercase tracking-[0.5em] opacity-30">
            <span>2026_Engine_Prime</span>
            <div className="w-1.5 h-1.5 rounded-full bg-anthropic-muted" />
            <span>Unit_Alpha_ZJ</span>
         </div>
      </footer>
    </div>
  );
}

