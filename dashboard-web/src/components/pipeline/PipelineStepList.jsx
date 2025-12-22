import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button
} from '@mui/material';
import { CheckCircle, Error } from '@mui/icons-material';

const PipelineStepList = ({ 
  steps, 
  activeStep, 
  results, 
  loading, 
  onRunStep, 
  getStepEstimate 
}) => {
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Execute Individual Steps
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Run each step separately for testing or debugging
        </Typography>
        <Box display="flex" flexDirection="column" gap={2}>
          {steps.map((step, index) => (
            <Box 
              key={step.label} 
              display="flex" 
              alignItems="center" 
              gap={2}
              sx={{ 
                p: 1, 
                borderRadius: 1, 
                bgcolor: activeStep === index ? 'action.selected' : 'transparent' 
              }}
            >
              <Box sx={{ color: 'primary.main' }}>
                {step.icon}
              </Box>
              <Box sx={{ flexGrow: 1 }}>
                <Typography>{step.label}</Typography>
                <Typography variant="caption" color="text.secondary">
                  Est. time: {getStepEstimate(index)}
                </Typography>
              </Box>
              {results.find(r => r.step === step.label)?.status === 'success' && (
                <CheckCircle color="success" />
              )}
              {results.find(r => r.step === step.label)?.status === 'error' && (
                <Error color="error" />
              )}
              <Button
                variant="outlined"
                onClick={() => onRunStep(index)}
                disabled={loading}
              >
                Run
              </Button>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default PipelineStepList;
