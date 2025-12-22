import { gatewayApi, getCached, setCache, clearCache } from './apiCore';

export { clearCache };

// Health checks for all services (direct checks for admin purposes)
// Health checks for all services (routed via Gateway)
export const checkAllServicesHealth = async () => {
  const services = [
    { name: 'ProxyFHIR', path: '/api/v1/fhir/health', port: 8081 },
    { name: 'DeID', path: '/api/v1/deid/health', port: 5000 },
    { name: 'Featurizer', path: '/api/v1/features/health', port: 5001 },
    { name: 'ML-Predictor', path: '/api/v1/predictions/health', port: 5002 },
    { name: 'ScoreAPI', path: '/api/v1/scores/health', port: 5003 },
    { name: 'AuditFairness', path: '/api/v1/audit/health', port: 5004 },
    { name: 'API Gateway', path: '/health', port: 8085 },
  ];

  const healthChecks = await Promise.allSettled(
    services.map(async (service) => {
      try {
        // Use gatewayApi to benefit from valid baseURL and config
        const response = await gatewayApi.get(service.path, {
            timeout: 5000 
        });
        return {
          name: service.name,
          status: 'healthy',
          details: response.data,
        };
      } catch (error) {
        return {
          name: service.name,
          status: 'unhealthy',
          error: error.code === 'ECONNREFUSED'
            ? 'Service not reachable via Gateway'
            : (error.response?.statusText || error.message),
        };
      }
    })
  );

  return healthChecks.map((result, index) => {
    const serviceInfo = services[index];
    if (result.status === 'fulfilled') {
      return { ...serviceInfo, ...result.value };
    } else {
      return {
        ...serviceInfo,
        status: 'error',
        error: result.reason?.message || 'Unknown error'
      };
    }
  });
};

// ============ Features API (via Gateway) ============
export const getFeatures = async () => {
  const cacheKey = 'features';
  const cached = getCached(cacheKey);
  if (cached) return cached;

  try {
    const response = await gatewayApi.get('/api/v1/features/features');
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
    const response = await gatewayApi.get('/api/v1/features/stats');
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get feature stats:', error);
    return { total_patients: 0 };
  }
};

export const extractFeatures = async () => {
  clearCache();
  const response = await gatewayApi.post('/api/v1/features/extract/all');
  return response.data;
};

// ============ Predictions API (via Gateway) ============
export const getPredictions = async () => {
  const cacheKey = 'predictions';
  const cached = getCached(cacheKey);
  if (cached) return cached;

  try {
    const response = await gatewayApi.get('/api/v1/predictions/predictions');
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
    const response = await gatewayApi.get('/api/v1/predictions/stats');
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
    const response = await gatewayApi.get('/api/v1/predictions/high-risk');
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get high risk patients:', error);
    return [];
  }
};

export const predictRisks = async () => {
  clearCache();
  const response = await gatewayApi.post('/api/v1/predictions/predict/all');
  return response.data;
};

// ============ Patient Details ============
export const getPatientFeatures = async (patientId) => {
  const response = await gatewayApi.get(`/api/v1/features/features/${patientId}`);
  return response.data;
};

export const getPatientPrediction = async (patientId) => {
  const response = await gatewayApi.get(`/api/v1/predictions/risk/${patientId}`);
  return response.data;
};

// ============ Patients API (Combined Features + Predictions) ============
export const getPatients = async () => {
  const cacheKey = 'patients';
  const cached = getCached(cacheKey);
  if (cached) return cached;

  try {
    const response = await gatewayApi.get('/api/v1/predictions/patients');
    const patients = response.data.patients || [];
    setCache(cacheKey, patients);
    return patients;
  } catch (error) {
    console.error('Failed to get patients:', error);
    return [];
  }
};

// ============ FHIR Sync (via Gateway) ============
export const getLocalPatientCount = async () => {
    try {
        const response = await gatewayApi.get('/api/v1/fhir/count');
        return response.data;
    } catch (error) {
        console.error('Failed to get patient count:', error);
        return { count: 0 };
    }
};

export const syncFhirData = async (count = 100) => {
  clearCache();
  const response = await gatewayApi.post(`/api/v1/fhir/sync/bulk?count=${count}`, {}, {
    timeout: 600000, // 10 minutes for bulk sync
  });
  return response.data;
};

export const generatePatients = async (count = 10) => {
    clearCache();
    const response = await gatewayApi.post(`/api/v1/fhir/generate?count=${count}`, {}, {
        timeout: 600000 // 10 minutes
    });
    return response.data;
};

// ============ Anonymization (via Gateway) ============
export const anonymizeData = async () => {
  clearCache();
  const response = await gatewayApi.post('/api/v1/deid/anonymize/all');
  return response.data;
};

// ============ Audit Fairness API (via Gateway) ============
export const getAuditMetrics = async () => {
  const cacheKey = 'auditMetrics';
  const cached = getCached(cacheKey);
  if (cached) return cached;

  try {
    const response = await gatewayApi.get('/api/v1/audit/metrics');
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to get audit metrics:', error);
    throw error; // Let component handle fallback
  }
};

export const generateFairnessReport = async () => {
  const response = await gatewayApi.post('/api/v1/audit/report');
  return response.data;
};

export default gatewayApi;
