import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, FileText, Link2, Sparkles, Brain, Database, Calendar, 
  Activity, Sliders, Settings, RefreshCw, LogOut, CheckCircle, 
  AlertTriangle, Shield, Cpu, Network, Terminal
} from 'lucide-react';
import { 
  ChatPage, DocumentsPage, IntegrationsPage, InsightsPage, 
  EntitiesPage, MemoryPage, TimelinePage, TelemetryPage 
} from './components/Pages';

function App() {
  const [entered, setEntered] = useState(false);
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [apiStatus, setApiStatus] = useState('connecting'); // online, offline, connecting
  const [healthData, setHealthData] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');

  // Check health status of API
  const checkHealth = async (urlToTest = apiUrl) => {
    setApiStatus('connecting');
    try {
      const res = await fetch(`${urlToTest}/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      if (res.ok) {
        const data = await res.json();
        setHealthData(data);
        setApiStatus('online');
      } else {
        setApiStatus('offline');
        setHealthData(null);
      }
    } catch (err) {
      setApiStatus('offline');
      setHealthData(null);
    }
  };

  useEffect(() => {
    checkHealth();
    // Poll every 8 seconds
    const interval = setInterval(() => checkHealth(), 8000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  const handleEnterSystem = () => {
    if (apiStatus === 'online') {
      setEntered(true);
    } else {
      // Allow entering even if offline, but show alert
      if (confirm("Backend API is currently offline. Proceed to interface anyway? Some components may not load data.")) {
        setEntered(true);
      }
    }
  };

  // Nav items configuration
  const navItems = [
    { id: 'chat', label: 'Neural Portal', icon: Bot, component: ChatPage, title: 'Neural Core Query Portal' },
    { id: 'documents', label: 'Documents', icon: FileText, component: DocumentsPage, title: 'Knowledge Catalog Ingestion' },
    { id: 'integrations', label: 'Integrations', icon: Link2, component: IntegrationsPage, title: 'Nexus Integration Hub' },
    { id: 'insights', label: 'Insights', icon: Sparkles, component: InsightsPage, title: 'Cognitive Cycle Reflection' },
    { id: 'entities', label: 'Entities', icon: Brain, component: EntitiesPage, title: 'Concept Knowledge Graph' },
    { id: 'memory', label: 'Memory', icon: Database, component: MemoryPage, title: 'Long-Term Cognitive Engine' },
    { id: 'timeline', label: 'Timeline', icon: Calendar, component: TimelinePage, title: 'Daily Activity Synthesis' },
    { id: 'diagnostics', label: 'Diagnostics', icon: Activity, component: TelemetryPage, title: 'System Telemetry & Health' },
  ];

  const currentTab = navItems.find(item => item.id === activeTab) || navItems[0];
  const ActivePageComponent = currentTab.component;

  return (
    <div className="min-h-screen portal-bg text-onSurface selection:bg-primary/30 selection:text-white font-sans overflow-y-auto">
      <AnimatePresence mode="wait">
        {!entered ? (
          /* ── LANDING PAGE (NEURAL ENTRANCE) ────────────────────────── */
          <motion.div 
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center justify-center min-h-screen p-6 relative overflow-hidden"
          >
            {/* Animated particles or glow background elements */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-tertiary/5 rounded-full blur-3xl animate-pulse [animation-delay:2s]"></div>

            <div className="max-w-xl w-full text-center space-y-8 z-10">
              {/* Spinning / Glowing Logo Dot */}
              <div className="flex justify-center">
                <div className="relative w-20 h-20 flex items-center justify-center">
                  <div className="absolute inset-0 border border-primary/20 rounded-full animate-spin [animation-duration:10s]"></div>
                  <div className="absolute inset-2 border border-dashed border-tertiary/30 rounded-full animate-spin [animation-duration:15s] [animation-direction:reverse]"></div>
                  <div className="w-8 h-8 rounded-full bg-primary dot-glow-cyan animate-pulse"></div>
                </div>
              </div>

              {/* Title Section */}
              <div className="space-y-2">
                <h1 className="text-4xl md:text-5xl font-display font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-onSurface via-primary to-secondary">
                  PERSONAL LIFE OS
                </h1>
                <p className="text-xs font-cyber tracking-[0.3em] text-onSurfaceMuted uppercase">
                  Neural Core Ingestion & Retrieval Gateway
                </p>
              </div>

              {/* Status Telemetry Card */}
              <div className="glass-panel rounded-2xl p-6 border border-outline/30 space-y-4 shadow-2xl">
                <div className="flex items-center justify-between border-b border-outline/20 pb-3">
                  <span className="text-[10px] font-mono text-onSurfaceMuted uppercase tracking-wider flex items-center gap-1.5">
                    <Terminal size={12} className="text-primary" />
                    Telemetry Handshake
                  </span>
                  {apiStatus === 'online' ? (
                    <span className="lifeos-chip lifeos-chip-cyan text-[8px] flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-tertiary dot-glow-cyan"></span>
                      Core Online
                    </span>
                  ) : apiStatus === 'connecting' ? (
                    <span className="lifeos-chip lifeos-chip-amber text-[8px] flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary dot-glow-amber animate-ping"></span>
                      Connecting
                    </span>
                  ) : (
                    <span className="lifeos-chip lifeos-chip-error text-[8px] flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-400"></span>
                      Gateway Offline
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4 text-left">
                  <div className="space-y-1">
                    <span className="text-[9px] font-mono text-onSurfaceMuted uppercase tracking-wider block">API Gateway</span>
                    <span className="text-xs font-mono font-semibold text-onSurface">
                      {apiStatus === 'online' ? 'CONNECTED' : apiStatus === 'connecting' ? 'SYNCING...' : 'DISCONNECTED'}
                    </span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[9px] font-mono text-onSurfaceMuted uppercase tracking-wider block">Neural Index</span>
                    <span className="text-xs font-mono font-semibold text-onSurface">
                      {healthData ? `${healthData.documents || 0} Docs / ${healthData.chunks || 0} Chunks` : 'STANDBY'}
                    </span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[9px] font-mono text-onSurfaceMuted uppercase tracking-wider block">Memory Engine</span>
                    <span className="text-xs font-mono font-semibold text-onSurface">
                      {apiStatus === 'online' ? 'ACTIVE' : 'OFFLINE'}
                    </span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[9px] font-mono text-onSurfaceMuted uppercase tracking-wider block">System Port</span>
                    <span className="text-xs font-mono font-semibold text-tertiary">
                      {apiUrl.replace('http://', '')}
                    </span>
                  </div>
                </div>

                {/* Show offline assistance if needed */}
                {apiStatus === 'offline' && (
                  <div className="p-3 bg-red-500/10 border border-red-500/25 rounded-lg text-left">
                    <p className="text-[10px] text-red-400 font-mono leading-relaxed">
                      Error: Unable to connect to neural core. Please verify your Python FastAPI server is running with `uvicorn api.main:app --reload` on port 8000.
                    </p>
                  </div>
                )}
              </div>

              {/* Enter CTA Button */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
                <button
                  onClick={handleEnterSystem}
                  className="w-full sm:w-auto px-8 py-3.5 bg-primary text-background font-cyber text-xs tracking-wider rounded-xl font-bold transition-all duration-300 hover:shadow-[0_0_25px_rgba(255,193,116,0.5)] transform hover:scale-105"
                >
                  ENTER NEURAL SYSTEM
                </button>
                
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="p-3.5 bg-surface border border-outline/35 text-onSurfaceMuted hover:text-onSurface rounded-xl transition-all"
                  title="Configure Network Gateway"
                >
                  <Settings size={16} />
                </button>
              </div>

              {/* Collapsible Network Settings */}
              {showSettings && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass-panel rounded-xl p-4 border border-outline/30 text-left space-y-3"
                >
                  <label className="block text-[9px] font-mono text-onSurfaceMuted uppercase tracking-wider">
                    API Endpoint Config
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={apiUrl}
                      onChange={(e) => setApiUrl(e.target.value)}
                      placeholder="http://localhost:8000"
                      className="flex-1 bg-background text-onSurface text-xs font-mono border border-outline/40 rounded-lg px-3 py-2 focus:outline-none focus:border-primary"
                    />
                    <button
                      onClick={() => checkHealth()}
                      className="bg-primary/10 hover:bg-primary/20 border border-primary/30 text-primary px-3 rounded-lg text-xs"
                    >
                      Test
                    </button>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        ) : (
          /* ── DASHBOARD SHELL ───────────────────────────────────────── */
          <motion.div 
            key="dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col md:flex-row min-h-screen"
          >
            {/* Sidebar Navigation */}
            <aside className="w-full md:w-64 bg-gradient-to-b from-surface/90 to-background border-b md:border-b-0 md:border-r border-outline/25 p-4 flex flex-col justify-between flex-shrink-0 backdrop-blur-xl">
              <div className="space-y-6">
                {/* Logo and System Online Banner */}
                <div className="lifeos-sidebar-header">
                  <div className="lifeos-logo-wrap">
                    <div className="lifeos-logo-dot">
                      <div className="lifeos-logo-inner"></div>
                    </div>
                    <div>
                      <div className="lifeos-logo-name">Life OS</div>
                      <div className="lifeos-logo-version">V.2.04 · ONLINE</div>
                    </div>
                  </div>
                </div>

                {/* API Gateway status tag */}
                <div className="lifeos-status-bar">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${apiStatus === 'online' ? 'bg-tertiary dot-glow-cyan' : 'bg-red-400'}`}></span>
                    <span className="text-[9px] font-mono text-onSurfaceMuted uppercase">
                      {apiStatus === 'online' ? 'API READY' : 'OFFLINE'}
                    </span>
                  </div>
                  <span className="text-[9px] text-tertiary font-mono uppercase tracking-wider">Neural Sync</span>
                </div>

                {/* Navigation Menu */}
                <nav className="space-y-1">
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;
                    return (
                      <button
                        key={item.id}
                        onClick={() => setActiveTab(item.id)}
                        className={`w-full text-left lifeos-nav-item ${isActive ? 'active' : ''}`}
                      >
                        <Icon size={16} />
                        <span>{item.label}</span>
                      </button>
                    );
                  })}
                </nav>
              </div>

              {/* Sidebar Footer Controls */}
              <div className="mt-8 pt-4 border-t border-outline/20 space-y-3">
                {/* Compact API Config */}
                <div className="space-y-1.5">
                  <span className="text-[8px] font-mono text-onSurfaceMuted uppercase tracking-wider block">Gateway Node</span>
                  <div className="flex items-center justify-between text-[10px] font-mono text-onSurface bg-outline/10 p-2 rounded border border-outline/20">
                    <span className="truncate">{apiUrl.replace('http://', '')}</span>
                    <button 
                      onClick={() => checkHealth()} 
                      className="text-primary hover:text-white transition-colors"
                      title="Force Handshake Sync"
                    >
                      <RefreshCw size={10} className={apiStatus === 'connecting' ? 'animate-spin' : ''} />
                    </button>
                  </div>
                </div>

                {/* Exit Portal Button */}
                <button
                  onClick={() => setEntered(false)}
                  className="w-full bg-outline/20 hover:bg-outline/40 text-onSurface px-3 py-2 rounded-lg text-xs font-mono flex items-center justify-center gap-2 border border-outline/30 transition-all"
                >
                  <LogOut size={12} />
                  <span>Exit Portal</span>
                </button>
              </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col min-w-0">
              {/* Header Bar */}
              <header className="h-16 border-b border-outline/20 px-6 flex items-center justify-between bg-surface/30 backdrop-blur-md">
                <div className="flex items-center gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary dot-glow-amber"></div>
                  <div>
                    <span className="lifeos-welcome-sub block m-0">Dashboard Portal</span>
                    <h2 className="text-sm font-semibold tracking-wide font-display text-onSurface">
                      {currentTab.title}
                    </h2>
                  </div>
                </div>
                
                {/* Secondary Telemetry */}
                {healthData && (
                  <div className="hidden sm:flex items-center gap-3 text-[10px] font-mono text-onSurfaceMuted">
                    <span>Docs: <span className="text-primary">{healthData.documents || 0}</span></span>
                    <span className="opacity-30">|</span>
                    <span>Chunks: <span className="text-tertiary">{healthData.chunks || 0}</span></span>
                    <span className="opacity-30">|</span>
                    <span>Cache Hit Rate: <span className="text-secondary">{healthData.cache_hit_rate || '0.00'}%</span></span>
                  </div>
                )}
              </header>

              {/* Tab Content Panel */}
              <div className="flex-1 p-6 overflow-y-auto">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35, ease: "easeOut" }}
                >
                  <ActivePageComponent apiUrl={apiUrl} />
                </motion.div>
              </div>
            </main>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
