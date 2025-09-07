import React, { useState, useEffect } from 'react';
import './App.css';
import { 
  askBot,
  getDashboard
} from './api';

function App() {
  // State for dashboard data
  const [metrics, setMetrics] = useState({ rrf: 0, bench: 0, projects: 0, trainees: 0 });
  const [recentRRF, setRecentRRF] = useState([]);
  const [training, setTraining] = useState([]);
  const [error, setError] = useState(null);

  // QA Chat state
  const [isQAChatOpen, setIsQAChatOpen] = useState(false);
  const [botInput, setBotInput] = useState("");
  const [botMessages, setBotMessages] = useState([]);
  const [botLoading, setBotLoading] = useState(false);

  useEffect(() => {
    async function fetchDashboard() {
      setLoading(true);
      setError(null);
      try {
        const data = await getDashboard();
        setMetrics({
          rrf: data.active_rrfs,
          bench: data.bench_resources,
          projects: data.active_projects,
          trainees: data.trainees
        });
        setRecentRRF(data.recent_rrf_updates || []);
        setTraining(data.training_progress || []);
      } catch (err) {
        setError('Failed to load dashboard data');
      }
      setLoading(false);
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

  return (
    <div className="app-container">
      {/* Main Dashboard */}
      <div className="dashboard-container">
        <header className="dashboard-header">
          <div className="header-content">
            <div className="logo-section">
              <div className="logo-icon">🏢</div>
              <div className="logo-text">
                <h1>Operations Hub</h1>
                <p>Enterprise Resource Management</p>
              </div>
            </div>
            <div className="user-profile">
              <div className="user-info">
                <span className="user-name">Sarah Johnson</span>
                <span className="user-role">Operations Manager</span>
              </div>
              <div className="user-avatar">👤</div>
            </div>
          </div>
        </header>

        <main className="dashboard-main">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">📋</div>
              <div className="metric-content">
                <div className="metric-value">{metrics.rrf}</div>
                <div className="metric-label">Active RRFs</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">🪑</div>
              <div className="metric-content">
                <div className="metric-value">{metrics.bench}</div>
                <div className="metric-label">Bench Resources</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">🏗️</div>
              <div className="metric-content">
                <div className="metric-value">{metrics.projects}</div>
                <div className="metric-label">Active Projects</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">🎓</div>
              <div className="metric-content">
                <div className="metric-value">{metrics.trainees}</div>
                <div className="metric-label">Trainees</div>
              </div>
            </div>
          </div>

          <div className="content-grid">
            <div className="content-card">
              <h3>Recent RRF Updates</h3>
              <div className="card-content">
                {recentRRF.length === 0 ? (
                  <div className="empty-state">No recent RRF updates</div>
                ) : (
                  recentRRF.map((item, idx) => (
                    <div className="list-item" key={idx}>
                      <div className="item-content">
                        <div className="item-title">{item.role}</div>
                        <div className="item-subtitle">Client: {item.client}</div>
                      </div>
                      <span className={`status-badge ${item.status.toLowerCase()}`}>
                        {item.status}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="content-card">
              <h3>Training Progress</h3>
              <div className="card-content">
                {training.length === 0 ? (
                  <div className="empty-state">No training progress data</div>
                ) : (
                  training.map((item, idx) => (
                    <div className="list-item" key={idx}>
                      <div className="item-content">
                        <div className="item-title">{item.title}</div>
                        <div className="item-subtitle">{item.trainees} trainees</div>
                      </div>
                      <span className={`status-badge ${item.status.toLowerCase()}`}>
                        {item.progress}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Floating QA Chat Button */}
      <button 
        className={`qa-chat-button ${isQAChatOpen ? 'active' : ''}`}
        onClick={toggleQAChat}
        aria-label="Open QA Assistant"
      >
        <div className="chat-icon">
          {isQAChatOpen ? '✕' : '💬'}
        </div>
        <span className="chat-label">QA Assistant</span>
      </button>

      {/* QA Chat Modal */}
      {isQAChatOpen && (
        <div className="qa-chat-modal">
          <div className="qa-chat-container">
            <div className="qa-chat-header">
              <div className="qa-header-content">
                <div className="qa-avatar">🤖</div>
                <div className="qa-info">
                  <h3>OpBot Assistant</h3>
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
                    <h4>Welcome to OpBot! 👋</h4>
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