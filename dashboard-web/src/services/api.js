import axios from 'axios';

// Direct service URLs - bypassing API gateway to avoid CORS issues
const FEATURES_URL = 'http://localhost:5001';
const PREDICTIONS_URL = 'http://localhost:5002';
const DEID_URL = 'http://localhost:5000';
const FHIR_URL = 'http://localhost:8081';
const GATEWAY_URL = 'http://localhost:8085';

const createApi = (baseURL) => {
  const instance = axios.create({
    baseURL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000,
  });
  return instance;
};

// Direct service connections (bypassing gateway for CORS-free access)
const featuresApi = createApi(FEATURES_URL);
const predictionsApi = createApi(PREDICTIONS_URL);
const deidApi = createApi(DEID_URL);
const fhirApi = createApi(FHIR_URL);

// Simple cache implementation
const cache = new Map();
const CACHE_TTL = 60000; // 1 minute

const getCached = (key) => {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  cache.delete(key);
  return null;
};

const setCache = (key, data) => {
  cache.set(key, { data, timestamp: Date.now() });
};

export const clearCache = () => {
  cache.clear();
};

// Health checks for all services
export const checkAllServicesHealth = async () => {
  const services = [
    { name: 'DeID', port: 5000, path: '/health' },
    { name: 'Featurizer', port: 5001, path: '/health' },
    { name: 'ML-Predictor', port: 5002, path: '/health' },
    { name: 'ScoreAPI', port: 5003, path: '/health' },
    { name: 'API Gateway', port: 8085, path: '/health' },
  ];

  const healthChecks = await Promise.allSettled(
    services.map(async (service) => {
      try {
        const response = await axios.get(`http://localhost:${service.port}${service.path}`, {
          timeout: 5000,
        });
        return {
          name: service.name,
          port: service.port,
          status: 'healthy',
          details: response.data,
        };
      } catch (error) {
        return {
          name: service.name,
          port: service.port,
          status: 'unhealthy',
          error: error.code === 'ECONNREFUSED'
            ? 'Service not running'
            : error.message,
        };
      }
    })
  );

  return healthChecks.map((result, index) => ({
    ...services[index],
    ...(result.status === 'fulfilled' ? result.value : {
      status: 'error',
      error: result.reason?.message || 'Unknown error'
    }),
  }));
};

// Features API - call featurizer service directly
export const getFeatures = async () => {
  const cacheKey = 'features';
  const cached = getCached(cacheKey);
  if (cached) return cached;

  try {
    const response = await featuresApi.get('/api/v1/features');
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get features:', error);
    return [];
  }
};

export const getFeatureStats = async () => {
  const cacheKey = 'featureStats';
  const cached = getCached(cacheKey);
  if (cached) return cached;

  try {
    const response = await featuresApi.get('/api/v1/stats');
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get feature stats:', error);
    return { total_patients: 0 };
  }
};

export const extractFeatures = async () => {
  clearCache();
  const response = await featuresApi.post('/api/v1/extract/all');
  return response.data;
};

// Predictions API - call ml-predictor service directly
export const getPredictions = async () => {
  const cacheKey = 'predictions';
  const cached = getCached(cacheKey);
  if (cached) return cached;

  try {
    const response = await predictionsApi.get('/api/v1/predictions');
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get predictions:', error);
    return [];
  }
};

export const getPredictionStats = async () => {
  const cacheKey = 'predictionStats';
  const cached = getCached(cacheKey);
  if (cached) return cached;

  try {
    const response = await predictionsApi.get('/api/v1/stats');
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get prediction stats:', error);
    return { total_predictions: 0, risk_distribution: {} };
  }
};

export const getHighRiskPatients = async () => {
  const cacheKey = 'highRiskPatients';
  const cached = getCached(cacheKey);
  if (cached) return cached;

  try {
    const response = await predictionsApi.get('/api/v1/high-risk');
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get high risk patients:', error);
    return [];
  }
};

export const predictRisks = async () => {
  clearCache();
  const response = await predictionsApi.post('/api/v1/predict/all');
  return response.data;
};

// Get patient details
export const getPatientFeatures = async (patientId) => {
  const response = await featuresApi.get(`/api/v1/features/${patientId}`);
  return response.data;
};

export const getPatientPrediction = async (patientId) => {
  const response = await predictionsApi.get(`/api/v1/risk/${patientId}`);
  return response.data;
};

// FHIR sync
export const syncFhirData = async (count = 100) => {
  clearCache();
  const response = await fhirApi.post(`/api/v1/sync/bulk?count=${count}`, {}, {
    timeout: 600000, // 10 minutes for bulk sync
  });
  return response.data;
};

// Anonymization
export const anonymizeData = async () => {
  clearCache();
  const response = await deidApi.post('/api/v1/anonymize/all');
  return response.data;
};

export default featuresApi;
