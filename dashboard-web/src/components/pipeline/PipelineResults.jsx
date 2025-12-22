import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  Box,
  ListItemText,
  Chip,
  Divider
} from '@mui/material';
import { CheckCircle, Error } from '@mui/icons-material';

const PipelineResults = ({ results, steps }) => {
  if (results.length === 0) return null;

  return (
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
                    {result.data.message && !result.data.synced && !result.data.generated && (
                        <Typography variant="body2">
                            ℹ️ {result.data.message}
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
        {results.length === steps.length && !results.some(r => r.status === 'error') && (
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
  );
};

export default PipelineResults;
