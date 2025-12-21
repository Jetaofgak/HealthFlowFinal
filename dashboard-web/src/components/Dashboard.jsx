import { useEffect, useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  Skeleton,
} from '@mui/material';
import {
  People,
  Assessment,
  Warning,
  TrendingUp,
  Refresh,
  Psychology,
  Favorite,
} from '@mui/icons-material';
import { getFeatureStats, getPredictionStats, extractFeatures, predictRisks } from '../services/api';
import StatsCard from './StatsCard';
import RiskDistributionChart, { RiskBar } from './RiskDistributionChart';

function Dashboard() {
  const [featureStats, setFeatureStats] = useState(null);
  const [predictionStats, setPredictionStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [features, predictions] = await Promise.all([
        getFeatureStats(),
        getPredictionStats(),
      ]);
      setFeatureStats(features);
      setPredictionStats(predictions);
    } catch (error) {
      console.error('Error loading data:', error);
      setError('Failed to load dashboard data. Please check if services are running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleExtractFeatures = async () => {
    setProcessing(true);
    try {
      await extractFeatures();
      await loadData();
    } catch (error) {
      setError('Error extracting features');
    } finally {
      setProcessing(false);
    }
  };

  const handlePredictRisks = async () => {
    setProcessing(true);
    try {
      await predictRisks();
      await loadData();
    } catch (error) {
      setError('Error predicting risks');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <Box>
        <Skeleton variant="text" width={300} height={60} sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rounded" height={140} sx={{ borderRadius: 4 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  const highRiskCount = predictionStats?.risk_distribution?.high || 0;
  const criticalCount = predictionStats?.risk_distribution?.critical || 0;
  const totalPredictions = predictionStats?.total_predictions || 0;

  return (
    <Box className="fade-in">
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Healthcare Analytics Overview
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadData}
            disabled={processing}
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

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Total Patients"
            value={featureStats?.total_patients || 0}
            icon={People}
            color="primary"
            subtitle="In database"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Average Age"
            value={featureStats?.average_age ? `${featureStats.average_age.toFixed(1)} yrs` : 'N/A'}
            icon={Favorite}
            color="info"
            subtitle="Patient cohort"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="High Risk"
            value={highRiskCount + criticalCount}
            icon={Warning}
            color="error"
            subtitle="Need attention"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Predictions"
            value={totalPredictions}
            icon={Assessment}
            color="success"
            subtitle="Generated"
          />
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Button
            variant="contained"
            fullWidth
            size="large"
            startIcon={processing ? <CircularProgress size={20} color="inherit" /> : <Psychology />}
            onClick={handleExtractFeatures}
            disabled={processing}
            sx={{ py: 1.5 }}
          >
            Extract Features (BioBERT + Structured)
          </Button>
        </Grid>
        <Grid item xs={12} md={6}>
          <Button
            variant="contained"
            color="secondary"
            fullWidth
            size="large"
            startIcon={processing ? <CircularProgress size={20} color="inherit" /> : <TrendingUp />}
            onClick={handlePredictRisks}
            disabled={processing}
            sx={{ py: 1.5 }}
          >
            Predict Risks (XGBoost)
          </Button>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Risk Distribution
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Patient risk level breakdown
              </Typography>
              <RiskDistributionChart data={predictionStats?.risk_distribution || {}} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Prediction Statistics
              </Typography>

              <Box sx={{ mt: 3 }}>
                <Box sx={{ mb: 3 }}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2" color="text.secondary">
                      Total Predictions
                    </Typography>
                    <Typography variant="h5" fontWeight={700} color="primary.main">
                      {predictionStats?.total_predictions || 0}
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2" color="text.secondary">
                      Average Risk Score
                    </Typography>
                    <Typography variant="h5" fontWeight={700}>
                      {predictionStats?.average_framingham_score
                        ? `${(predictionStats.average_framingham_score * 100).toFixed(1)}%`
                        : 'N/A'}
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Risk Level Distribution
                  </Typography>
                  <RiskBar distribution={predictionStats?.risk_distribution || {}} />
                </Box>

                <Box
                  sx={{
                    mt: 3,
                    p: 2,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, rgba(0, 102, 204, 0.08) 0%, rgba(0, 168, 107, 0.08) 100%)',
                    border: '1px solid rgba(0, 102, 204, 0.2)',
                  }}
                >
                  <Typography variant="subtitle2" color="primary.main" fontWeight={600}>
                    Model Info
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    XGBoost with 51 features (37 structured + 14 NLP from BioBERT)
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Test AUC: 88.27%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Stats Bar */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" fontWeight={700} color="primary.main">
                  {featureStats?.average_bmi?.toFixed(1) || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Average BMI
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" fontWeight={700} color="warning.main">
                  {featureStats?.average_cholesterol?.toFixed(0) || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Cholesterol (mg/dL)
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" fontWeight={700} color="success.main">
                  {predictionStats?.risk_distribution?.low || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Low Risk Patients
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" fontWeight={700} color="error.main">
                  {(highRiskCount + criticalCount)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  High/Critical Risk
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Dashboard;
