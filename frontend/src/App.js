import React, { useState, useEffect } from 'react';
import './App.css';
import { 
  askBot,
  getDashboard
} from './api';

function App() {
  // State for dashboard data
  const [metrics, setMetrics] = useState({ 
    rrf: 0, 
    bench: 0, 
    projects: 0, 
    trainees: 0 
  });
  const [recentRRF, setRecentRRF] = useState([]);
  const [training, setTraining] = useState([]);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  // QA Chat state
  const [isQAChatOpen, setIsQAChatOpen] = useState(false);
  const [botInput, setBotInput] = useState("");
  const [botMessages, setBotMessages] = useState([]);
  const [botLoading, setBotLoading] = useState(false);

  useEffect(() => {
    async function fetchDashboard() {
      setError(null);
      try {
        const data = await getDashboard();
        setMetrics({
          rrf: data.active_rrfs || 0,
          bench: data.bench_resources || 0,
          projects: data.active_projects || 0,
          trainees: data.trainees || 0
        });
        setRecentRRF(data.recent_rrf_updates || []);
        setTraining(data.training_progress || []);
      } catch (err) {
        setError('Failed to load dashboard data');
      }
    }
    fetchDashboard();
  }, []);

  // Handle bot question submit
  const handleBotSubmit = async (e) => {
    e.preventDefault();
    if (!botInput.trim()) return;
    setBotLoading(true);
    setBotMessages((msgs) => [...msgs, { sender: "user", text: botInput }]);
    try {
      const res = await askBot(botInput);
      setBotMessages((msgs) => [...msgs, { sender: "bot", text: res.answer }]);
    } catch {
      setBotMessages((msgs) => [...msgs, { sender: "bot", text: "Sorry, I couldn't process your request." }]);
    }
    setBotInput("");
    setBotLoading(false);
  };

  const toggleQAChat = () => {
    setIsQAChatOpen(!isQAChatOpen);
  };

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'rrfs', label: 'RRFs', icon: '📋' },
    { id: 'resources', label: 'Resources', icon: '👥' },
    { id: 'projects', label: 'Projects', icon: '🏗️' },
    { id: 'training', label: 'Training', icon: '🎓' },
    { id: 'reports', label: 'Reports', icon: '📈' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  const handleTokenSetup = () => {
    window.open('/api/token-setup', '_blank');
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo-section">
            <div className="logo-icon">🏢</div>
            <div className="logo-text">
              <h1>Ops Bot</h1>
              <p>Enterprise Operations</p>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* QA Assistant Section */}
        <div className="qa-assistant-section">
          <div className="qa-help-text">
            <h4>Need help with your tasks?</h4>
            <p>Our AI agent can help you get started with your tasks and workflows.</p>
          </div>
          <button 
            className="qa-assistant-button"
            onClick={toggleQAChat}
          >
            <div className="qa-icon">🤖</div>
            <span className="qa-text">Ask Ops QA</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <header className="main-header">
          <div className="header-left">
            <h1 className="page-title">Dashboard</h1>
          </div>
          <div className="header-right">
            <div className="search-bar">
              <span className="search-icon">🔍</span>
              <input type="text" placeholder="Search..." />
            </div>
            <div className="header-actions">
              <button className="notification-btn">🔔</button>
              <div className="user-profile">
                <div className="user-avatar">👤</div>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="dashboard-content">
          {activeTab === 'dashboard' && (
            <>
              {/* Metrics Grid */}
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-icon">📋</div>
                  <div className="metric-content">
                    <div className="metric-value">{metrics.rrf}</div>
                    <div className="metric-label">Active RRFs</div>
                    <div className="metric-change">Resource requests</div>
                  </div>
                </div>
                <div className="metric-card">
                  <div className="metric-icon">🪑</div>
                  <div className="metric-content">
                    <div className="metric-value">{metrics.bench}</div>
                    <div className="metric-label">Bench Resources</div>
                    <div className="metric-change">Available resources</div>
                  </div>
                </div>
                <div className="metric-card">
                  <div className="metric-icon">🏗️</div>
                  <div className="metric-content">
                    <div className="metric-value">{metrics.projects}</div>
                    <div className="metric-label">Active Projects</div>
                    <div className="metric-change">Ongoing projects</div>
                  </div>
                </div>
                <div className="metric-card">
                  <div className="metric-icon">🎓</div>
                  <div className="metric-content">
                    <div className="metric-value">{metrics.trainees}</div>
                    <div className="metric-label">Trainees</div>
                    <div className="metric-change">In training programs</div>
                  </div>
                </div>
              </div>

              {/* Operations Overview Chart */}
              <div className="chart-section">
                <div className="chart-card">
                  <div className="chart-header">
                    <h3>Operations Overview</h3>
                    <p>Resource allocation and project status over the last 7 days.</p>
                  </div>
                  <div className="chart-content">
                    <div className="chart-placeholder">
                      <div className="chart-line"></div>
                      <div className="chart-labels">
                        <div className="y-axis-left">
                          <span>80</span>
                          <span>120</span>
                          <span>160</span>
                        </div>
                        <div className="y-axis-right">
                          <span>50</span>
                          <span>75</span>
                          <span>100</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'settings' && (
            <div className="settings-content">
              <div className="settings-card">
                <h3>OneDrive Integration</h3>
                <p>Configure your OneDrive connection to access real data from your files.</p>
                <div className="settings-actions">
                  <button 
                    className="settings-button primary"
                    onClick={handleTokenSetup}
                  >
                    <span className="button-icon">🔐</span>
                    Setup OneDrive Token
                  </button>
                  <div className="settings-info">
                    <p>This will open a setup page where you can:</p>
                    <ul>
                      <li>Get your OneDrive access token</li>
                      <li>Test the connection</li>
                      <li>Configure the integration</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* QA Chat Modal */}
      {isQAChatOpen && (
        <div className="qa-chat-modal">
          <div className="qa-chat-container">
            <div className="qa-chat-header">
              <div className="qa-header-content">
                <div className="qa-avatar">🤖</div>
                <div className="qa-info">
                  <h3>Ops QA Assistant</h3>
                  <p>AI-powered operations support</p>
                </div>
              </div>
              <button 
                className="close-button"
                onClick={toggleQAChat}
                aria-label="Close chat"
              >
                ✕
              </button>
            </div>

            <div className="qa-chat-messages">
              {botMessages.length === 0 && (
                <div className="welcome-message">
                  <div className="welcome-content">
                    <h4>Welcome to Ops QA! 👋</h4>
                    <p>I'm your AI assistant for operations, resources, and training. How can I help you today?</p>
                    <div className="suggested-questions">
                      <button 
                        className="suggestion-chip"
                        onClick={() => setBotInput("Show me active RRFs")}
                      >
                        Show me active RRFs
                      </button>
                      <button 
                        className="suggestion-chip"
                        onClick={() => setBotInput("What training is available?")}
                      >
                        What training is available?
                      </button>
                      <button 
                        className="suggestion-chip"
                        onClick={() => setBotInput("Bench resource status")}
                      >
                        Bench resource status
                      </button>
                    </div>
                  </div>
                </div>
              )}
              
              {botMessages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.sender}`}>
                  <div className="message-avatar">
                    {msg.sender === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{msg.text}</div>
                    <div className="message-time">
                      {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </div>
                  </div>
                </div>
              ))}
              
              {botLoading && (
                <div className="message bot">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <form className="qa-chat-input-form" onSubmit={handleBotSubmit}>
              <div className="input-container">
                <input
                  type="text"
                  value={botInput}
                  onChange={e => setBotInput(e.target.value)}
                  placeholder="Ask me anything about operations..."
                  disabled={botLoading}
                  className="qa-chat-input"
                />
                <button 
                  type="submit" 
                  disabled={botLoading || !botInput.trim()} 
                  className="qa-send-button"
                >
                  <span className="send-icon">➤</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {error && (
        <div className="error-toast">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{error}</span>
        </div>
      )}
    </div>
  );
}

export default App;