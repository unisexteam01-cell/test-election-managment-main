import axios, { AxiosInstance, AxiosError } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

// Resolve backend host in this order:
// 1. Expo runtime config `extra.backendUrl` (set by `app.config.js` / EAS)
// 2. environment variable available during dev `process.env.EXPO_PUBLIC_BACKEND_URL`
// 3. Android emulator loopback `10.0.2.2:8004` for local testing
const runtimeExtra = (Constants.expoConfig && (Constants.expoConfig.extra as any)) || {};
const BACKEND_HOST = runtimeExtra.backendUrl || process.env.EXPO_PUBLIC_BACKEND_URL || 'http://10.0.2.2:8004';
const API_URL = `${BACKEND_HOST.replace(/\/$/, '')}/api`;

// Debug: print resolved API URL at runtime to help diagnose emulator network issues
try {
  // eslint-disable-next-line no-console
  console.log('Resolved API_URL for ApiService:', API_URL);
} catch (e) {}

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          await AsyncStorage.removeItem('auth_token');
          await AsyncStorage.removeItem('user');
          // Navigation to login will be handled by auth context
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth APIs
  async login(username: string, password: string) {
    const response = await this.api.post('/auth/login', { username, password });
    return response.data;
  }

  async register(userData: any) {
    const response = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.api.get('/auth/me');
    return response.data;
  }

  async getUsers(role?: string) {
    const response = await this.api.get('/auth/users', {
      params: { role },
    });
    return response.data;
  }

  async createSuperAdmin(data: any) {
    const response = await this.api.post('/auth/create-super-admin', data);
    return response.data;
  }

  // Voter APIs
  async getVoters(params: any = {}) {
    const response = await this.api.get('/voters', { params });
    return response.data;
  }

  async getVoter(id: string) {
    const response = await this.api.get(`/voters/${id}`);
    return response.data;
  }

  async createVoter(voterData: any) {
    const response = await this.api.post('/voters', voterData);
    return response.data;
  }

  async updateVoter(id: string, voterData: any) {
    const response = await this.api.put(`/voters/${id}`, voterData);
    return response.data;
  }

  async deleteVoter(id: string) {
    const response = await this.api.delete(`/voters/${id}`);
    return response.data;
  }

  async markVoterVisited(id: string) {
    const response = await this.api.post(`/voters/${id}/mark-visited`);
    return response.data;
  }

  async markVoterVoted(id: string) {
    const response = await this.api.post(`/voters/${id}/mark-voted`);
    return response.data;
  }

  async assignVoters(voterIds: string[], karyakartaId: string, mode: string = 'manual') {
    const response = await this.api.post('/voters/assign', {
      voter_ids: voterIds,
      karyakarta_id: karyakartaId,
      mode,
    });
    return response.data;
  }

  async bulkUpdateVoters(voterIds: string[], updates: any) {
    const response = await this.api.post('/voters/bulk-update', {
      voter_ids: voterIds,
      updates,
    });
    return response.data;
  }

  async exportVoters(filters: any) {
    const response = await this.api.get('/voters/export', { params: filters, responseType: 'blob' as any });
    return response.data;
  }

  // Import endpoints (use /import routes)
  async uploadCsv(file: any) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.api.post('/import/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async mapColumns(sessionId: string, columnMapping: any, adminId: string) {
    const response = await this.api.post('/import/map-columns', {
      session_id: sessionId,
      column_mapping: columnMapping,
      admin_id: adminId,
    });
    return response.data;
  }

  // Survey APIs

  async getSurveyTemplates() {
    const response = await this.api.get('/survey-templates');
    return response.data;
  }

  async getSurveyTemplateById(templateId: string) {
    const response = await this.api.get(`/survey-templates/${templateId}`);
    return response.data;
  }

  async createSurveyTemplate(templateData: any) {
    const response = await this.api.post('/survey-templates', templateData);
    return response.data;
  }

  async submitSurvey(surveyData: any) {
    const response = await this.api.post('/surveys/submit', surveyData);
    return response.data;
  }

  async getVoterSurveys(voterId: string) {
    const response = await this.api.get(`/surveys/voter/${voterId}`);
    return response.data;
  }

  async getMySurveys() {
    const response = await this.api.get('/surveys/my-surveys');
    return response.data;
  }

  async getSurveyStatistics() {
    const response = await this.api.get('/surveys/statistics');
    return response.data;
  }

  // Task APIs
  async createTask(taskData: any) {
    const response = await this.api.post('/tasks/create', taskData);
    return response.data;
  }

  async getMyTasks() {
    const response = await this.api.get('/tasks/assigned-to-me');
    return response.data;
  }

  async updateTaskStatus(taskId: string, status: string, completionPercentage?: number) {
    const response = await this.api.put(`/tasks/${taskId}/update-status`, {
      status,
      completion_percentage: completionPercentage,
    });
    return response.data;
  }

  // Dashboard APIs
  async getDashboard(role: 'super-admin' | 'admin' | 'karyakarta') {
    const response = await this.api.get(`/dashboard/${role}`);
    return response.data;
  }

  async getBoothPerformance() {
    const response = await this.api.get('/dashboard/booth-performance');
    return response.data;
  }

  async getFavorScoreTrends() {
    const response = await this.api.get('/dashboard/favor-score-trends');
    return response.data;
  }

  // Analytics APIs
  async getBoothWiseAnalytics() {
    const response = await this.api.get('/analytics/booth-wise');
    return response.data;
  }

  async getCasteDistribution() {
    const response = await this.api.get('/analytics/caste-distribution');
    return response.data;
  }

  async getLiveTurnout() {
    const response = await this.api.get('/analytics/turnout-live');
    return response.data;
  }

  async getFavorScoreHeatmap() {
    const response = await this.api.get('/analytics/favor-score-heatmap');
    return response.data;
  }

  // Family APIs
  async getFamilies(params: any = {}) {
    const response = await this.api.get('/families', { params });
    return response.data;
  }

  async getFamily(familyId: string) {
    const response = await this.api.get(`/families/${familyId}`);
    return response.data;
  }

  async getFamilyMembers(familyId: string) {
    const response = await this.api.get(`/families/${familyId}/members`);
    return response.data;
  }

  // Influencer APIs
  async getInfluencers(params: any = {}) {
    const response = await this.api.get('/influencers', { params });
    return response.data;
  }

  async createInfluencer(influencerData: any) {
    const response = await this.api.post('/influencers', influencerData);
    return response.data;
  }

  // Issue APIs
  async getIssues(params: any = {}) {
    const response = await this.api.get('/issues', { params });
    return response.data;
  }

  async createIssue(issueData: any) {
    const response = await this.api.post('/issues', issueData);
    return response.data;
  }

  async resolveIssue(issueId: string) {
    const response = await this.api.put(`/issues/${issueId}/resolve`);
    return response.data;
  }
}

export default new ApiService();
