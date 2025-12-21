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

  const riskScore = patient.risk_score || patient.framingham_score || 0;
  const riskLevel = getRiskLevel(riskScore);
  const riskConfig = getRiskConfig(riskLevel);

  const vitalSigns = [
    { label: 'Heart Rate', value: patient.vit_heart_rate, unit: 'bpm', icon: Favorite },
    { label: 'BP Systolic', value: patient.vit_bp_systolic, unit: 'mmHg', icon: Speed },
    { label: 'Temperature', value: patient.vit_temperature, unit: '°F', icon: Thermostat },
    { label: 'BMI', value: patient.bmi, unit: '', icon: Person },
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
          <RiskBadge riskLevel={riskLevel} score={riskScore} size="small" />
        </Box>

        {/* Risk Score Bar */}
        <Box sx={{ mb: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
            <Typography variant="caption" color="text.secondary">
              Risk Score
            </Typography>
            <Typography variant="caption" fontWeight={600} color={riskConfig.color}>
              {(riskScore * 100).toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={riskScore * 100}
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
            {vitalSigns.slice(0, 4).map((vital) => {
              const Icon = vital.icon;
              return (
                <Grid item xs={6} key={vital.label}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 1,
                      backgroundColor: 'grey.50',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                    }}
                  >
                    <Icon sx={{ fontSize: 16, color: 'text.secondary' }} />
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
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Conditions Detected
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {nlpFeatures.conditions}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
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
              </Box>
            </Collapse>
          </>
        )}
      </CardContent>
    </Card>
  );
}
