import React, { useState, useEffect } from 'react';
import { AgentVisualizer } from './components/AgentVisualizer';
import { AgentGeneratingVisualizer } from './components/AgentGeneratingVisualizer';
import { ResultCard } from './components/ResultCard';
import { Sparkles } from 'lucide-react';

type Stage = 'idle' | 'plan' | 'write' | 'reflect' | 'render' | 'done';

const API_BASE = import.meta.env.VITE_API_URL || '';

function App() {
  const [request, setRequest] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [stage, setStage] = useState<Stage>('idle');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<'cream' | 'dark' | 'blue' | 'coral'>('cream');

  // Synchronize CSS class on document body
  useEffect(() => {
    document.body.className = `theme-${theme}`;
  }, [theme]);

  // Fake pipeline progression for the logs
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isLoading) {
      let currentStage = 0;
      const stages: Stage[] = ['plan', 'write', 'reflect', 'render'];
      setStage(stages[0]);
      
      interval = setInterval(() => {
        if (currentStage < stages.length - 1) {
          currentStage++;
          setStage(stages[currentStage]);
        }
      }, 3000); 
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (request.trim().length < 5) return;

    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/agent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request }),
      });

      if (!response.ok) {
        throw new Error('Agent failed to process request');
      }

      const data = await response.json();
      setResult(data);
      setStage('done');
    } catch (err: any) {
      setError(err.message);
      setStage('idle');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTemplate = (text: string) => {
    setRequest(text);
  };

  return (
    <div className="app-container">
      {/* Top Header */}
      <header className="top-header">
        <div className="brand-section">
          <div className="blueprint-version">AUTONOMOUS BLUEPRINT / V4.2</div>
          <div className="brand-title">Agent Docx Builder</div>
        </div>
        <div className="status-section">
          <div className="theme-presets">
            <div 
              className={`preset-dot ${theme === 'cream' ? 'active' : ''}`} 
              style={{backgroundColor: '#f6efe6'}}
              onClick={() => setTheme('cream')}
              title="Cream/Sepia Theme"
            ></div>
            <div 
              className={`preset-dot ${theme === 'dark' ? 'active' : ''}`} 
              style={{backgroundColor: '#3f1a1a'}}
              onClick={() => setTheme('dark')}
              title="Dark Chocolate Theme"
            ></div>
            <div 
              className={`preset-dot ${theme === 'blue' ? 'active' : ''}`} 
              style={{backgroundColor: '#e8f0f8'}}
              onClick={() => setTheme('blue')}
              title="Blueprint Blue Theme"
            ></div>
            <div 
              className={`preset-dot ${theme === 'coral' ? 'active' : ''}`} 
              style={{backgroundColor: '#d9534f'}}
              onClick={() => setTheme('coral')}
              title="Warm Terracotta Theme"
            ></div>
          </div>
          <div className="system-status">
            <div className="status-label">STATUS CODE</div>
            <div className="status-value">SYSTEM_ONLINE</div>
          </div>
        </div>
      </header>

      {/* Hero Banner */}
      <div className="hero-banner">
        <div className="hero-content">
          <div className="hero-label">CORE INITIATIVE</div>
          <div className="hero-title">Act On It.</div>
        </div>
        <div className="active-protocol">
          <div className="protocol-label">ACTIVE PROTOCOL</div>
          <div className="protocol-desc">Reflecting and correcting custom text drafts in real-time.</div>
        </div>
      </div>

      {/* Main Viewport Split */}
      <main className="main-viewport">
        {/* Left Column (Forms & Logs) */}
        <div className="left-column">
          
          {/* Spec Box */}
          <div className="blueprint-box">
            <div className="box-header">
              <span>01. SPECIFICATION</span>
              <div className="box-indicator"></div>
            </div>
            <div className="box-content">
              <div className="spec-title">Prompt Directive</div>
              <div className="spec-desc">Formulate clear guidelines or prompt queries for the document builder.</div>
              <form onSubmit={handleSubmit}>
                <textarea
                  value={request}
                  onChange={(e) => setRequest(e.target.value)}
                  placeholder="e.g. Create a comprehensive project plan for our Q3 initiative, including milestones, team roles, and risk evaluation..."
                  disabled={isLoading}
                  spellCheck={false}
                />
                <button type="submit" className="btn-launch" disabled={isLoading || request.length < 5}>
                  {isLoading ? 'PROCESSING DIRECTIVE...' : 'LAUNCH AUTONOMOUS AGENT'}
                </button>
              </form>
              {error && <div style={{marginTop: '1rem', color: '#d9534f', fontSize: '0.75rem', fontFamily: 'var(--font-mono)'}}>ERR: {error}</div>}
            </div>
          </div>

          {/* Templates Box */}
          <div className="blueprint-box">
            <div className="box-header">
              <span>02. TEMPLATE BLUEPRINTS</span>
            </div>
            <div className="box-content" style={{padding: '1rem'}}>
              
              <div className="template-card">
                <div className="template-header">001 STANDARD PROJECT PLAN</div>
                <div className="template-desc">Create a project plan for launching a new mobile banking app's onboarding feature, including timeline, team roles, and risks.</div>
                <div className="template-actions">
                  <div className="template-tag">STANDARD EXECUTION</div>
                  <button className="btn-select" onClick={() => handleTemplate("Create a project plan for launching a new mobile banking app's onboarding feature, including timeline, team roles, and risks.")}>
                    SELECT & RUN
                  </button>
                </div>
              </div>

              <div className="template-card">
                <div className="template-header">002 AMBIGUOUS CLIENT MEMO</div>
                <div className="template-desc">We need something for the client about our Q3 initiative - make it look professional and include next steps, but I don't have exact numbers yet.</div>
                <div className="template-actions">
                  <div className="template-tag">FORCES REFLECTION & ASSUMPTIONS</div>
                  <button className="btn-select" onClick={() => handleTemplate("We need something for the client about our Q3 initiative - make it look professional and include next steps, but I don't have exact numbers yet.")}>
                    SELECT & RUN
                  </button>
                </div>
              </div>

            </div>
          </div>

          {/* Logs Box */}
          <div className="blueprint-box" style={{flex: 1}}>
            <div className="box-header">
              <span>&gt;_ 03. ARCHITECTURAL LOGS</span>
              <span style={{fontWeight: 400, color: 'var(--text-secondary)'}}>{isLoading ? 'STREAMING' : 'IDLE'}</span>
            </div>
            <div className="box-content">
               <AgentVisualizer stage={stage} />
            </div>
          </div>

        </div>

        {/* Right Column (Canvas) */}
        <div className="right-column">
          {stage === 'idle' && !result && !error && (
            <div className="canvas-empty">
              <Sparkles size={32} className="empty-icon" />
              <div className="empty-title">System Core Ready</div>
              <div className="empty-desc">Provide instructions above or select an orchestration scenario. The agent will formulate planning assumptions, compile rich copy tables, inspect its own work, and output a valid ".docx" file.</div>
            </div>
          )}

          {isLoading && <AgentGeneratingVisualizer stage={stage} />}

          {result && <ResultCard data={result} />}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div>SYSTEM STATUS: <strong>OPTIMAL</strong></div>
        <div style={{display: 'flex', gap: '2rem'}}>
          <span>LAT: 34.0522° N</span>
          <span>LNG: 118.2437° W</span>
          <strong>© MMXXVI CATALYST SYSTEMS</strong>
        </div>
      </footer>
    </div>
  );
}

export default App;
