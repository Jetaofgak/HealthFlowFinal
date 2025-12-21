import { useEffect, useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  CircularProgress,
} from '@mui/material';
import { CheckCircle, Error, Warning } from '@mui/icons-material';
import { checkAllServicesHealth } from '../services/api';

function HealthStatus() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHealthStatus();
    const interval = setInterval(loadHealthStatus, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadHealthStatus = async () => {
    try {
      const results = await checkAllServicesHealth();
      setServices(results);
    } catch (error) {
      console.error('Failed to load health status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const ServiceCard = ({ service }) => {
    const isHealthy = service.status === 'healthy';
    const statusColor = isHealthy ? 'success' : 'error';
    const StatusIcon = isHealthy ? CheckCircle : Error;

    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">{service.name}</Typography>
            <Chip
              icon={<StatusIcon />}
              label={service.status.toUpperCase()}
              color={statusColor}
            />
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Port: {service.port}
          </Typography>
          {service.details && (
            <Box sx={{ mt: 2, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="caption" component="pre" sx={{ fontSize: '0.75rem' }}>
                {JSON.stringify(service.details, null, 2)}
              </Typography>
            </Box>
          )}
          {service.error && (
            <Typography variant="body2" color="error" sx={{ mt: 1 }}>
              Error: {service.error}
            </Typography>
          )}
        </CardContent>
      </Card>
    );
  };

  const healthyCount = services.filter(s => s.status === 'healthy').length;
  const totalCount = services.length;

  return (
    <div>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Microservices Health Status
        </Typography>
        <Chip
          icon={healthyCount === totalCount ? <CheckCircle /> : <Warning />}
          label={`${healthyCount}/${totalCount} Services Healthy`}
          color={healthyCount === totalCount ? 'success' : 'warning'}
          size="large"
        />
      </Box>

      <Grid container spacing={3}>
        {services.map((service) => (
          <Grid item xs={12} md={6} lg={4} key={service.name}>
            <ServiceCard service={service} />
          </Grid>
        ))}
      </Grid>
    </div>
  );
}

export default HealthStatus;
