import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Alert
} from '@mui/material';
import {
  Science,
  AutoGraph,
  Storage
} from '@mui/icons-material';
import axios from 'axios';
import * as api from '../services/api';

import PipelineConfig from './pipeline/PipelineConfig';
import PipelineStatus from './pipeline/PipelineStatus';
import PipelineStepList from './pipeline/PipelineStepList';
import PipelineResults from './pipeline/PipelineResults';

const API_BASE_URL = 'http://localhost:8085/api/v1';

// Step definitions
const steps = [
  { label: 'Check/Generate Data', endpoint: '/fhir/count', icon: <Storage /> },
  { label: 'Anonymize', endpoint: '/deid/anonymize/all', icon: <Storage /> },
  { label: 'Extract Features', endpoint: '/features/extract/all', icon: <Science /> },
  { label: 'Predict Risks', endpoint: '/predictions/predict/all', icon: <AutoGraph /> }
];

const Pipeline = () => {
  const [activeStep, setActiveStep] = useState(-1);
  const [loading, setLoading] = useState(false);
  const [patientCount, setPatientCount] = useState(1);
  const [forceGenerate, setForceGenerate] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Timer loop
  useEffect(() => {
    let interval;
    if (loading) {
      interval = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      setElapsedTime(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const executeStep = async (step, index) => {
    try {
      setActiveStep(index);
      setError(null);

      // Special handling for Step 1 (Check/Generate Data)
      if (index === 0) {
          // Check count first
          const countResult = await api.getLocalPatientCount();
          const hasData = countResult.count && countResult.count > 0;
          
          if (hasData && !forceGenerate) {
               // Data exists and we don't want to force generate
               const newResult = {
                  step: step.label,
                  status: 'success',
                  data: { 
                      message: `Found ${countResult.count} patients. Ready to proceed.`,
                      synced: countResult.count
                  },
                  timestamp: new Date().toLocaleTimeString()
              };
              setResults(prev => [...prev, newResult]);
              return true;
          } else {
              // No data OR force generate is true
              const initialCount = hasData ? countResult.count : 0;
              const genResult = await api.generatePatients(patientCount);
              const newTotal = initialCount + genResult.generated;
              
              const newResult = {
                  step: step.label,
                  status: 'success',
                  data: {
                      message: `Generated ${genResult.generated} new patients in ${genResult.duration}ms. Total: ${newTotal}`,
                      synced: genResult.generated,
                      generated: genResult.generated
                  },
                  timestamp: new Date().toLocaleTimeString()
              };
              setResults(prev => [...prev, newResult]);
              return true;
          }
      }

      const url = `${API_BASE_URL}${step.endpoint}`;
      
      // Timeout différent selon l'étape
      const timeout = step.endpoint === '/fhir/sync/bulk' ? 600000 : 120000; // 10min pour FHIR, 2min pour les autres

      const response = await axios.post(url, {}, {
        timeout: timeout
      });

      const newResult = {
        step: step.label,
        status: 'success',
        data: response.data,
        timestamp: new Date().toLocaleTimeString()
      };

      setResults(prev => [...prev, newResult]);
      return true;
    } catch (err) {
      const newResult = {
        step: step.label,
        status: 'error',
        error: err.response?.data?.error || err.message,
        timestamp: new Date().toLocaleTimeString()
      };
      setResults(prev => [...prev, newResult]);
      setError(`Error in ${step.label}: ${err.message}`);
      return false;
    }
  };

  const runFullPipeline = async () => {
    setLoading(true);
    setResults([]);
    setError(null);

    for (let i = 0; i < steps.length; i++) {
      const success = await executeStep(steps[i], i);
      if (!success) {
        setLoading(false);
        setActiveStep(-1);
        return;
      }
    }

    setLoading(false);
    setActiveStep(-1);
  };

  const runSingleStep = async (index) => {
    setLoading(true);
    setResults([]);
    setError(null);
    await executeStep(steps[index], index);
    setLoading(false);
    setActiveStep(-1);
  };

  const getStepEstimate = (stepIndex) => {
    switch(stepIndex) {
      case 0: return '2-5 minutes';
      case 1: return '2-5 minutes';
      case 2: return '30-60 seconds';
      case 3: return '5-15 seconds';
      default: return '';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Pipeline Execution
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Execute the complete data processing pipeline: Sync FHIR data → Anonymize → Extract Features → Predict Risks
      </Typography>

      <PipelineConfig 
        patientCount={patientCount}
        setPatientCount={setPatientCount}
        forceGenerate={forceGenerate}
        setForceGenerate={setForceGenerate}
        loading={loading}
        onRun={runFullPipeline}
      />

      <PipelineStatus 
        steps={steps}
        activeStep={activeStep}
        results={results}
        loading={loading}
        elapsedTime={elapsedTime}
        getStepEstimate={getStepEstimate}
        patientCount={patientCount}
      />

      <PipelineStepList 
        steps={steps}
        activeStep={activeStep}
        results={results}
        loading={loading}
        onRunStep={runSingleStep}
        getStepEstimate={getStepEstimate}
      />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <PipelineResults 
        results={results}
        steps={steps}
      />
    </Box>
  );
}

export default Pipeline;
