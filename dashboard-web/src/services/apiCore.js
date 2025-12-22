import axios from 'axios';

// All requests go through API Gateway
export const GATEWAY_URL = 'http://localhost:8085';

const createApi = (baseURL) => {
  const instance = axios.create({
    baseURL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000,
  });
  return instance;
};

// Gateway API instance
export const gatewayApi = createApi(GATEWAY_URL);

// Simple cache implementation
const cache = new Map();
const CACHE_TTL = 60000; // 1 minute

export const getCached = (key) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  cache.delete(key);
  return null;
};

export const setCache = (key, data) => {
  cache.set(key, { data, timestamp: Date.now() });
};

export const clearCache = () => {
  cache.clear();
};
