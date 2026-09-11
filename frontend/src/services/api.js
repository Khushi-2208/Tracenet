/**
 * TRACENET API Service
 * Centralized Axios client for all FastAPI backend communication.
 */
import axios from 'axios';

const rawBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE = rawBase.endsWith('/api') ? rawBase : `${rawBase.replace(/\/$/, '')}/api`;

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 min timeout for AI processing
});

// ===================== Upload & Processing =====================

export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/upload-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function loadSampleData() {
  const res = await api.post('/load-sample');
  return res.data;
}

export async function getDatasetStats() {
  const res = await api.get('/dataset/stats');
  return res.data;
}

export async function resetState() {
  const res = await api.post('/reset');
  return res.data;
}

// ===================== Search & Profiles =====================

export async function searchEntities(query, type = null) {
  const params = { q: query };
  if (type) params.type = type;
  const res = await api.get('/search', { params });
  return res.data;
}

export async function listActors() {
  const res = await api.get('/actors');
  return res.data;
}

export async function getActorProfile(username) {
  const res = await api.get(`/actors/${encodeURIComponent(username)}`);
  return res.data;
}

export async function getActorGraph(username) {
  const res = await api.get(`/actors/${encodeURIComponent(username)}/graph`);
  return res.data;
}

export async function getActorTimeline(username) {
  const res = await api.get(`/actors/${encodeURIComponent(username)}/timeline`);
  return res.data;
}

// ===================== Analysis & Evidence =====================

export async function getPersonaLinks(minConfidence = null, limit = null) {
  const params = {};
  if (minConfidence) params.min_confidence = minConfidence;
  if (limit) params.limit = limit;
  const res = await api.get('/persona-links', { params });
  return res.data;
}

export async function getEvidenceBreakdown(usernameA, usernameB) {
  const res = await api.get(`/evidence/${encodeURIComponent(usernameA)}/${encodeURIComponent(usernameB)}`);
  return res.data;
}

export async function verifyLink(usernameA, usernameB) {
  const res = await api.post('/investigation/verify', { username_a: usernameA, username_b: usernameB });
  return res.data;
}

export async function rejectLink(usernameA, usernameB) {
  const res = await api.post('/investigation/reject', { username_a: usernameA, username_b: usernameB });
  return res.data;
}

export async function addNote(usernameA, usernameB, notes) {
  const res = await api.post('/investigation/note', { username_a: usernameA, username_b: usernameB, notes });
  return res.data;
}

// ===================== Export =====================

export function getExportCSVUrl() {
  return `${API_BASE}/export/csv`;
}

export function getExportPDFUrl(usernameA = null, usernameB = null) {
  let url = `${API_BASE}/export/pdf`;
  if (usernameA && usernameB) {
    url += `?username_a=${encodeURIComponent(usernameA)}&username_b=${encodeURIComponent(usernameB)}`;
  }
  return url;
}

export function getExportJSONUrl() {
  return `${API_BASE}/export/json`;
}

export async function getFullGraph() {
  const res = await api.get('/export/graph');
  return res.data;
}

export async function getFullTimeline() {
  const res = await api.get('/timeline');
  return res.data;
}

export async function healthCheck() {
  const res = await api.get('/health');
  return res.data;
}

export default api;
