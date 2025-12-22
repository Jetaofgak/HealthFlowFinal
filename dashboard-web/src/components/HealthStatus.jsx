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
            p: 4,
            borderRadius: 3,
            backgroundColor: 'grey.50',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
          }}
        >
          {/* Dashboard Node */}
          <Box
            sx={{
              p: 2,
              border: '1px solid',
              borderColor: 'primary.main',
              borderRadius: 2,
              backgroundColor: 'white',
              width: '280px',
              textAlign: 'center',
              boxShadow: 1,
            }}
          >
            <Typography variant="subtitle1" fontWeight={700} color="primary.main">
              React Dashboard
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Port: 3002
            </Typography>
          </Box>

          {/* Arrow */}
          <Typography variant="h4" color="text.secondary" sx={{ lineHeight: 0.5 }}>
            ⬇
          </Typography>

          {/* API Gateway Node */}
          <Box
            sx={{
              p: 2,
              border: '1px solid',
              borderColor: 'warning.main',
              borderRadius: 2,
              backgroundColor: 'white',
              width: '320px',
              textAlign: 'center',
              boxShadow: 1,
            }}
          >
            <Typography variant="subtitle1" fontWeight={700} color="warning.main">
              API Gateway
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Port: 8085
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Spring Cloud Gateway + CORS
            </Typography>
          </Box>

          {/* Arrow */}
           <Typography variant="h4" color="text.secondary" sx={{ lineHeight: 0.5 }}>
            ⬇
          </Typography>

          {/* Microservices Layer */}
          <Grid container spacing={2} justifyContent="center" sx={{ mt: 2 }}>
            {[
              { name: 'ProxyFHIR', port: 8081, lang: 'Java' },
              { name: 'DeID', port: 5000, lang: 'Python' },
              { name: 'Featurizer', port: 5001, lang: 'Python' },
              { name: 'ML-Predictor', port: 5002, lang: 'Python' },
              { name: 'ScoreAPI', port: 5003, lang: 'Python' },
            ].map((svc) => (
              <Grid item key={svc.name}>
                <Box
                  sx={{
                    p: 1.5,
                    border: '1px solid',
                    borderColor: 'grey.300',
                    borderRadius: 2,
                    backgroundColor: 'white',
                    width: '140px',
                    textAlign: 'center',
                    boxShadow: 1,
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: 3,
                    }
                  }}
                >
                  <Typography variant="subtitle2" fontWeight={700}>
                    {svc.name}
                  </Typography>
                  <Typography variant="caption" display="block" color="text.secondary">
                    Port: {svc.port}
                  </Typography>
                  <Typography variant="caption" color="text.disabled" sx={{ fontSize: '0.7rem' }}>
                    {svc.lang}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
          
           {/* Arrow to DB */}
           <Typography variant="h4" color="text.secondary" sx={{ lineHeight: 0.5, mt: 1 }}>
            ⬇
          </Typography>

          {/* Database Node */}
          <Box
            sx={{
              p: 1.5,
              border: '1px solid',
              borderColor: 'grey.400',
              borderRadius: 2,
              backgroundColor: 'grey.100',
              width: '200px',
              textAlign: 'center',
              boxShadow: 1,
            }}
          >
             <Typography variant="subtitle2" fontWeight={700} color="text.primary">
              PostgreSQL
            </Typography>
             <Typography variant="caption" display="block" color="text.secondary">
              Port: 5433
            </Typography>
             <Typography variant="caption" color="text.secondary">
              healthflow_fhir
            </Typography>
          </Box>

        </Box>
      </Box>
    </Box>
  );
}
