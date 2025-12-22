import React from 'react';
import {
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  Box,
  LinearProgress,
  Typography,
  Chip,
  Alert
} from '@mui/material';

const PipelineStatus = ({ 
  steps, 
  activeStep, 
  results, 
  loading, 
  elapsedTime, 
  getStepEstimate,
  patientCount 
}) => {
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Stepper activeStep={activeStep}>
          {steps.map((step) => (
            <Step key={step.label}>
              <StepLabel
                icon={step.icon}
                error={results.find(r => r.step === step.label)?.status === 'error'}
              >
                {step.label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        {loading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress />
            <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2">
                Executing: <strong>{steps[activeStep]?.label}</strong>
              </Typography>
              <Chip 
                label={`Elapsed: ${formatTime(elapsedTime)}`} 
                size="small" 
                color="primary"
              />
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Estimated time for this step: {getStepEstimate(activeStep)}
            </Typography>
            {activeStep === 0 && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <strong>FHIR Processing in progress...</strong> This may take time depending on data generation/sync needs.
              </Alert>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default PipelineStatus;
