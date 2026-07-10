import React, { useState, useEffect, useRef } from 'react';
import { Network, FileCode, ShieldAlert, Layers, Activity } from 'lucide-react';

interface GeneratingVisualizerProps {
  stage: 'idle' | 'plan' | 'write' | 'reflect' | 'render' | 'done';
}

type TabType = 'auto' | 'plan' | 'write' | 'reflect' | 'render';

export const AgentGeneratingVisualizer: React.FC<GeneratingVisualizerProps> = ({ stage }) => {
  const [activeTab, setActiveTab] = useState<TabType>('auto');
  const [elapsedTime, setElapsedTime] = useState(0);
  const [memoryUsage, setMemoryUsage] = useState(104.2);
  const [cpuUsage, setCpuUsage] = useState(45);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Determine which animation to show
  const currentView = activeTab === 'auto' ? (stage === 'idle' || stage === 'done' ? 'plan' : stage) : activeTab;

  // Uptime counter
  useEffect(() => {
    setElapsedTime(0);
    timerRef.current = setInterval(() => {
      setElapsedTime(prev => prev + 0.1);
    }, 100);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Oscillate metrics to make the UI look alive
  useEffect(() => {
    const interval = setInterval(() => {
      setMemoryUsage(prev => {
        const delta = (Math.random() - 0.5) * 1.5;
        return Math.max(90, Math.min(130, Number((prev + delta).toFixed(1))));
      });
      setCpuUsage(prev => {
        const delta = Math.floor((Math.random() - 0.5) * 10);
        return Math.max(20, Math.min(95, prev + delta));
      });
    }, 800);

    return () => clearInterval(interval);
  }, []);

  // Format elapsed time (e.g. "04.2s")
  const formatTime = (time: number) => {
    return `${time.toFixed(1)}s`;
  };

  return (
    <div className="agent-gen-visualizer">
      {/* Top Tabs / Controls */}
      <div className="visualizer-tabs">
        <button
          className={`tab-btn ${activeTab === 'auto' ? 'active' : ''}`}
          onClick={() => setActiveTab('auto')}
          title="Auto-track current stage"
        >
          <span className="live-dot-pulse"></span>
          AUTO-TRACK
        </button>
        <button
          className={`tab-btn ${activeTab === 'plan' ? 'active' : ''} ${stage === 'plan' && activeTab === 'auto' ? 'active-track' : ''}`}
          onClick={() => setActiveTab('plan')}
        >
          <Network size={12} />
          01. NODE MAP
        </button>
        <button
          className={`tab-btn ${activeTab === 'write' ? 'active' : ''} ${stage === 'write' && activeTab === 'auto' ? 'active-track' : ''}`}
          onClick={() => setActiveTab('write')}
        >
          <FileCode size={12} />
          02. SYNTAX
        </button>
        <button
          className={`tab-btn ${activeTab === 'reflect' ? 'active' : ''} ${stage === 'reflect' && activeTab === 'auto' ? 'active-track' : ''}`}
          onClick={() => setActiveTab('reflect')}
        >
          <ShieldAlert size={12} />
          03. RADAR
        </button>
        <button
          className={`tab-btn ${activeTab === 'render' ? 'active' : ''} ${stage === 'render' && activeTab === 'auto' ? 'active-track' : ''}`}
          onClick={() => setActiveTab('render')}
        >
          <Layers size={12} />
          04. COMPILER
        </button>
      </div>

      {/* Metrics Overlay Panel */}
      <div className="metrics-panel">
        <div className="metric-item">
          <span className="metric-label">STAGE PROTOCOL:</span>
          <span className="metric-value stage-highlight">{stage.toUpperCase()}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">ELAPSED TIME:</span>
          <span className="metric-value font-mono-only">{formatTime(elapsedTime)}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">SYS MEM:</span>
          <span className="metric-value font-mono-only">{memoryUsage} MB</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">CPU CORE:</span>
          <span className="metric-value font-mono-only">{cpuUsage}%</span>
        </div>
        <div className="metric-status-glow">
          <Activity size={12} className="heartbeat-icon" />
          <span>SYNCING_LLM</span>
        </div>
      </div>

      {/* Main Canvas Viewport */}
      <div className="visualizer-canvas">
        {currentView === 'plan' && <PlanNodeMap />}
        {currentView === 'write' && <WriteSyntaxStream />}
        {currentView === 'reflect' && <ReflectRadar />}
        {currentView === 'render' && <RenderLayerCompiler />}
      </div>
    </div>
  );
};

/* =========================================================================
   ANIMATION SUB-COMPONENTS
   ========================================================================= */

// 1. PLAN: Node Map Constellation Animation
const PlanNodeMap: React.FC = () => {
  return (
    <div className="animation-container node-map-view">
      <div className="view-tag">SUBROUTINE: PLAN_ORCHESTRATOR</div>
      <div className="canvas-grid-bg"></div>
      
      <svg className="node-map-svg" viewBox="0 0 400 300" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Connection Paths */}
        <path d="M 200,150 L 100,90" className="path-line line-pulse-1" />
        <path d="M 200,150 L 300,90" className="path-line line-pulse-2" />
        <path d="M 200,150 L 100,210" className="path-line line-pulse-3" />
        <path d="M 200,150 L 300,210" className="path-line line-pulse-4" />
        <path d="M 100,90 L 100,210" className="path-line path-secondary" />
        <path d="M 300,90 L 300,210" className="path-line path-secondary" />
        
        {/* Pulsing signal markers moving along paths */}
        <circle r="4" fill="var(--text-primary)" className="pulse-marker m-1" />
        <circle r="4" fill="var(--text-primary)" className="pulse-marker m-2" />
        <circle r="4" fill="var(--text-primary)" className="pulse-marker m-3" />
        
        {/* Nodes */}
        {/* Central Core */}
        <g className="node-group central-core">
          <circle cx="200" cy="150" r="16" className="node-outer-glow" />
          <circle cx="200" cy="150" r="8" className="node-core" />
          <text x="200" y="180" textAnchor="middle" className="node-text core-label">AGENT_CORE</text>
        </g>

        {/* Node 1: Validate */}
        <g className="node-group node-sub n-1">
          <circle cx="100" cy="90" r="8" className="node-sub-outer" />
          <circle cx="100" cy="90" r="4" className="node-sub-core" />
          <text x="100" y="75" textAnchor="middle" className="node-text">VALIDATE</text>
        </g>

        {/* Node 2: Outline */}
        <g className="node-group node-sub n-2">
          <circle cx="300" cy="90" r="8" className="node-sub-outer" />
          <circle cx="300" cy="90" r="4" className="node-sub-core" />
          <text x="300" y="75" textAnchor="middle" className="node-text">OUTLINE</text>
        </g>

        {/* Node 3: Tasks */}
        <g className="node-group node-sub n-3">
          <circle cx="100" cy="210" r="8" className="node-sub-outer" />
          <circle cx="100" cy="210" r="4" className="node-sub-core" />
          <text x="100" y="230" textAnchor="middle" className="node-text">TASK_LIST</text>
        </g>

        {/* Node 4: Synthesize */}
        <g className="node-group node-sub n-4">
          <circle cx="300" cy="210" r="8" className="node-sub-outer" />
          <circle cx="300" cy="210" r="4" className="node-sub-core" />
          <text x="300" y="230" textAnchor="middle" className="node-text">SYNTHESIZE</text>
        </g>
      </svg>
    </div>
  );
};

// 2. WRITE: Syntax Stream / Typing Layout Animation
const WriteSyntaxStream: React.FC = () => {
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    'INIT: writer_module booted',
    'STREAM: requesting LLM structure tokens...',
  ]);

  useEffect(() => {
    const logs = [
      'RESOLVED: schema matching SectionOutline',
      'WRITE [01]: Section Heading "Executive Summary"',
      'WRITE [01]: drafting summary paragraph blocks...',
      'WRITE [02]: Section Heading "Project Timeline & Plan"',
      'GEN_TABLE: calculating cell matrices (4 rows)',
      'WRITE [03]: Section Heading "Risk Assessment"',
      'WRITE [03]: detailing mitigation scenarios...',
      'STREAM: closing text buffer chunks',
      'STATUS: draft content successfully compiled.'
    ];

    let logIndex = 0;
    const interval = setInterval(() => {
      if (logIndex < logs.length) {
        setTerminalLogs(prev => [...prev, logs[logIndex]].slice(-6));
        logIndex++;
      }
    }, 1800);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="animation-container syntax-view">
      <div className="view-tag">SUBROUTINE: DOCUMENT_WRITER</div>
      <div className="canvas-grid-bg"></div>

      <div className="syntax-split">
        {/* Left Side: Mock Document Layout Compilation */}
        <div className="doc-layout-skeleton">
          <div className="skel-page">
            <div className="skel-line header-title scanning"></div>
            <div className="skel-block block-1 active-glow">
              <div className="skel-line"></div>
              <div className="skel-line short"></div>
            </div>
            <div className="skel-block block-2 active-glow">
              <div className="skel-line"></div>
              <div className="skel-line"></div>
              <div className="skel-line short"></div>
            </div>
            {/* Mock Table Layout */}
            <div className="skel-table active-glow">
              <div className="skel-table-row header">
                <div className="skel-cell"></div>
                <div className="skel-cell"></div>
              </div>
              <div className="skel-table-row">
                <div className="skel-cell"></div>
                <div className="skel-cell"></div>
              </div>
              <div className="skel-table-row">
                <div className="skel-cell"></div>
                <div className="skel-cell"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Streaming Logs */}
        <div className="syntax-logs">
          <div className="logs-header">TERMINAL FEEDBACK</div>
          <div className="logs-content font-mono-only">
            {terminalLogs.map((log, index) => (
              <div key={index} className={`log-line-entry ${log.includes('WRITE') ? 'highlight' : ''}`}>
                <span className="log-prompt">&gt;</span> {log}
              </div>
            ))}
            <div className="log-cursor"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

// 3. REFLECT: Sonar Constraint Check Animation
const ReflectRadar: React.FC = () => {
  const [checks, setChecks] = useState([
    { id: 1, label: 'CHECK_PROMPT_COVERAGE', status: 'pass' },
    { id: 2, label: 'VERIFY_TIMELINE_CONSISTENCY', status: 'warning' },
    { id: 3, label: 'INSPECT_ASSUMPTIONS_LOG', status: 'pending' },
    { id: 4, label: 'AUTOCORRECT_SECTION_DRAFTS', status: 'pending' },
  ]);

  useEffect(() => {
    const timer1 = setTimeout(() => {
      setChecks(prev =>
        prev.map(c => (c.id === 2 ? { ...c, status: 'pass' } : c))
      );
    }, 3000);

    const timer2 = setTimeout(() => {
      setChecks(prev =>
        prev.map(c => (c.id === 3 ? { ...c, status: 'pass' } : c))
      );
    }, 5500);

    const timer3 = setTimeout(() => {
      setChecks(prev =>
        prev.map(c => (c.id === 4 ? { ...c, status: 'pass' } : c))
      );
    }, 8000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div className="animation-container radar-view">
      <div className="view-tag">SUBROUTINE: SELF_REFLECTION_CRITIC</div>
      <div className="canvas-grid-bg"></div>

      <div className="radar-layout">
        {/* Radar Scanner Screen */}
        <div className="radar-screen">
          <div className="radar-sweep"></div>
          <div className="radar-circle rc-1"></div>
          <div className="radar-circle rc-2"></div>
          <div className="radar-circle rc-3"></div>
          <div className="radar-axis-h"></div>
          <div className="radar-axis-v"></div>
          
          {/* Scanning Blip Nodes */}
          <div className="radar-blip blip-1 pass" style={{ top: '30%', left: '40%' }}></div>
          <div className="radar-blip blip-2 warning" style={{ top: '60%', left: '70%' }}></div>
          <div className="radar-blip blip-3 active" style={{ top: '45%', left: '25%' }}></div>
        </div>

        {/* Checklists status */}
        <div className="radar-checklist">
          <div className="checklist-title">CRITIC RULES EVALUATION</div>
          <div className="checklist-items">
            {checks.map(c => (
              <div key={c.id} className={`checklist-item ${c.status}`}>
                <span className="check-bullet"></span>
                <span className="check-label font-mono-only">{c.label}</span>
                <span className="check-status font-mono-only">
                  {c.status.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// 4. RENDER: 3D Isometric Page Stack Animation
const RenderLayerCompiler: React.FC = () => {
  return (
    <div className="animation-container compiler-view">
      <div className="view-tag">SUBROUTINE: DOCX_BUILD_ENGINE</div>
      <div className="canvas-grid-bg"></div>

      <div className="isometric-scene">
        {/* Compilation Laser Scan Indicator */}
        <div className="laser-beam"></div>

        {/* Isometric Sheets */}
        <div className="iso-layer top-layer">
          <div className="iso-layer-header">
            <span>PAGE_META: HEADER & PAGE_NUMBERS</span>
            <span className="layer-tag">TOP</span>
          </div>
          <div className="iso-layer-content">
            <div className="iso-element line"></div>
            <div className="iso-element line short"></div>
          </div>
        </div>

        <div className="iso-layer middle-layer">
          <div className="iso-layer-header">
            <span>DRAFT_CONTENT: PARAGRAPHS & TABLES</span>
            <span className="layer-tag">MID</span>
          </div>
          <div className="iso-layer-content">
            <div className="iso-element content-box"></div>
            <div className="iso-element content-box-secondary"></div>
          </div>
        </div>

        <div className="iso-layer base-layer">
          <div className="iso-layer-header">
            <span>DOCX_BLUEPRINT: FILE STYLES & LAYOUT</span>
            <span className="layer-tag">BASE</span>
          </div>
          <div className="iso-layer-content">
            <div className="iso-element grid"></div>
          </div>
        </div>
      </div>
    </div>
  );
};
