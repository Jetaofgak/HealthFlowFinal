import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  IconButton,
  Collapse,
  Divider,
  LinearProgress,
  Avatar,
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  Person,
  Favorite,
  Thermostat,
  Speed,
  Medication,
  Psychology,
} from '@mui/icons-material';
import { useState } from 'react';
import RiskBadge, { getRiskLevel, getRiskConfig } from './RiskBadge';

export default function PatientCard({ patient, onClick }) {
  const [expanded, setExpanded] = useState(false);

  // Framingham score is 1-20, need to normalize for risk level calculation
  const framinghamScore = patient.framingham_score || patient.risk_score || 0;
  
  // Convert Framingham score (1-20 range) to risk level
  // Framingham: 1-4=low, 5-8=moderate, 9-12=high, 13+=critical
  const getRiskLevelFromFramingham = (score) => {
    if (score >= 13) return 'critical';
    if (score >= 9) return 'high';
    if (score >= 5) return 'moderate';
    if (score >= 1) return 'low';
    return 'minimal';
  };
  
  const riskLevel = patient.risk_level || getRiskLevelFromFramingham(framinghamScore);
  const riskConfig = getRiskConfig(riskLevel);

  const vitalSigns = [
    { label: 'Heart Rate', value: patient.vit_heart_rate, unit: 'bpm', icon: Favorite, color: '#E74C3C' },
    { label: 'BMI', value: patient.bmi, unit: '', icon: Person, color: '#3498DB' },
  ].filter(v => v.value !== undefined && v.value !== null);

  const labResults = [
    { label: 'Total Cholesterol', value: patient.avg_cholesterol, unit: 'mg/dL', normal: '< 200' },
    { label: 'HDL', value: patient.avg_hdl, unit: 'mg/dL', normal: '> 40' },
    { label: 'LDL', value: patient.avg_ldl, unit: 'mg/dL', normal: '< 100' },
  ].filter(v => v.value !== undefined && v.value !== null);

  const physicalMetrics = [
    { label: 'Weight', value: patient.weight_kg, unit: 'kg' },
    { label: 'Height', value: patient.height_cm, unit: 'cm' },
  ].filter(v => v.value !== undefined && v.value !== null);

  const nlpFeatures = {
    conditions: patient.nlp_num_conditions || 0,
    medications: patient.nlp_num_medications || 0,
    symptoms: patient.nlp_num_symptoms || 0,
    hasChf: patient.nlp_has_chf === 1,
    hasCopd: patient.nlp_has_copd === 1,
    hasDiabetes: patient.nlp_has_diabetes === 1,
    hasHypertension: patient.nlp_has_hypertension === 1,
    polypharmacy: patient.nlp_polypharmacy === 1,
  };

  const hasNlpData = nlpFeatures.conditions > 0 || nlpFeatures.medications > 0;

  return (
    <Card
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        overflow: 'visible',
        '&::before': {
          content: '""',
          position: 'absolute',
          left: 0,
          top: 16,
          bottom: 16,
          width: 4,
          borderRadius: '0 4px 4px 0',
          backgroundColor: riskConfig.color,
        },
      }}
      onClick={onClick}
    >
      <CardContent>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                backgroundColor: `${riskConfig.color}20`,
                color: riskConfig.color,
                fontWeight: 600,
              }}
            >
              {patient.patient_id?.slice(-2) || 'P'}
            </Avatar>
            <Box>
              <Typography variant="subtitle1" fontWeight={600}>
                Patient #{patient.patient_id?.slice(-8) || 'Unknown'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {patient.gender || 'Unknown'} • Age {patient.age || 'N/A'}
              </Typography>
            </Box>
          </Box>
          <RiskBadge riskLevel={riskLevel} score={framinghamScore} showScore={false} size="small" />
        </Box>

        {/* Framingham Risk Score */}
        <Box sx={{ mb: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
            <Typography variant="caption" color="text.secondary">
              Framingham Score
            </Typography>
            <Typography variant="caption" fontWeight={600} color={riskConfig.color}>
              {Math.min(framinghamScore, 20).toFixed(0)} / 20
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min((framinghamScore / 20) * 100, 100)}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                backgroundColor: riskConfig.color,
                borderRadius: 3,
              },
            }}
          />
        </Box>

        {/* Vital Signs */}
        {vitalSigns.length > 0 && (
          <Grid container spacing={1} sx={{ mb: 2 }}>
            {vitalSigns.map((vital) => {
              const Icon = vital.icon;
              return (
                <Grid size={{ xs: 6 }} key={vital.label}>
                  <Box
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      backgroundColor: `${vital.color}10`,
                      border: `1px solid ${vital.color}30`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                    }}
                  >
                    <Icon sx={{ fontSize: 20, color: vital.color }} />
                    <Box>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {vital.label}
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {typeof vital.value === 'number' ? vital.value.toFixed(1) : vital.value}
                        {vital.unit && <span style={{ fontWeight: 400, marginLeft: 2 }}>{vital.unit}</span>}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              );
            })}
          </Grid>
        )}

        {/* Lab Results */}
        {labResults.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary" fontWeight={600} display="block" mb={1}>
              Lab Results
            </Typography>
            <Grid container spacing={1}>
              {labResults.map((lab) => (
                <Grid size={{ xs: 4 }} key={lab.label}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 1.5,
                      backgroundColor: 'grey.50',
                      textAlign: 'center',
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" display="block" noWrap>
                      {lab.label}
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {typeof lab.value === 'number' ? lab.value.toFixed(0) : lab.value}
                    </Typography>
                    <Typography variant="caption" color="success.main" display="block">
                      {lab.normal}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Physical Metrics */}
        {physicalMetrics.length > 0 && (
          <Grid container spacing={1} sx={{ mb: 2 }}>
            {physicalMetrics.map((metric) => (
              <Grid size={{ xs: 6 }} key={metric.label}>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 1.5,
                    backgroundColor: 'grey.50',
                    textAlign: 'center',
                  }}
                >
                  <Typography variant="caption" color="text.secondary" display="block">
                    {metric.label}
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {typeof metric.value === 'number' ? metric.value.toFixed(1) : metric.value}
                    {metric.unit && <span style={{ fontWeight: 400, marginLeft: 2 }}>{metric.unit}</span>}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        )}

        {/* NLP Insights Toggle */}
        {hasNlpData && (
          <>
            <Divider sx={{ my: 1 }} />
            <Box
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}
              sx={{ cursor: 'pointer', py: 1 }}
            >
              <Box display="flex" alignItems="center" gap={1}>
                <Psychology sx={{ fontSize: 18, color: 'primary.main' }} />
                <Typography variant="body2" fontWeight={500} color="primary.main">
                  NLP Insights
                </Typography>
              </Box>
              <IconButton size="small">
                {expanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Box>

            <Collapse in={expanded}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  backgroundColor: 'rgba(0, 102, 204, 0.05)',
                  border: '1px solid rgba(0, 102, 204, 0.1)',
                }}
              >
                <Grid container spacing={1}>
                  <Grid size={{ xs: 6 }}>
                    <Typography variant="caption" color="text.secondary">
                      Conditions Detected
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {nlpFeatures.conditions}
                    </Typography>
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Typography variant="caption" color="text.secondary">
                      Medications
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {nlpFeatures.medications}
                    </Typography>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 1.5, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {nlpFeatures.hasDiabetes && (
                    <Chip label="Diabetes" size="small" color="warning" variant="outlined" />
                  )}
                  {nlpFeatures.hasHypertension && (
                    <Chip label="Hypertension" size="small" color="error" variant="outlined" />
                  )}
                  {nlpFeatures.hasChf && (
                    <Chip label="CHF" size="small" color="error" variant="outlined" />
                  )}
                  {nlpFeatures.hasCopd && (
                    <Chip label="COPD" size="small" color="warning" variant="outlined" />
                  )}
                  {nlpFeatures.polypharmacy && (
                    <Chip
                      icon={<Medication sx={{ fontSize: 14 }} />}
                      label="Polypharmacy"
                      size="small"
                      color="info"
                      variant="outlined"
                    />
                  )}
                </Box>

                {/* Risk Factors */}
                {patient.risk_factors && patient.risk_factors.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={600} display="block" mb={0.5}>
                      Risk Factors
                    </Typography>
                    {patient.risk_factors.filter(f => f).slice(0, 3).map((factor, idx) => {
                      // Handle both string and object formats
                      const isObj = typeof factor === 'object' && factor !== null;
                      const label = isObj ? factor.factor : factor;
                      const value = isObj ? `: ${typeof factor.value === 'number' ? factor.value.toFixed(1) : factor.value}` : '';
                      
                      return (
                        <Box key={idx} sx={{ mb: 0.5 }}>
                          <Typography variant="caption" color="error.main">
                            • {label}{value}
                          </Typography>
                        </Box>
                      );
                    })}
                  </Box>
                )}

                {/* Top Recommendations */}
                {patient.recommendations && patient.recommendations.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={600} display="block" mb={0.5}>
                      Recommendations
                    </Typography>
                    {patient.recommendations.filter(r => r).slice(0, 2).map((rec, idx) => {
                      // Handle both string and object formats
                      const isObj = typeof rec === 'object' && rec !== null;
                      const text = isObj ? rec.action : rec;
                      
                      return (
                        <Box key={idx} sx={{ mb: 0.5 }}>
                          <Typography variant="caption" color="primary.main">
                            • {text}
                          </Typography>
                        </Box>
                      );
                    })}
                  </Box>
                )}
              </Box>
            </Collapse>
          </>
        )}
      </CardContent>
    </Card>
  );
}
