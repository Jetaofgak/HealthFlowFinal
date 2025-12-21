import { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Grid,
    Card,
    CardContent,
    Chip,
    TextField,
    Skeleton,
    Alert,
    LinearProgress,
} from '@mui/material';
import { Psychology, LocalHospital, Medication, Warning } from '@mui/icons-material';
import { getFeatures } from '../services/api';

export default function NLPInsights() {
    const [features, setFeatures] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        loadFeatures();
    }, []);

    const loadFeatures = async () => {
        setLoading(true);
        try {
            const data = await getFeatures();
            setFeatures(data);
        } catch (error) {
            console.error('Error loading features:', error);
            setError('Failed to load NLP insights data');
        } finally {
            setLoading(false);
        }
    };

    // Aggregate NLP statistics
    const nlpStats = {
        totalPatients: features.length,
        patientsWithDiabetes: features.filter((f) => f.nlp_has_diabetes === 1).length,
        patientsWithHypertension: features.filter((f) => f.nlp_has_hypertension === 1).length,
        patientsWithChf: features.filter((f) => f.nlp_has_chf === 1).length,
        patientsWithCopd: features.filter((f) => f.nlp_has_copd === 1).length,
        patientsWithPolypharmacy: features.filter((f) => f.nlp_polypharmacy === 1).length,
        avgConditions: features.length > 0
            ? (features.reduce((sum, f) => sum + (f.nlp_num_conditions || 0), 0) / features.length).toFixed(1)
            : 0,
        avgMedications: features.length > 0
            ? (features.reduce((sum, f) => sum + (f.nlp_num_medications || 0), 0) / features.length).toFixed(1)
            : 0,
        avgSymptoms: features.length > 0
            ? (features.reduce((sum, f) => sum + (f.nlp_num_symptoms || 0), 0) / features.length).toFixed(1)
            : 0,
    };

    // Condition data for word cloud
    const conditionData = [
        { name: 'Diabetes', count: nlpStats.patientsWithDiabetes, color: '#F39C12', icon: LocalHospital },
        { name: 'Hypertension', count: nlpStats.patientsWithHypertension, color: '#E74C3C', icon: Warning },
        { name: 'Heart Failure (CHF)', count: nlpStats.patientsWithChf, color: '#C0392B', icon: LocalHospital },
        { name: 'COPD', count: nlpStats.patientsWithCopd, color: '#9B59B6', icon: LocalHospital },
        { name: 'Polypharmacy', count: nlpStats.patientsWithPolypharmacy, color: '#3498DB', icon: Medication },
    ].sort((a, b) => b.count - a.count);

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

    return (
        <Box className="fade-in">
            {/* Header */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
                <Box>
                    <Typography variant="h4" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Psychology color="primary" sx={{ fontSize: 40 }} />
                        NLP Insights
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Clinical notes analysis powered by BioBERT
                    </Typography>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {/* Summary Stats */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={6} sm={4} md={2}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" fontWeight={700} color="primary.main">
                                {nlpStats.totalPatients}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Patients Analyzed
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={6} sm={4} md={2}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" fontWeight={700} color="secondary.main">
                                {nlpStats.avgConditions}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Avg Conditions
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={6} sm={4} md={2}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" fontWeight={700} color="info.main">
                                {nlpStats.avgMedications}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Avg Medications
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={6} sm={4} md={2}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" fontWeight={700} color="warning.main">
                                {nlpStats.avgSymptoms}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Avg Symptoms
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={6} sm={4} md={2}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" fontWeight={700} color="error.main">
                                {nlpStats.patientsWithPolypharmacy}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Polypharmacy
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={6} sm={4} md={2}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" fontWeight={700} color="success.main">
                                14
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                NLP Features
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Condition Word Cloud */}
            <Card sx={{ mb: 4 }}>
                <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                        Most Common Conditions (NLP Extracted)
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Conditions detected from clinical notes using BioBERT NLP
                    </Typography>

                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                        {conditionData.map((condition) => {
                            const Icon = condition.icon;
                            const percentage = nlpStats.totalPatients > 0
                                ? ((condition.count / nlpStats.totalPatients) * 100).toFixed(1)
                                : 0;

                            return (
                                <Box
                                    key={condition.name}
                                    sx={{
                                        flex: '1 1 200px',
                                        p: 2,
                                        borderRadius: 3,
                                        backgroundColor: `${condition.color}10`,
                                        border: `1px solid ${condition.color}30`,
                                        transition: 'all 0.2s ease',
                                        '&:hover': {
                                            transform: 'translateY(-2px)',
                                            boxShadow: `0 4px 12px ${condition.color}30`,
                                        },
                                    }}
                                >
                                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                                        <Icon sx={{ color: condition.color }} />
                                        <Typography variant="subtitle2" fontWeight={600}>
                                            {condition.name}
                                        </Typography>
                                    </Box>
                                    <Typography variant="h5" fontWeight={700} sx={{ color: condition.color }}>
                                        {condition.count}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        {percentage}% of patients
                                    </Typography>
                                    <LinearProgress
                                        variant="determinate"
                                        value={parseFloat(percentage)}
                                        sx={{
                                            mt: 1,
                                            height: 4,
                                            borderRadius: 2,
                                            backgroundColor: `${condition.color}20`,
                                            '& .MuiLinearProgress-bar': {
                                                backgroundColor: condition.color,
                                            },
                                        }}
                                    />
                                </Box>
                            );
                        })}
                    </Box>
                </CardContent>
            </Card>

            {/* NLP Feature Descriptions */}
            <Card>
                <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                        BioBERT NLP Features (14 Total)
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Features extracted from clinical notes using BioBERT medical NLP
                    </Typography>

                    <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                            <Box sx={{ p: 2, borderRadius: 2, backgroundColor: 'grey.50' }}>
                                <Typography variant="subtitle2" fontWeight={600} color="primary.main" gutterBottom>
                                    Comorbidity Detection
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                    <Chip label="nlp_has_chf" size="small" variant="outlined" />
                                    <Chip label="nlp_has_copd" size="small" variant="outlined" />
                                    <Chip label="nlp_has_ckd" size="small" variant="outlined" />
                                    <Chip label="nlp_has_diabetes" size="small" variant="outlined" />
                                    <Chip label="nlp_has_hypertension" size="small" variant="outlined" />
                                    <Chip label="nlp_num_conditions" size="small" variant="outlined" />
                                </Box>
                            </Box>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Box sx={{ p: 2, borderRadius: 2, backgroundColor: 'grey.50' }}>
                                <Typography variant="subtitle2" fontWeight={600} color="secondary.main" gutterBottom>
                                    Medication & Symptoms
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                    <Chip label="nlp_num_medications" size="small" variant="outlined" />
                                    <Chip label="nlp_polypharmacy" size="small" variant="outlined" />
                                    <Chip label="nlp_num_symptoms" size="small" variant="outlined" />
                                    <Chip label="nlp_has_pain" size="small" variant="outlined" />
                                    <Chip label="nlp_has_dyspnea" size="small" variant="outlined" />
                                </Box>
                            </Box>
                        </Grid>
                        <Grid item xs={12}>
                            <Box sx={{ p: 2, borderRadius: 2, backgroundColor: 'grey.50' }}>
                                <Typography variant="subtitle2" fontWeight={600} color="info.main" gutterBottom>
                                    Clinical Note Statistics
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                    <Chip label="nlp_note_length" size="small" variant="outlined" />
                                    <Chip label="nlp_note_count" size="small" variant="outlined" />
                                    <Chip label="nlp_avg_note_length" size="small" variant="outlined" />
                                </Box>
                            </Box>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </Box>
    );
}
