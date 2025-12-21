import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health checks for all services
export const checkAllServicesHealth = async () => {
  const services = [
    { name: 'DeID', port: 5000, path: '/health' },
    { name: 'Featurizer', port: 5001, path: '/health' },
    { name: 'ML-Predictor', port: 5002, path: '/health' },
    { name: 'ScoreAPI', port: 5003, path: '/health' },
    { name: 'API Gateway', port: 8080, path: '/health' },
  ];

  const healthChecks = await Promise.allSettled(
    services.map(async (service) => {
      try {
        const response = await axios.get(`http://localhost:${service.port}${service.path}`);
        return {
          name: service.name,
          status: 'healthy',
          details: response.data,
        };
      } catch (error) {
        return {
          name: service.name,
          status: 'unhealthy',
          error: error.message,
        };
      }
    })
  );

  return healthChecks.map((result, index) => ({
    ...services[index],
    ...(result.status === 'fulfilled' ? result.value : { status: 'error', error: result.reason }),
  }));
};


// Features API
export const getFeatures = async () => {
  const response = await api.get('/features/features');
  return response.data;
};

export const getFeatureStats = async () => {
  const response = await api.get('/features/stats');
  return response.data;
};

export const extractFeatures = async () => {
  const response = await api.post('/features/extract/all');
  return response.data;
};

// Predictions API
export const getPredictions = async () => {
  const response = await api.get('/predictions/predictions');
  return response.data;
};

export const getPredictionStats = async () => {
  const response = await api.get('/predictions/stats');
  return response.data;
};

export const getHighRiskPatients = async () => {
  const response = await api.get('/predictions/high-risk');
  return response.data;
};

export const predictRisks = async () => {
  const response = await api.post('/predictions/predict/all');
  return response.data;
};

// Get patient details
export const getPatientFeatures = async (patientId) => {
  const response = await api.get(`/features/features/${patientId}`);
  return response.data;
};

export const getPatientPrediction = async (patientId) => {
  const response = await api.get(`/predictions/risk/${patientId}`);
  return response.data;
};

export default api;
