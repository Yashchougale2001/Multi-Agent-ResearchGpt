// API service
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const researchAPI = {
  startResearch: async (query) => {
    const response = await apiClient.post("/api/research", { query });
    return response.data;
  },

  getResult: async (sessionId) => {
    const response = await apiClient.get(`/api/research/${sessionId}`);
    return response.data;
  },

  uploadDocument: async (content, metadata) => {
    const response = await apiClient.post("/api/documents/upload", {
      content,
      metadata,
    });
    return response.data;
  },

  getStats: async () => {
    const response = await apiClient.get("/stats");
    return response.data;
  },

  deleteSession: async (sessionId) => {
    const response = await apiClient.delete(`/api/sessions/${sessionId}`);
    return response.data;
  },
};

export default apiClient;
