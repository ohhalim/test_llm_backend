import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터: 모든 요청에 토큰 추가
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 에러 시 토큰 제거 및 로그인 페이지로 리다이렉트
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 인증 관련 API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
};

// 게시글 관련 API
export const postsAPI = {
  getPosts: (page = 1, size = 10) => api.get(`/posts?page=${page}&size=${size}`),
  getPost: (id) => api.get(`/posts/${id}`),
  createPost: (postData) => api.post('/posts', postData),
  updatePost: (id, postData) => api.put(`/posts/${id}`, postData),
  deletePost: (id) => api.delete(`/posts/${id}`),
};

// AI 에이전트 관련 API
const AI_API_BASE_URL = process.env.REACT_APP_AI_AGENT_URL || 'http://localhost:8081';
const aiApi = axios.create({
  baseURL: AI_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const aiAPI = {
  chat: (query, userId = null) => aiApi.post('/ai/chat', { query, user_id: userId }),
  searchMedical: (query, limit = 5) => aiApi.post('/ai/search-medical', { query, limit }),
  medicalQA: (question, limit = 5) => aiApi.post('/ai/medical-qa', { question, limit }),
  getMedicalStats: () => aiApi.get('/ai/medical-stats'),
  getRagHealth: () => aiApi.get('/ai/rag-health'),
  searchPosts: (query, userId = null, limit = 5) => aiApi.get('/ai/search', { params: { query, user_id: userId, limit } }),
};

export default api;