// API configuration and functions for the Operations Bot
const API_BASE_URL = process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000');

// Helper function to make API requests
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to Operations Bot. Please ensure the backend is running.');
    }
    throw error;
  }
}

// Ask the bot a question
export async function askBot(question) {
  if (!question || !question.trim()) {
    throw new Error('Question is required');
  }
  
  return await apiRequest('/bot/ask', {
    method: 'POST',
    body: JSON.stringify({ question: question.trim() }),
  });
}

// Get bot status and health
export async function getBotStatus() {
  return await apiRequest('/bot/status');
}

// Get dashboard data
export async function getDashboard() {
  return await apiRequest('/bot/dashboard');
}

// Get category details
export async function getCategoryDetails(category) {
  if (!category) {
    throw new Error('Category is required');
  }
  
  return await apiRequest('/bot/category', {
    method: 'POST',
    body: JSON.stringify({ category }),
  });
}

// Scan all data (admin function)
export async function scanAllData() {
  return await apiRequest('/bot/scan', {
    method: 'POST',
  });
}

// Health check
export async function checkBackendHealth() {
  return await apiRequest('/');
}
