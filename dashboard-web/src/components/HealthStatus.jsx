import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Grid,
  Button,
  IconButton,
  Skeleton,
  Alert,
} from '@mui/material';
import { Refresh, CheckCircle, Error } from '@mui/icons-material';
import { checkAllServicesHealth } from '../services/api';
import ServiceStatusCard from './ServiceStatusCard';

export default function HealthStatus() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadHealthStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const healthData = await checkAllServicesHealth();
      setServices(healthData);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error checking health:', error);
      setError('Failed to check service health');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHealthStatus();

    // Auto-refresh every 30 seconds
    const interval = setInterval(loadHealthStatus, 30000);
    return () => clearInterval(interval);
  }, [loadHealthStatus]);

  const healthyCount = services.filter((s) => s.status === 'healthy').length;
  const totalCount = services.length;
  const allHealthy = healthyCount === totalCount;

  if (loading && services.length === 0) {
    return (
      <Box>
        <Skeleton variant="text" width={300} height={50} sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {[1, 2, 3, 4, 5].map((i) => (
            <Grid item xs={12} md={6} lg={4} key={i}>
              <Skeleton variant="rounded" height={180} sx={{ borderRadius: 4 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box className="fade-in">
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            System Health
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Microservices status monitoring
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={2}>
          {lastUpdated && (
            <Typography variant="caption" color="text.secondary">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </Typography>
          )}
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadHealthStatus}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Overall Status */}
      <Box
        sx={{
          mb: 4,
          p: 3,
          borderRadius: 3,
          background: allHealthy
            ? 'linear-gradient(135deg, rgba(39, 174, 96, 0.1) 0%, rgba(39, 174, 96, 0.05) 100%)'
            : 'linear-gradient(135deg, rgba(231, 76, 60, 0.1) 0%, rgba(231, 76, 60, 0.05) 100%)',
          border: `1px solid ${allHealthy ? 'rgba(39, 174, 96, 0.3)' : 'rgba(231, 76, 60, 0.3)'}`,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
        }}
      >
        {allHealthy ? (
          <CheckCircle sx={{ fontSize: 48, color: 'success.main' }} />
        ) : (
          <Error sx={{ fontSize: 48, color: 'error.main' }} />
        )}
        <Box>
          <Typography variant="h5" fontWeight={700}>
            {allHealthy ? 'All Systems Operational' : 'Some Services Need Attention'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {healthyCount} of {totalCount} services are healthy
          </Typography>
        </Box>
        <Box
          sx={{
            ml: 'auto',
            display: 'flex',
            alignItems: 'center',
            gap: 3,
          }}
        >
          <Box textAlign="center">
            <Typography variant="h4" fontWeight={700} color="success.main">
              {healthyCount}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Healthy
            </Typography>
          </Box>
          <Box textAlign="center">
            <Typography variant="h4" fontWeight={700} color="error.main">
              {totalCount - healthyCount}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Unhealthy
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Service Cards */}
      <Grid container spacing={3}>
        {services.map((service) => (
          <Grid item xs={12} md={6} lg={4} key={service.name}>
            <ServiceStatusCard service={service} loading={loading} />
          </Grid>
        ))}
      </Grid>

      {/* Service Architecture */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Service Architecture
        </Typography>
        <Box
          sx={{
            p: 3,
            borderRadius: 3,
            backgroundColor: 'grey.50',
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            overflowX: 'auto',
          }}
        >
          <pre style={{ margin: 0 }}>
            {`┌─────────────────────────────────────────────────────────────┐
│                    React Dashboard (3000)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway (8080)                        │
│              Spring Cloud Gateway + CORS                     │
└─────────────────────────────────────────────────────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ProxyFHIR │  │   DeID   │  │Featurizer│  │ML-Predict│
│  (8081)  │  │  (5000)  │  │  (5001)  │  │  (5002)  │
│  Java    │  │  Python  │  │  Python  │  │  Python  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
                   │              │              │
                   └──────────────┼──────────────┘
                                  ▼
                    ┌──────────────────────────┐
                    │    PostgreSQL (5433)      │
                    │      healthflow_fhir      │
                    └──────────────────────────┘`}
          </pre>
        </Box>
      </Box>
    </Box>
  );
}
