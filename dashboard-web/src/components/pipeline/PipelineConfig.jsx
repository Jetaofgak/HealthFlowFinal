import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  CircularProgress
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';

const PipelineConfig = ({ patientCount, setPatientCount, forceGenerate, setForceGenerate, loading, onRun }) => {
  return (
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
            helperText="1-100 patients recommended"
          />
          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
            onClick={onRun}
            disabled={loading}
          >
            Run Full Pipeline
          </Button>
        </Box>
        <Box sx={{ mt: 2 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                <input 
                    type="checkbox"
                    checked={forceGenerate}
                    onChange={(e) => setForceGenerate(e.target.checked)}
                    disabled={loading}
                    style={{ width: '16px', height: '16px' }}
                />
                <Typography variant="body2">
                    Force Generate Data (even if local data exists)
                </Typography>
            </label>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          ⏱️ Estimated total time: ~3-10 minutes for 100 patients
        </Typography>
      </CardContent>
    </Card>
  );
};

export default PipelineConfig;
