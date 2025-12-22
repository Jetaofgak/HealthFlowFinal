import { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Card,
    CardContent,
    Button,
    Chip,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    LinearProgress,
    Skeleton,
    Alert as MuiAlert,
    Grid,
} from '@mui/material';
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
} from 'recharts';
import { Gavel, CheckCircle, Warning, Info, Refresh, TrendingUp, TrendingDown } from '@mui/icons-material';
import { getAuditMetrics, generateFairnessReport } from '../services/api';

export default function AuditFairness() {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        loadMetrics();
    }, []);

    const loadMetrics = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getAuditMetrics();
            setMetrics(data);
        } catch (err) {
            console.error('Failed to load audit metrics:', err);
            setError('AuditFairness service unavailable. Please ensure the service is running on port 5004.');
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateReport = async () => {
        setGenerating(true);
        try {
            await generateFairnessReport();
            await loadMetrics();
        } catch (err) {
            setError('Failed to generate report');
        } finally {
            setGenerating(false);
        }
    };

    // Fallback data if service unavailable
    const overallFairnessScore = metrics?.overall_score ?? 0;
    const demographicData = metrics?.demographic_analysis ?? [];
    const ageGroupData = metrics?.age_group_analysis ?? [];
    const biasMetrics = metrics?.bias_metrics ?? [];
    const radarData = metrics?.model_dimensions ?? [];
    const recommendations = metrics?.recommendations ?? [];

    if (loading) {
        return (
            <Box>
                <Skeleton variant="text" width={300} height={50} sx={{ mb: 3 }} />
                <Grid container spacing={3}>
                    {[1, 2, 3].map((i) => (
                        <Grid item xs={12} md={4} key={i}>
                            <Skeleton variant="rounded" height={180} sx={{ borderRadius: 4 }} />
                        </Grid>
                    ))}
                </Grid>
            </Box>
        );
    }

    const getFairnessColor = (score) => {
        if (score >= 90) return '#10b981';
        if (score >= 70) return '#f59e0b';
        return '#ef4444';
    };

    const getFairnessStatus = (score) => {
        if (score >= 90) return 'Excellent';
        if (score >= 70) return 'Good';
        if (score >= 50) return 'Review Recommended';
        return 'Action Required';
    };

    return (
        <Box className="fade-in" sx={{ 
            background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
            minHeight: '100vh',
            p: 4
        }}>
            {/* Header */}
            <Box mb={5} display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                    <Box display="flex" alignItems="center" gap={2} mb={1}>
                        <Gavel sx={{ fontSize: 40, color: '#0f172a' }} />
                        <Typography 
                            variant="h3" 
                            fontWeight={800}
                            sx={{
                                background: 'linear-gradient(135deg, #0f172a 0%, #334155 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                letterSpacing: '-0.02em'
                            }}
                        >
                            AI Fairness Audit
                        </Typography>
                    </Box>
                    <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
                        Algorithmic bias detection powered by EvidentlyAI
                    </Typography>
                </Box>
                <Box display="flex" gap={2}>
                    <Button 
                        variant="outlined" 
                        startIcon={<Refresh />} 
                        onClick={loadMetrics} 
                        disabled={loading}
                        sx={{
                            borderColor: '#334155',
                            color: '#334155',
                            fontWeight: 600,
                            '&:hover': {
                                borderColor: '#0f172a',
                                background: 'rgba(15, 23, 42, 0.05)'
                            }
                        }}
                    >
                        Refresh
                    </Button>
                    <Button 
                        variant="contained" 
                        startIcon={<Gavel />} 
                        onClick={handleGenerateReport}
                        disabled={generating || !!error}
                        sx={{
                            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
                            fontWeight: 600,
                            boxShadow: '0 4px 12px rgba(15, 23, 42, 0.3)',
                            '&:hover': {
                                background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
                                boxShadow: '0 6px 16px rgba(15, 23, 42, 0.4)'
                            }
                        }}
                    >
                        {generating ? 'Generating...' : 'Generate Report'}
                    </Button>
                </Box>
            </Box>

            {error && (
                <MuiAlert severity="error" sx={{ mb: 3, borderRadius: 2 }} onClose={() => setError(null)}>
                    {error}
                </MuiAlert>
            )}

            {!error && metrics && (
                <>
                    {/* Fairness Score Hero */}
                    <Card sx={{ 
                        mb: 4, 
                        borderRadius: 3,
                        background: `linear-gradient(135deg, ${getFairnessColor(overallFairnessScore)}15 0%, ${getFairnessColor(overallFairnessScore)}05 100%)`,
                        border: `2px solid ${getFairnessColor(overallFairnessScore)}40`,
                        boxShadow: `0 8px 24px ${getFairnessColor(overallFairnessScore)}20`
                    }}>
                        <CardContent sx={{ p: 4 }}>
                            <Grid container spacing={4} alignItems="center">
                                <Grid item xs={12} md={4}>
                                    <Box textAlign="center">
                                        <Typography variant="subtitle2" sx={{ opacity: 0.7, fontWeight: 600, mb: 2 }}>
                                            Overall Fairness Score
                                        </Typography>
                                        <Typography 
                                            variant="h1" 
                                            fontWeight={900}
                                            sx={{ 
                                                fontSize: '5rem',
                                                color: getFairnessColor(overallFairnessScore),
                                                textShadow: `0 2px 8px ${getFairnessColor(overallFairnessScore)}40`
                                            }}
                                        >
                                            {overallFairnessScore}
                                        </Typography>
                                        <Chip 
                                            label={getFairnessStatus(overallFairnessScore)}
                                            sx={{ 
                                                mt: 2,
                                                fontWeight: 700,
                                                fontSize: '0.9rem',
                                                background: getFairnessColor(overallFairnessScore),
                                                color: 'white',
                                                px: 2
                                            }}
                                        />
                                    </Box>
                                </Grid>
                                <Grid item xs={12} md={8}>
                                    <Typography variant="h6" fontWeight={700} mb={2}>
                                        Key Fairness Metrics
                                    </Typography>
                                    {biasMetrics.length > 0 ? (
                                        <TableContainer>
                                            <Table size="small">
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell sx={{ fontWeight: 700 }}>Metric</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 700 }}>Value</TableCell>
                                                        <TableCell align="right" sx={{ fontWeight: 700 }}>Threshold</TableCell>
                                                        <TableCell align="center" sx={{ fontWeight: 700 }}>Status</TableCell>
                                                    </TableRow>
                                                </TableHead>
                                                <TableBody>
                                                    {biasMetrics.map((row) => (
                                                        <TableRow key={row.metric}>
                                                            <TableCell sx={{ fontWeight: 600 }}>{row.metric}</TableCell>
                                                            <TableCell align="right" sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                                                                {row.value}
                                                            </TableCell>
                                                            <TableCell align="right" sx={{ fontFamily: 'monospace' }}>
                                                                {row.threshold}
                                                            </TableCell>
                                                            <TableCell align="center">
                                                                <Chip 
                                                                    label={row.status.toUpperCase()} 
                                                                    color={row.status === 'pass' ? 'success' : row.status === 'warning' ? 'warning' : 'error'} 
                                                                    size="small" 
                                                                    sx={{ fontWeight: 700, minWidth: 80 }}
                                                                />
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </TableContainer>
                                    ) : (
                                        <Typography color="text.secondary">No metrics available</Typography>
                                    )}
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>

                    {/* Charts Section */}
                    <Grid container spacing={3} sx={{ mb: 4 }}>
                        <Grid item xs={12} sm={12} md={6} lg={6} xl={6}>
                            <Paper sx={{ 
                                p: { xs: 2, md: 3 }, 
                                borderRadius: 3, 
                                height: { xs: 350, sm: 400, md: 420, lg: 480 },
                                background: 'white',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                                border: '1px solid #e2e8f0'
                            }}>
                                <Box display="flex" alignItems="center" gap={1} mb={3}>
                                    <TrendingUp sx={{ color: '#0f172a' }} />
                                    <Typography variant="h6" fontWeight={700}>
                                        Demographic Analysis
                                    </Typography>
                                </Box>
                                <Typography variant="caption" color="text.secondary" display="block" mb={2}>
                                    High-risk prediction rates by gender
                                </Typography>
                                {demographicData.length > 0 ? (
                                    <ResponsiveContainer width="100%" height="85%">
                                        <BarChart data={demographicData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                            <XAxis dataKey="group" stroke="#64748b" fontWeight={600} />
                                            <YAxis stroke="#64748b" />
                                            <Tooltip 
                                                contentStyle={{ 
                                                    borderRadius: 8, 
                                                    border: '1px solid #e2e8f0',
                                                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                                                }}
                                            />
                                            <Legend />
                                            <Bar dataKey="highRiskRate" name="High Risk Rate (%)" fill="#0f172a" radius={[8, 8, 0, 0]} />
                                            <Bar dataKey="sampleSize" name="Sample Size" fill="#64748b" radius={[8, 8, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <Box display="flex" alignItems="center" justifyContent="center" height="80%">
                                        <Typography color="text.secondary">No demographic data available</Typography>
                                    </Box>
                                )}
                            </Paper>
                        </Grid>
                        <Grid item xs={12} sm={12} md={6} lg={12} xl={6}>
                            <Paper sx={{ 
                                p: { xs: 2, md: 3 }, 
                                borderRadius: 3, 
                                height: { xs: 350, sm: 400, md: 420, lg: 480 },
                                background: 'white',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                                border: '1px solid #e2e8f0'
                            }}>
                                <Box display="flex" alignItems="center" gap={1} mb={3}>
                                    <TrendingDown sx={{ color: '#0f172a' }} />
                                    <Typography variant="h6" fontWeight={700}>
                                        Age Group Disparity
                                    </Typography>
                                </Box>
                                <Typography variant="caption" color="text.secondary" display="block" mb={2}>
                                    Risk distribution across age demographics
                                </Typography>
                                {ageGroupData.length > 0 ? (
                                    <ResponsiveContainer width="100%" height="85%">
                                        <BarChart data={ageGroupData} layout="vertical" margin={{ top: 20, right: 30, left: 60, bottom: 5 }}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                            <XAxis type="number" stroke="#64748b" />
                                            <YAxis dataKey="group" type="category" stroke="#64748b" fontWeight={600} />
                                            <Tooltip 
                                                contentStyle={{ 
                                                    borderRadius: 8, 
                                                    border: '1px solid #e2e8f0',
                                                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                                                }}
                                            />
                                            <Legend />
                                            <Bar dataKey="highRiskRate" name="High Risk Rate (%)" fill="#0f172a" radius={[0, 8, 8, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <Box display="flex" alignItems="center" justifyContent="center" height="80%">
                                        <Typography color="text.secondary">No age group data available</Typography>
                                    </Box>
                                )}
                            </Paper>
                        </Grid>
                    </Grid>

                    {/* Detailed Analysis */}
                    <Grid container spacing={3}>
                        <Grid item xs={12} sm={12} md={6} lg={12} xl={6}>
                            <Paper sx={{ 
                                p: { xs: 2, md: 3 }, 
                                borderRadius: 3, 
                                height: { xs: 400, sm: 450, md: 480, lg: 520 },
                                background: 'white',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                                border: '1px solid #e2e8f0'
                            }}>
                                <Typography variant="h6" fontWeight={700} mb={3}>
                                    Model Evaluation Dimensions
                                </Typography>
                                {radarData.length > 0 ? (
                                    <ResponsiveContainer width="100%" height="90%">
                                        <RadarChart outerRadius={100} data={radarData}>
                                            <PolarGrid stroke="#e2e8f0" />
                                            <PolarAngleAxis dataKey="subject" stroke="#64748b" fontWeight={600} />
                                            <PolarRadiusAxis angle={30} domain={[0, 150]} stroke="#64748b" />
                                            <Radar name="Current Model" dataKey="B" stroke="#0f172a" fill="#0f172a" fillOpacity={0.6} />
                                            <Radar name="Baseline" dataKey="A" stroke="#64748b" fill="#64748b" fillOpacity={0.3} />
                                            <Legend />
                                        </RadarChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <Box display="flex" alignItems="center" justifyContent="center" height="80%">
                                        <Typography color="text.secondary">No evaluation data available</Typography>
                                    </Box>
                                )}
                            </Paper>
                        </Grid>
                        <Grid item xs={12} sm={12} md={6} lg={12} xl={6}>
                            <Paper sx={{ 
                                p: { xs: 2, md: 3 }, 
                                borderRadius: 3, 
                                minHeight: { xs: 250, sm: 300 },
                                display: 'flex', 
                                flexDirection: 'column',
                                background: 'white',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                                border: '1px solid #e2e8f0'
                            }}>
                                <Typography variant="h6" fontWeight={700} mb={3} sx={{ fontSize: { xs: '1rem', md: '1.25rem' } }}>
                                    Fairness Recommendations
                                </Typography>
                                
                                <Box sx={{ flex: 1, overflowY: 'auto', mb: 2 }}>
                                    {recommendations.length > 0 ? (
                                        <Box display="flex" flexDirection="column" gap={2}>
                                            {recommendations.map((rec, idx) => (
                                                <Box
                                                    key={idx}
                                                    sx={{
                                                        p: 2.5,
                                                        borderRadius: 2,
                                                        border: '2px solid',
                                                        borderColor: rec.severity === 'warning' ? '#f59e0b' : rec.severity === 'info' ? '#3b82f6' : '#10b981',
                                                        background: rec.severity === 'warning' ? '#fef3c7' : rec.severity === 'info' ? '#dbeafe' : '#d1fae5',
                                                        display: 'flex',
                                                        gap: 2,
                                                        alignItems: 'flex-start'
                                                    }}
                                                >
                                                    {rec.severity === 'warning' ? (
                                                        <Warning sx={{ color: '#f59e0b', mt: 0.5 }} />
                                                    ) : rec.severity === 'info' ? (
                                                        <Info sx={{ color: '#3b82f6', mt: 0.5 }} />
                                                    ) : (
                                                        <CheckCircle sx={{ color: '#10b981', mt: 0.5 }} />
                                                    )}
                                                    <Box flex={1}>
                                                        <Typography variant="subtitle2" fontWeight={700} mb={0.5}>
                                                            {rec.title}
                                                        </Typography>
                                                        <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                                                            {rec.message}
                                                        </Typography>
                                                    </Box>
                                                </Box>
                                            ))}
                                        </Box>
                                    ) : (
                                        <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                                            <Typography color="text.secondary">No recommendations available</Typography>
                                        </Box>
                                    )}
                                </Box>
                                 
                                <Button 
                                    variant="contained" 
                                    fullWidth 
                                    disabled={!!error}
                                    sx={{
                                        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
                                        fontWeight: 600,
                                        py: 1.5,
                                        '&:hover': {
                                            background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)'
                                        }
                                    }}
                                >
                                    Run Automated Remediation
                                </Button>
                            </Paper>
                        </Grid>
                    </Grid>
                </>
            )}

            {error && !metrics && (
                <Box textAlign="center" py={8}>
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                        AuditFairness Service Unavailable
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Please ensure the audit-fairness microservice is running on port 5004
                    </Typography>
                    <Button variant="contained" onClick={loadMetrics}>
                        Retry Connection
                    </Button>
                </Box>
            )}
        </Box>
    );
}
