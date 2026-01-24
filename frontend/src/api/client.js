import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatService = {
  sendMessage: async (message, history = []) => {
    const response = await apiClient.post('/api/v1/chat', { message, history });
    return response.data;
  },
  
  getSchema: async () => {
    const response = await apiClient.get('/api/v1/schema');
    return response.data;
  },
  
  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
  
  getLineage: async () => {
    const response = await apiClient.get('/api/v1/lineage');
    return response.data;
  }
};
