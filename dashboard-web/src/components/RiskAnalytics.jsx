import { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Grid,
    Card,
    CardContent,
    Button,
    IconButton,
    Skeleton,
    Alert,
} from '@mui/material';
import { Refresh, Warning, TrendingUp, People } from '@mui/icons-material';
import { getPredictionStats, getHighRiskPatients, getPredictions } from '../services/api';
import RiskDistributionChart from './RiskDistributionChart';
import StatsCard from './StatsCard';
import PatientCard from './PatientCard';

export default function RiskAnalytics() {
    const [stats, setStats] = useState(null);
    const [highRiskPatients, setHighRiskPatients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        setLoading(true);
        setError(null);
        try {
            const [statsData, highRisk] = await Promise.all([
                getPredictionStats(),
                getHighRiskPatients().catch(() => []),
            ]);
            setStats(statsData);
            setHighRiskPatients(highRisk || []);
        } catch (error) {
            console.error('Failed to load analytics:', error);
            setError('Failed to load risk analytics data');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Box>
                <Skeleton variant="text" width={300} height={50} sx={{ mb: 3 }} />
                <Grid container spacing={3}>
                    {[1, 2, 3, 4].map((i) => (
                        <Grid item xs={12} sm={6} md={3} key={i}>
                            <Skeleton variant="rounded" height={140} sx={{ borderRadius: 4 }} />
                        </Grid>
                    ))}
                    <Grid item xs={12} md={6}>
                        <Skeleton variant="rounded" height={350} sx={{ borderRadius: 4 }} />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Skeleton variant="rounded" height={350} sx={{ borderRadius: 4 }} />
                    </Grid>
                </Grid>
            </Box>
        );
    }

    const distribution = stats?.risk_distribution || {};
    const total = Object.values(distribution).reduce((a, b) => a + b, 0);
    const criticalCount = distribution.critical || 0;
    const highCount = distribution.high || 0;
    const moderateCount = distribution.moderate || 0;
    const lowCount = (distribution.low || 0) + (distribution.minimal || 0);

    return (
        <Box className="fade-in">
            {/* Header */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
                <Box>
                    <Typography variant="h4" fontWeight={700} gutterBottom>
                        Risk Analytics
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Patient readmission risk analysis and prediction insights
                    </Typography>
                </Box>
                <IconButton onClick={loadAnalytics} color="primary">
                    <Refresh />
                </IconButton>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Summary Stats */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatsCard
                        title="Total Predictions"
                        value={total}
                        icon={TrendingUp}
                        color="primary"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatsCard
                        title="Critical Risk"
                        value={criticalCount}
                        icon={Warning}
                        color="error"
                        subtitle={`${total > 0 ? ((criticalCount / total) * 100).toFixed(1) : 0}% of patients`}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatsCard
                        title="High Risk"
                        value={highCount}
                        icon={Warning}
                        color="warning"
                        subtitle={`${total > 0 ? ((highCount / total) * 100).toFixed(1) : 0}% of patients`}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatsCard
                        title="Low/Minimal Risk"
                        value={lowCount}
                        icon={People}
                        color="success"
                        subtitle={`${total > 0 ? ((lowCount / total) * 100).toFixed(1) : 0}% of patients`}
                    />
                </Grid>
            </Grid>

            {/* Charts */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} gutterBottom>
                                Risk Level Distribution (Pie)
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Visual breakdown of patient risk categories
                            </Typography>
                            <RiskDistributionChart data={distribution} variant="pie" />
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" fontWeight={600} gutterBottom>
                                Risk Level Distribution (Bar)
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Patient counts per risk category
                            </Typography>
                            <RiskDistributionChart data={distribution} variant="bar" />
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Model Performance */}
            <Card sx={{ mb: 4 }}>
                <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                        Model Performance Metrics
                    </Typography>
                    <Grid container spacing={3} sx={{ mt: 1 }}>
                        <Grid item xs={6} sm={3}>
                            <Box textAlign="center">
                                <Typography variant="h3" fontWeight={700} color="primary.main">
                                    88.3%
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    ROC-AUC Score
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                            <Box textAlign="center">
                                <Typography variant="h3" fontWeight={700} color="success.main">
                                    81.6%
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Test Accuracy
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                            <Box textAlign="center">
                                <Typography variant="h3" fontWeight={700} color="info.main">
                                    51
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Total Features
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                            <Box textAlign="center">
                                <Typography variant="h3" fontWeight={700} color="warning.main">
                                    14
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    NLP Features
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            {/* High Risk Patients */}
            {highRiskPatients.length > 0 && (
                <Box>
                    <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mb: 2 }}>
                        High-Risk Patients Requiring Attention
                    </Typography>
                    <Grid container spacing={3}>
                        {highRiskPatients.slice(0, 6).map((patient) => (
                            <Grid item xs={12} md={6} lg={4} key={patient.patient_id}>
                                <PatientCard patient={patient} />
                            </Grid>
                        ))}
                    </Grid>
                    {highRiskPatients.length > 6 && (
                        <Box textAlign="center" mt={3}>
                            <Typography variant="body2" color="text.secondary">
                                And {highRiskPatients.length - 6} more high-risk patients...
                            </Typography>
                        </Box>
                    )}
                </Box>
            )}
        </Box>
    );
}
