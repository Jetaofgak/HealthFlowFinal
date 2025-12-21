import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Stepper,
  Step,
  StepLabel,
  Alert,
  CircularProgress,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  CheckCircle,
  Error,
  Sync,
  Science,
  AutoGraph,
  Storage
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8085/api/v1';

const steps = [
  { label: 'Sync FHIR', endpoint: '/fhir/sync/bulk', icon: <Sync /> },
  { label: 'Anonymize', endpoint: '/deid/anonymize/all', icon: <Storage /> },
  { label: 'Extract Features', endpoint: '/features/extract/all', icon: <Science /> },
  { label: 'Predict Risks', endpoint: '/predictions/predict/all', icon: <AutoGraph /> }
];

function Pipeline() {
  const [patientCount, setPatientCount] = useState(100);
  const [activeStep, setActiveStep] = useState(-1);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Timer pour afficher le temps écoulé
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

      const url = step.endpoint === '/fhir/sync/bulk' 
        ? `${API_BASE_URL}${step.endpoint}?count=${patientCount}`
        : `${API_BASE_URL}${step.endpoint}`;

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
      // Skip Sync if checkbox is checked
      if (i === 0 && document.getElementById('skipSync')?.checked) {
          const skipResult = {
              step: steps[i].label,
              status: 'success',
              data: { message: 'Skipped (Data Loaded Locally)' },
              timestamp: new Date().toLocaleTimeString()
          };
          setResults(prev => [...prev, skipResult]);
          continue;
      }
      
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

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
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

      {/* Configuration */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Configuration
          </Typography>
          <Box display="flex" alignItems="center" gap={2}>
            <TextField
              label="Number of Patients"
              type="number"
              value={patientCount}
              onChange={(e) => setPatientCount(parseInt(e.target.value))}
              disabled={loading}
              sx={{ width: 200 }}
              helperText="10-100 patients recommended"
            />
            <Box display="flex" alignItems="center" gap={1}>
                {/* Checkbox manually implemented since I can't import properly without seeing lines */}
                <input 
                    type="checkbox" 
                    id="skipSync" 
                    defaultChecked={true} 
                    style={{ width: 20, height: 20 }}
                />
                <label htmlFor="skipSync" style={{ cursor: 'pointer' }}>
                    <Typography variant="body2">Skip Sync (Data Loaded Locally)</Typography>
                </label>
            </Box>
            <Button
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
              onClick={runFullPipeline}
              disabled={loading}
            >
              Run Full Pipeline
            </Button>
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            ⏱️ Estimated total time: ~3-10 minutes for 100 patients
          </Typography>
        </CardContent>
      </Card>

      {/* Stepper */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stepper activeStep={activeStep}>
            {steps.map((step, index) => (
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
                  <strong>FHIR Sync in progress...</strong> This may take 2-5 minutes for {patientCount} patients. Please wait.
                </Alert>
              )}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Individual Steps */}
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
                  onClick={() => runSingleStep(index)}
                  disabled={loading}
                >
                  Run
                </Button>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {results.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Execution Results
            </Typography>
            <List>
              {results.map((result, index) => (
                <div key={index}>
                  <ListItem>
                    <Box display="flex" alignItems="center" width="100%" gap={2}>
                      {result.status === 'success' ? (
                        <CheckCircle color="success" />
                      ) : (
                        <Error color="error" />
                      )}
                      <ListItemText
                        primary={result.step}
                        secondary={result.timestamp}
                      />
                      <Chip
                        label={result.status}
                        color={result.status === 'success' ? 'success' : 'error'}
                        size="small"
                      />
                    </Box>
                  </ListItem>

                  {/* Details */}
                  <Box sx={{ pl: 7, pr: 2, pb: 2 }}>
                    {result.status === 'success' ? (
                      <Box>
                        {result.data.synced !== undefined && (
                          <Typography variant="body2">
                            ✅ Synced: <strong>{result.data.synced}</strong> patients
                            {result.data.failed > 0 && ` (${result.data.failed} failed)`}
                          </Typography>
                        )}
                        {result.data.totalResources !== undefined && (
                          <Typography variant="body2">
                            📦 Total resources: <strong>{result.data.totalResources}</strong>
                          </Typography>
                        )}
                        {result.data.anonymized !== undefined && (
                          <Typography variant="body2">
                            🔒 Anonymized: <strong>{result.data.anonymized}</strong> patients
                          </Typography>
                        )}
                        {result.data.extracted !== undefined && (
                          <Typography variant="body2">
                            🧪 Extracted: <strong>{result.data.extracted}</strong> features
                          </Typography>
                        )}
                        {result.data.predicted !== undefined && (
                          <Typography variant="body2">
                            📊 Predicted: <strong>{result.data.predicted}</strong> patients
                          </Typography>
                        )}
                        {result.data.errors > 0 && (
                          <Typography variant="body2" color="warning.main">
                            ⚠️ Errors: {result.data.errors}
                          </Typography>
                        )}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="error">
                        ❌ {result.error}
                      </Typography>
                    )}
                  </Box>
                  {index < results.length - 1 && <Divider />}
                </div>
              ))}
            </List>

            {/* Summary */}
            {results.length === steps.length && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                <Typography variant="h6" color="success.dark">
                  ✅ Pipeline Completed Successfully!
                </Typography>
                <Typography variant="body2" color="success.dark">
                  All steps executed. Check the Dashboard and Patients tabs to view results.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default Pipeline;
