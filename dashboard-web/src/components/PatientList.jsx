import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Pagination,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Skeleton,
  Alert,
} from '@mui/material';
import { Search, FilterList, SortByAlpha } from '@mui/icons-material';
import PatientCard from './PatientCard';
import { getPatients } from '../services/api';

const PATIENTS_PER_PAGE = 12;

export default function PatientList() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('all');
  const [sortBy, setSortBy] = useState('risk_desc');

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    setLoading(true);
    setError(null);
    try {
      const patientsData = await getPatients();
      setPatients(patientsData);
    } catch (error) {
      console.error('Error loading patients:', error);
      setError('Failed to load patient data. Please check if services are running.');
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort patients
  const filteredPatients = patients
    .filter((patient) => {
      // Search filter
      const matchesSearch =
        searchTerm === '' ||
        patient.patient_id?.toLowerCase().includes(searchTerm.toLowerCase());

      // Risk level filter
      const getRiskLevel = (score) => {
        if (score >= 0.8) return 'critical';
        if (score >= 0.6) return 'high';
        if (score >= 0.4) return 'moderate';
        if (score >= 0.2) return 'low';
        return 'minimal';
      };

      const patientRisk = getRiskLevel(patient.risk_score);
      const matchesRisk = riskFilter === 'all' || patientRisk === riskFilter;

      return matchesSearch && matchesRisk;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'risk_desc':
          return (b.risk_score || 0) - (a.risk_score || 0);
        case 'risk_asc':
          return (a.risk_score || 0) - (b.risk_score || 0);
        case 'age_desc':
          return (b.age || 0) - (a.age || 0);
        case 'age_asc':
          return (a.age || 0) - (b.age || 0);
        default:
          return 0;
      }
    });

  const paginatedPatients = filteredPatients.slice(
    (page - 1) * PATIENTS_PER_PAGE,
    page * PATIENTS_PER_PAGE
  );

  const totalPages = Math.ceil(filteredPatients.length / PATIENTS_PER_PAGE);

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1);
  }, [searchTerm, riskFilter, sortBy]);

  if (loading) {
    return (
      <Box>
        <Skeleton variant="text" width={200} height={50} sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {[...Array(6)].map((_, i) => (
            <Grid item xs={12} md={6} lg={4} key={i}>
              <Skeleton variant="rounded" height={280} sx={{ borderRadius: 4 }} />
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
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Patients
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {filteredPatients.length} patients found
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Box
        sx={{
          mb: 4,
          p: 3,
          borderRadius: 3,
          backgroundColor: 'background.paper',
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        }}
      >
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search by patient ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search color="action" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Risk Level</InputLabel>
              <Select
                value={riskFilter}
                label="Risk Level"
                onChange={(e) => setRiskFilter(e.target.value)}
                startAdornment={
                  <InputAdornment position="start">
                    <FilterList color="action" sx={{ ml: 1 }} />
                  </InputAdornment>
                }
              >
                <MenuItem value="all">All Levels</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="moderate">Moderate</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="minimal">Minimal</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                label="Sort By"
                onChange={(e) => setSortBy(e.target.value)}
                startAdornment={
                  <InputAdornment position="start">
                    <SortByAlpha color="action" sx={{ ml: 1 }} />
                  </InputAdornment>
                }
              >
                <MenuItem value="risk_desc">Risk (High to Low)</MenuItem>
                <MenuItem value="risk_asc">Risk (Low to High)</MenuItem>
                <MenuItem value="age_desc">Age (Oldest First)</MenuItem>
                <MenuItem value="age_asc">Age (Youngest First)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Box display="flex" gap={0.5} flexWrap="wrap">
              {riskFilter !== 'all' && (
                <Chip
                  label={`Risk: ${riskFilter}`}
                  size="small"
                  onDelete={() => setRiskFilter('all')}
                />
              )}
              {searchTerm && (
                <Chip
                  label={`Search: ${searchTerm}`}
                  size="small"
                  onDelete={() => setSearchTerm('')}
                />
              )}
            </Box>
          </Grid>
        </Grid>
      </Box>

      {/* Patient Grid */}
      {paginatedPatients.length === 0 ? (
        <Box
          sx={{
            textAlign: 'center',
            py: 8,
            backgroundColor: 'grey.50',
            borderRadius: 3,
          }}
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No patients found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search or filter criteria
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {paginatedPatients.map((patient) => (
            <Grid item xs={12} md={6} lg={4} key={patient.patient_id}>
              <PatientCard patient={patient} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, mb: 2 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(e, value) => setPage(value)}
            color="primary"
            size="large"
            showFirstButton
            showLastButton
            sx={{
              '& .MuiPaginationItem-root': {
                fontWeight: 500,
              },
            }}
          />
        </Box>
      )}

      {/* Results summary */}
      <Box textAlign="center">
        <Typography variant="body2" color="text.secondary">
          Showing {(page - 1) * PATIENTS_PER_PAGE + 1} -{' '}
          {Math.min(page * PATIENTS_PER_PAGE, filteredPatients.length)} of{' '}
          {filteredPatients.length} patients
        </Typography>
      </Box>
    </Box>
  );
}
