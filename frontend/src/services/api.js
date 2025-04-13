// API service for communicating with the Python backend

// Base URL for API requests
const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://ai-tutor-backend-be.onrender.com' // Your Render backend URL
  : 'http://localhost:8000'; // In development, use the local backend

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    // Handle 401 Unauthorized errors
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Authentication failed. Please log in again.');
    }
    
    // Handle other errors
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }
  
  return response.json();
};

// Authentication API
export const authAPI = {
  // Sign up new user
  signup: async (userData) => {
    const response = await fetch(`${API_URL}/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    return handleResponse(response);
  },

  // Login and get token
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_URL}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
    
    return handleResponse(response);
  },
  
  // Google authentication
  googleAuth: async (googleToken) => {
    const response = await fetch(`${API_URL}/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ access_token: googleToken }),
    });
    
    return handleResponse(response);
  },
  
  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
  
  // Get authentication token
  getToken: () => {
    return localStorage.getItem('token');
  },
  
  // Set authentication token
  setToken: (token) => {
    localStorage.setItem('token', token);
  },
  
  // Remove authentication token (logout)
  logout: () => {
    localStorage.removeItem('token');
  },
};

// Tutor API
export const tutorAPI = {
  // Ask a question and get tutor response
  askQuestion: async (topic) => {
    const token = authAPI.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_URL}/tutor?topic=${encodeURIComponent(topic)}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    const data = await handleResponse(response);
    return data.response;
  },
  
  // Upload a document for analysis
  uploadDocument: async (file) => {
    const token = authAPI.getToken();
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });
    
    const data = await handleResponse(response);
    return data.response;
  },
};

export default {
  auth: authAPI,
  tutor: tutorAPI,
}; 