import React from 'react';

interface VisualizerProps {
  stage: 'idle' | 'plan' | 'write' | 'reflect' | 'render' | 'done';
}

const STAGES = [
  { id: 'plan', title: 'agent.planner initialized' },
  { id: 'write', title: 'agent.writer drafting blocks' },
  { id: 'reflect', title: 'agent.reflector constraint check' },
  { id: 'render', title: 'agent.renderer compiling docx' },
];

export const AgentVisualizer: React.FC<VisualizerProps> = ({ stage }) => {
  if (stage === 'idle') {
    return <div className="log-stream" style={{color: 'var(--text-secondary)', fontStyle: 'italic'}}>No dynamic execution active. Trigger pipeline to start.</div>;
  }

  const getStageStatus = (stageId: string) => {
    const stageIndex = STAGES.findIndex(s => s.id === stageId);
    const currentIndex = STAGES.findIndex(s => s.id === stage);
    
    if (stage === 'done' || currentIndex > stageIndex) return 'completed';
    if (currentIndex === stageIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="log-stream">
      {STAGES.map((s) => {
        const status = getStageStatus(s.id);
        if (status === 'pending') return null; // Only show active or completed
        
        return (
          <div key={s.id} className="log-entry">
            <span className="log-time">[{new Date().toISOString().split('T')[1].substring(0, 8)}]</span>
            {status === 'active' ? (
              <span className="log-active">&gt; {s.title}...</span>
            ) : (
              <span>[OK] {s.title} completed.</span>
            )}
          </div>
        );
      })}
      {stage === 'done' && (
        <div className="log-entry">
          <span className="log-time">[{new Date().toISOString().split('T')[1].substring(0, 8)}]</span>
          <span style={{color: '#10b981'}}>[SYS] Document architecture finalized and rendered successfully.</span>
        </div>
      )}
    </div>
  );
};
