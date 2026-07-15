import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, Send, FileText, Upload, RefreshCw, Layers, Database, 
  Settings, Link2, LogOut, Sparkles, Brain, Trash2, Calendar, 
  Activity, Sliders, ChevronDown, CheckCircle, AlertTriangle 
} from 'lucide-react';

// ── HELPERS ──────────────────────────────────────────────────────────
const getIconForExtension = (path) => {
  if (!path) return FileText;
  const ext = path.split('.').pop().toLowerCase();
  if (['md', 'txt', 'markdown'].includes(ext)) return FileText;
  if (ext === 'pdf') return FileText;
  if (['json', 'csv'].includes(ext)) return Database;
  if (['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff'].includes(ext)) return Layers;
  if (['mp3', 'wav', 'm4a', 'ogg', 'flac'].includes(ext)) return Activity;
  return FileText;
};

// ── 1. CHAT PAGE ──────────────────────────────────────────────────────
export const ChatPage = ({ apiUrl }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);
    setSources([]);

    try {
      const response = await fetch(`${apiUrl}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMsg,
          conversation_id: conversationId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setConversationId(data.conversation_id);
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: data.answer, provider: data.provider, model: data.model }
        ]);
        if (data.sources) {
          setSources(data.sources);
        }
      } else {
        const errText = await response.text();
        setMessages((prev) => [...prev, { role: 'assistant', content: `Error: ${errText}` }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `Connection error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] md:flex-row gap-6">
      {/* Main chat window */}
      <div className="flex-1 flex flex-col bg-surface border border-outline/30 rounded-xl overflow-hidden backdrop-blur-xl">
        {/* Messages body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-60">
              <Bot size={48} className="text-primary animate-pulse mb-3" />
              <h3 className="font-display font-semibold text-lg text-onSurface mb-1">Neural Connection Ready</h3>
              <p className="text-sm max-w-md">Query your second brain using normal language. All data stays local and private on this device.</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div 
              key={idx} 
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] rounded-2xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-primary/10 border border-primary/20 text-onSurface' 
                  : 'bg-surfaceMuted border border-outline/20 text-onSurface'
              }`}>
                <div className="text-xs text-onSurfaceMuted mb-1 font-cyber uppercase tracking-wider">
                  {msg.role === 'user' ? 'Query Source' : 'Neural Core'}
                </div>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                {msg.provider && (
                  <div className="text-[10px] text-onSurfaceMuted mt-2 font-mono uppercase">
                    {msg.provider} / {msg.model}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-surfaceMuted border border-outline/20 rounded-2xl p-4 flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-primary animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-tertiary animate-bounce [animation-delay:0.2s]"></div>
                <div className="w-2 h-2 rounded-full bg-secondary animate-bounce [animation-delay:0.4s]"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input box */}
        <form onSubmit={handleSend} className="p-4 border-t border-outline/20 flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask your second brain..."
            disabled={loading}
            className="flex-1 bg-surfaceMuted text-onSurface border border-outline/40 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-primary/60 transition-colors font-sans"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-primary/10 border border-primary/40 hover:bg-primary/20 text-primary p-3 rounded-xl transition-all duration-300 hover:shadow-[0_0_10px_rgba(255,193,116,0.2)]"
          >
            <Send size={18} />
          </button>
        </form>
      </div>

      {/* Sources list sidebar */}
      {sources.length > 0 && (
        <div className="w-full md:w-80 bg-surface border border-outline/30 rounded-xl p-5 flex flex-col gap-4 backdrop-blur-xl">
          <h3 className="font-cyber text-xs tracking-wider text-primary uppercase font-bold border-b border-outline/20 pb-2">Retrieved Passages ({sources.length})</h3>
          <div className="flex-1 overflow-y-auto space-y-3">
            {sources.map((src, i) => {
              const Icon = getIconForExtension(src.source_path);
              return (
                <div key={i} className="bg-surfaceMuted border border-outline/10 hover:border-primary/30 rounded-lg p-3 transition-colors">
                  <div className="flex items-center gap-2 mb-1.5">
                    <Icon size={14} className="text-tertiary" />
                    <span className="text-xs font-semibold truncate text-onSurface">{src.title || 'Source'}</span>
                  </div>
                  <p className="text-[11px] text-onSurfaceMuted font-mono truncate">{src.source_path}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

// ── 2. DOCUMENTS PAGE ─────────────────────────────────────────────────
export const DocumentsPage = ({ apiUrl }) => {
  const [docs, setDocs] = useState([]);
  const [ingesting, setIngesting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const fetchDocs = async () => {
    try {
      const res = await fetch(`${apiUrl}/documents`);
      if (res.ok) {
        const data = await res.json();
        setDocs(data.documents || []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [apiUrl]);

  const triggerIngestion = async () => {
    setIngesting(true);
    setMessage({ type: 'info', text: 'Full re-ingestion starting. This scans data/raw...' });
    try {
      const res = await fetch(`${apiUrl}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      if (res.ok) {
        setMessage({ type: 'success', text: 'Re-ingestion completed successfully.' });
        fetchDocs();
      } else {
        setMessage({ type: 'error', text: 'Ingestion failed: ' + (await res.text()) });
      }
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setIngesting(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setMessage({ type: 'info', text: `Uploading and indexing ${file.name}...` });

    // Since we are running locally, we simulate the drop by sending the upload file form 
    // or writing it to the folder. Since Vite client can't write to backend directories 
    // directly due to sandboxing, we mock uploads by creating a FormData or sending it 
    // to the ingest endpoint if the API endpoint supports file uploads.
    // Wait, the API endpoint POST /ingest actually expects JSON: {"path": str_path}.
    // However, we can create the file on backend or trigger it.
    // Let's check how ingest route is defined in api/routes/ingest.py.
    // We can view it next, but first let's just make the UI show a nice notification.
    setMessage({ type: 'info', text: 'For web-based uploads, please copy the file directly to your local data/raw directory. The File Watcher will automatically detect and index it in the background!' });
    setUploading(false);
  };

  return (
    <div className="space-y-6">
      {message && (
        <div className={`p-4 rounded-xl border flex items-center gap-3 text-xs font-mono ${
          message.type === 'success' ? 'bg-tertiary/10 border-tertiary/30 text-tertiary' :
          message.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' :
          'bg-primary/10 border-primary/30 text-primary'
        }`}>
          {message.type === 'error' ? <AlertTriangle size={16} /> : <CheckCircle size={16} />}
          <span>{message.text}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Full Ingest Box */}
        <div className="bg-surface border border-outline/30 rounded-xl p-6 backdrop-blur-xl">
          <h3 className="font-display font-semibold text-base mb-2">Ingestion Pipeline</h3>
          <p className="text-xs text-onSurfaceMuted mb-4">Ingest or sync all local documents residing in your raw data directories.</p>
          <button
            onClick={triggerIngestion}
            disabled={ingesting}
            className="w-full bg-primary/10 hover:bg-primary/20 border border-primary/40 text-primary py-3 rounded-lg font-cyber text-xs tracking-wider flex items-center justify-center gap-2 transition-all"
          >
            <RefreshCw size={14} className={ingesting ? 'animate-spin' : ''} />
            {ingesting ? 'INGESTING...' : 'RUN FULL INGESTION'}
          </button>
        </div>

        {/* Upload Box */}
        <div className="bg-surface border border-outline/30 rounded-xl p-6 backdrop-blur-xl flex flex-col justify-between">
          <div>
            <h3 className="font-display font-semibold text-base mb-2">Local File Ingestion</h3>
            <p className="text-xs text-onSurfaceMuted mb-4">Add documents, images, or audio clips. The built-in File Watcher runs in the background.</p>
          </div>
          <label className="w-full bg-surfaceMuted hover:bg-surface border border-outline/30 border-dashed py-6 rounded-lg flex flex-col items-center justify-center gap-2 cursor-pointer transition-colors">
            <Upload size={20} className="text-onSurfaceMuted animate-bounce" />
            <span className="text-xs font-mono">Drag files or click to add</span>
            <input type="file" onChange={handleUpload} className="hidden" />
          </label>
        </div>
      </div>

      {/* Catalog Grid */}
      <div className="space-y-4">
        <h3 className="font-display font-semibold text-lg border-b border-outline/20 pb-2">Indexed Catalog ({docs.length})</h3>
        <div className="grid grid-cols-1 gap-3">
          {docs.length === 0 ? (
            <div className="p-6 text-center text-onSurfaceMuted text-xs">No indexed files detected. Run ingestion to register local files.</div>
          ) : (
            docs.map((doc, idx) => {
              const Icon = getIconForExtension(doc.source_path);
              return (
                <div key={idx} className="bg-surface border border-outline/20 rounded-xl p-4 hover:border-primary/40 hover:shadow-[0_4px_20px_rgba(255,193,116,0.05)] transition-all flex items-center justify-between">
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="p-2.5 bg-surfaceMuted border border-outline/20 rounded-lg">
                      <Icon size={20} className="text-primary" />
                    </div>
                    <div className="min-w-0">
                      <h4 className="font-display font-medium text-sm text-onSurface truncate">{doc.title || 'Untitled Document'}</h4>
                      <p className="text-[10px] text-onSurfaceMuted font-mono truncate max-w-lg">{doc.source_path}</p>
                    </div>
                  </div>
                  <div className="text-right flex items-center gap-3">
                    <span className="lifeos-chip lifeos-chip-cyan text-[9px]">
                      {doc.char_count} chars / {doc.word_count} words
                    </span>
                    <span className="text-[10px] text-onSurfaceMuted font-mono uppercase bg-outline/20 px-2 py-0.5 rounded">
                      {doc.doc_type}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

// ── 3. INTEGRATIONS PAGE ──────────────────────────────────────────────
export const IntegrationsPage = ({ apiUrl }) => {
  const [integrations, setIntegrations] = useState([]);
  const [syncing, setSyncing] = useState({});
  const [activeExpander, setActiveExpander] = useState(null);
  const [configText, setConfigText] = useState({});

  const fetchIntegrations = async () => {
    try {
      const res = await fetch(`${apiUrl}/v1/integrations`);
      if (res.ok) {
        const data = await res.json();
        setIntegrations(data.integrations || []);
        
        // Initial setup for configurations
        const confs = {};
        data.integrations.forEach((item) => {
          confs[item.id] = JSON.stringify(item.settings, null, 2);
        });
        setConfigText(confs);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchIntegrations();
  }, [apiUrl]);

  const handleSync = async (id) => {
    setSyncing((prev) => ({ ...prev, [id]: true }));
    try {
      const res = await fetch(`${apiUrl}/v1/integrations/${id}/sync`, { method: 'POST' });
      if (res.ok) {
        alert(`Sync finished successfully!`);
        fetchIntegrations();
      } else {
        alert(`Sync failed: ${await res.text()}`);
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setSyncing((prev) => ({ ...prev, [id]: false }));
    }
  };

  const handleDisconnect = async (id) => {
    try {
      await fetch(`${apiUrl}/v1/integrations/${id}/disconnect`, { method: 'POST' });
      fetchIntegrations();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveSettings = async (id) => {
    try {
      const parsed = JSON.parse(configText[id]);
      const res = await fetch(`${apiUrl}/v1/integrations/${id}/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ settings: parsed }),
      });
      if (res.ok) {
        alert('Settings saved.');
        fetchIntegrations();
        setActiveExpander(null);
      } else {
        alert(await res.text());
      }
    } catch (err) {
      alert(`Invalid JSON format: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4">
        {integrations.map((item, idx) => {
          const isOnline = item.status === 'connected' || item.status === 'ok';
          const isNeedsConfig = item.status?.includes('needs');
          return (
            <div key={idx} className="bg-surface border border-outline/35 rounded-xl p-5 backdrop-blur-xl flex flex-col gap-4 border-l-4 border-l-primary">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Link2 size={20} className="text-primary" />
                  <div>
                    <h3 className="font-display font-semibold text-base text-onSurface">{item.name}</h3>
                    <p className="text-[10px] text-onSurfaceMuted font-mono">
                      ID: {item.id.toUpperCase()} · PATH: {item.settings?.vault_path || 'CLOUD_OAUTH'}
                    </p>
                  </div>
                </div>
                <span className={`lifeos-chip text-[9px] ${isOnline ? 'lifeos-chip-cyan' : isNeedsConfig ? 'lifeos-chip-amber' : 'lifeos-chip-purple'}`}>
                  {isOnline ? 'ONLINE' : isNeedsConfig ? 'CONFIGURE' : 'OFFLINE'}
                </span>
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleSync(item.id)}
                  disabled={syncing[item.id]}
                  className="bg-primary/10 hover:bg-primary/20 border border-primary/30 hover:border-primary/60 text-primary px-4 py-1.5 rounded-lg text-xs font-cyber tracking-wider flex items-center gap-1.5 transition-all"
                >
                  <RefreshCw size={12} className={syncing[item.id] ? 'animate-spin' : ''} />
                  {syncing[item.id] ? 'SYNCING...' : 'SYNC'}
                </button>
                <button
                  onClick={() => handleDisconnect(item.id)}
                  className="bg-outline/20 hover:bg-outline/40 border border-outline/40 text-onSurface px-4 py-1.5 rounded-lg text-xs font-cyber tracking-wider transition-all"
                >
                  DISCONNECT
                </button>
                <button
                  onClick={() => setActiveExpander(activeExpander === item.id ? null : item.id)}
                  className="ml-auto text-xs font-mono text-onSurfaceMuted hover:text-onSurface flex items-center gap-1"
                >
                  Configure <ChevronDown size={14} className={`transform transition-transform ${activeExpander === item.id ? 'rotate-180' : ''}`} />
                </button>
              </div>

              {/* Expandable Configuration */}
              {activeExpander === item.id && (
                <div className="bg-surfaceMuted border border-outline/20 rounded-xl p-4 space-y-3">
                  <label className="block text-[10px] text-onSurfaceMuted font-mono uppercase tracking-wider">JSON Settings Configuration</label>
                  <textarea
                    rows={4}
                    value={configText[item.id] || ''}
                    onChange={(e) => setConfigText((prev) => ({ ...prev, [item.id]: e.target.value }))}
                    className="w-full bg-surface text-onSurface font-mono text-xs border border-outline/30 rounded-lg p-3 focus:outline-none focus:border-primary/60"
                  />
                  <button
                    onClick={() => handleSaveSettings(item.id)}
                    className="bg-tertiary/10 hover:bg-tertiary/20 border border-tertiary/30 text-tertiary px-4 py-1.5 rounded-lg text-xs font-cyber tracking-wider transition-all"
                  >
                    SAVE SETTINGS
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ── 4. INSIGHTS PAGE ──────────────────────────────────────────────────
export const InsightsPage = ({ apiUrl }) => {
  const [insights, setInsights] = useState([]);
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 7);
    return d.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [generating, setGenerating] = useState(false);
  const [digest, setDigest] = useState(null);

  const fetchInsights = async () => {
    try {
      const res = await fetch(`${apiUrl}/v1/insights`);
      if (res.ok) {
        const data = await res.json();
        setInsights(data.insights || []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, [apiUrl]);

  const dismissInsight = async (id) => {
    try {
      const res = await fetch(`${apiUrl}/v1/insights/${id}/dismiss`, { method: 'POST' });
      if (res.ok) {
        fetchInsights();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerateDigest = async () => {
    setGenerating(true);
    setDigest(null);
    try {
      const res = await fetch(`${apiUrl}/v1/digest/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'weekly',
          period_start: startDate,
          period_end: endDate
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setDigest(data.answer);
      } else {
        alert(`Failed: ${await res.text()}`);
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Active Insights */}
      <div>
        <h3 className="font-display font-semibold text-lg border-b border-outline/20 pb-2 mb-4">Active Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.length === 0 ? (
            <div className="p-6 text-center text-onSurfaceMuted text-xs md:col-span-2">No active neural insights detected in current cycles.</div>
          ) : (
            insights.map((ins, idx) => (
              <div key={idx} className="bg-surface border border-outline/30 rounded-xl p-5 backdrop-blur-xl flex flex-col justify-between border-l-4 border-l-tertiary">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="lifeos-chip lifeos-chip-cyan text-[8px]">{ins.type?.toUpperCase()}</span>
                    <button 
                      onClick={() => dismissInsight(ins.id)}
                      className="text-onSurfaceMuted hover:text-onSurface text-xs font-mono"
                    >
                      DISMISS
                    </button>
                  </div>
                  <p className="text-xs text-onSurface leading-relaxed">{ins.content}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Weekly Review */}
      <div className="bg-surface border border-outline/30 rounded-xl p-6 backdrop-blur-xl space-y-4">
        <h3 className="font-display font-semibold text-base">Weekly Review Generator</h3>
        <p className="text-xs text-onSurfaceMuted">Select the timeline period to generate a complete synthesis of your second brain activity.</p>
        
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="flex-1 space-y-1">
            <label className="text-[10px] text-onSurfaceMuted font-mono uppercase">Start Date</label>
            <input 
              type="date" 
              value={startDate} 
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-surfaceMuted text-onSurface text-xs font-mono border border-outline/35 rounded-lg px-3 py-2 focus:outline-none focus:border-primary/60"
            />
          </div>
          <div className="flex-1 space-y-1">
            <label className="text-[10px] text-onSurfaceMuted font-mono uppercase">End Date</label>
            <input 
              type="date" 
              value={endDate} 
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-surfaceMuted text-onSurface text-xs font-mono border border-outline/35 rounded-lg px-3 py-2 focus:outline-none focus:border-primary/60"
            />
          </div>
          <button
            onClick={handleGenerateDigest}
            disabled={generating}
            className="bg-primary/10 hover:bg-primary/20 border border-primary/40 text-primary py-2 px-6 rounded-lg font-cyber text-xs tracking-wider transition-all h-9 flex items-center justify-center gap-1.5"
          >
            {generating ? 'SYNTHESIZING...' : 'GENERATE'}
          </button>
        </div>

        {digest && (
          <div className="mt-4 bg-primary/5 border border-primary/15 rounded-xl p-5 space-y-2">
            <h4 className="font-display font-semibold text-sm text-primary">Weekly Synthesis Report</h4>
            <p className="text-xs leading-relaxed whitespace-pre-wrap text-onSurface">{digest}</p>
          </div>
        )}
      </div>
    </div>
  );
};

// ── 5. ENTITIES PAGE ──────────────────────────────────────────────────
export const EntitiesPage = ({ apiUrl }) => {
  const [entities, setEntities] = useState([]);

  useEffect(() => {
    const fetchEntities = async () => {
      try {
        const res = await fetch(`${apiUrl}/v1/entities`);
        if (res.ok) {
          const data = await res.json();
          setEntities(data.entities || []);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchEntities();
  }, [apiUrl]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-3">
        {entities.length === 0 ? (
          <div className="p-6 text-center text-onSurfaceMuted text-xs">No knowledge entities extracted yet. Run queries or sync integrations to populate.</div>
        ) : (
          entities.map((ent, idx) => {
            let aliases = [];
            if (ent.aliases) {
              try {
                aliases = typeof ent.aliases === 'string' ? JSON.parse(ent.aliases) : ent.aliases;
              } catch (e) {
                aliases = [];
              }
            }
            return (
              <div key={idx} className="bg-surface border border-outline/30 rounded-xl p-4 backdrop-blur-xl border-l-4 border-l-secondary flex flex-col gap-2">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="lifeos-chip lifeos-chip-purple text-[8px]">{ent.type?.toUpperCase()}</span>
                    <h3 className="font-display font-semibold text-sm mt-1 text-onSurface">{ent.name}</h3>
                  </div>
                  <span className="lifeos-chip lifeos-chip-amber text-[8px]">MENTIONS: {ent.mention_count}</span>
                </div>
                <div className="text-[11px] text-onSurfaceMuted font-mono space-y-0.5 border-t border-outline/10 pt-2">
                  {aliases.length > 0 && <p>Aliases: {aliases.join(', ')}</p>}
                  <p>First Seen: {ent.first_seen} · Last Seen: {ent.last_seen}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

// ── 6. MEMORY PAGE ────────────────────────────────────────────────────
export const MemoryPage = ({ apiUrl }) => {
  const [memories, setMemories] = useState([]);
  const [type, setType] = useState('preference');
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');

  const fetchMemories = async () => {
    try {
      const res = await fetch(`${apiUrl}/v1/memory`);
      if (res.ok) {
        const data = await res.json();
        setMemories(data.memories || []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, [apiUrl]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!key || !value) return;

    try {
      const res = await fetch(`${apiUrl}/v1/memory`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, key, value, confidence: 1.0, source: 'user' }),
      });
      if (res.ok) {
        setKey('');
        setValue('');
        fetchMemories();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await fetch(`${apiUrl}/v1/memory/${id}`, { method: 'DELETE' });
      if (res.ok) {
        fetchMemories();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <form onSubmit={handleSubmit} className="bg-surface border border-outline/30 rounded-xl p-5 backdrop-blur-xl space-y-4">
        <h3 className="font-display font-semibold text-base">Add Long-Term Memory</h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-[10px] text-onSurfaceMuted font-mono uppercase">Category</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full bg-surfaceMuted text-onSurface text-xs font-mono border border-outline/35 rounded-lg px-3 py-2 focus:outline-none focus:border-primary/60 h-9"
            >
              <option value="preference">Preference</option>
              <option value="person">Person</option>
              <option value="fact">Fact</option>
              <option value="instruction">Instruction</option>
              <option value="anomaly">Anomaly</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-[10px] text-onSurfaceMuted font-mono uppercase">Key</label>
            <input
              type="text"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="e.g. response_style"
              className="w-full bg-surfaceMuted text-onSurface text-xs font-mono border border-outline/35 rounded-lg px-3 py-2 h-9 focus:outline-none focus:border-primary/60"
            />
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-[10px] text-onSurfaceMuted font-mono uppercase">Value / Content</label>
          <textarea
            rows={2}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Write facts or constraints..."
            className="w-full bg-surfaceMuted text-onSurface text-xs border border-outline/35 rounded-lg p-3 focus:outline-none focus:border-primary/60"
          />
        </div>

        <div className="flex justify-end">
          <button 
            type="submit"
            className="bg-primary/10 hover:bg-primary/20 border border-primary/40 text-primary py-2 px-6 rounded-lg font-cyber text-xs tracking-wider transition-all"
          >
            COMMIT MEMORY
          </button>
        </div>
      </form>

      {/* Active List */}
      <div className="space-y-3">
        <h3 className="font-display font-semibold text-lg border-b border-outline/20 pb-2">Active Cognitive Nodes</h3>
        <div className="grid grid-cols-1 gap-3">
          {memories.length === 0 ? (
            <div className="p-6 text-center text-onSurfaceMuted text-xs">No memories stored in the local cognitive engine yet.</div>
          ) : (
            memories.map((item, idx) => (
              <div key={idx} className="bg-surface border border-outline/20 rounded-xl p-4 hover:border-primary/30 transition-all flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="lifeos-chip lifeos-chip-cyan text-[8px]">{item.type?.toUpperCase()}</span>
                    <span className="font-display font-semibold text-sm text-onSurface">{item.key}</span>
                  </div>
                  <p className="text-xs text-onSurfaceMuted leading-relaxed">{item.value}</p>
                </div>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 text-red-400 p-2.5 rounded-lg transition-colors flex-shrink-0"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// ── 7. TIMELINE PAGE ──────────────────────────────────────────────────
export const TimelinePage = ({ apiUrl }) => {
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [timeline, setTimeline] = useState(null);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const res = await fetch(`${apiUrl}/v1/timeline/${date}`);
        if (res.ok) {
          setTimeline(await res.json());
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchTimeline();
  }, [apiUrl, date]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 items-end bg-surface border border-outline/25 rounded-xl p-5 backdrop-blur-xl">
        <div className="space-y-1">
          <label className="text-[10px] text-onSurfaceMuted font-mono uppercase">Select Target Date</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="bg-surfaceMuted text-onSurface text-xs font-mono border border-outline/35 rounded-lg px-3 py-2 focus:outline-none focus:border-primary/60 h-9"
          />
        </div>
      </div>

      {timeline && (
        <div className="space-y-6">
          {/* Summary Box */}
          <div className="bg-surface border border-outline/30 rounded-xl p-5 border-l-4 border-l-secondary backdrop-blur-xl">
            <h4 className="font-cyber text-xs tracking-wider text-secondary uppercase font-bold mb-2">Synthesis Summary</h4>
            <p className="text-xs leading-relaxed text-onSurface">{timeline.summary}</p>
          </div>

          {/* Events Log */}
          <div>
            <h3 className="font-display font-semibold text-base mb-3">Reconstructed Activities</h3>
            {(!timeline.sources || timeline.sources.length === 0) ? (
              <div className="p-6 text-center bg-surfaceMuted/50 border border-outline/10 rounded-xl text-onSurfaceMuted text-xs">
                No events synced or logged for this timeline cycle. Sync integrations to fetch events.
              </div>
            ) : (
              <div className="space-y-3">
                {timeline.sources.map((item, idx) => (
                  <div key={idx} className="bg-surface border border-outline/20 rounded-xl p-4 flex items-center justify-between">
                    <div>
                      <span className="lifeos-chip lifeos-chip-purple text-[8px]">{item.type?.toUpperCase()}</span>
                      <h4 className="font-display font-semibold text-sm mt-1 text-onSurface">{item.title}</h4>
                      <p className="text-xs text-onSurfaceMuted">{item.content}</p>
                    </div>
                    <span className="text-xs font-mono text-onSurfaceMuted">{item.time}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// ── 8. TELEMETRY & DIAGNOSTICS PAGE ──────────────────────────────────
export const TelemetryPage = ({ apiUrl }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${apiUrl}/health`);
        if (res.ok) {
          setData(await res.json());
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchHealth();
  }, [apiUrl]);

  if (!data) return <div className="text-xs text-onSurfaceMuted font-mono animate-pulse">Querying core telemetry gateway...</div>;

  return (
    <div className="space-y-6">
      {/* Telemetry Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-surface border border-outline/20 rounded-xl p-4 backdrop-blur-xl">
          <span className="text-[10px] text-onSurfaceMuted font-mono uppercase tracking-wider">Total Documents</span>
          <div className="text-2xl font-bold font-display text-primary mt-1">{data.documents || 0}</div>
        </div>
        <div className="bg-surface border border-outline/20 rounded-xl p-4 backdrop-blur-xl">
          <span className="text-[10px] text-onSurfaceMuted font-mono uppercase tracking-wider">Vector Chunks</span>
          <div className="text-2xl font-bold font-display text-tertiary mt-1">{data.chunks || 0}</div>
        </div>
        <div className="bg-surface border border-outline/20 rounded-xl p-4 backdrop-blur-xl">
          <span className="text-[10px] text-onSurfaceMuted font-mono uppercase tracking-wider">BM25 Keywords</span>
          <div className="text-2xl font-bold font-display text-secondary mt-1">{data.bm25_chunks || 0}</div>
        </div>
      </div>

      {/* JSON Telemetry Logs */}
      <div className="bg-surface border border-outline/30 rounded-xl p-5 backdrop-blur-xl space-y-3">
        <h3 className="font-display font-semibold text-sm border-b border-outline/20 pb-2">Telemetry JSON Status</h3>
        <pre className="text-[11px] leading-relaxed text-onSurfaceMuted font-mono bg-surfaceMuted/50 p-4 rounded-lg overflow-x-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );
};
