import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  useMediaQuery,
  useTheme,
  Avatar,
} from '@mui/material';
import { Menu as MenuIcon, LocalHospital, Notifications } from '@mui/icons-material';

// Components
import Sidebar, { SIDEBAR_WIDTH } from './components/Sidebar';
import Dashboard from './components/Dashboard';
import PatientList from './components/PatientList';
import HealthStatus from './components/HealthStatus';
import Pipeline from './components/Pipeline';
import RiskAnalytics from './components/RiskAnalytics';
import NLPInsights from './components/NLPInsights';
import AuditFairness from './components/AuditFairness';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Router>
      <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: 'background.default' }}>
        {/* Sidebar */}
        <Sidebar open={sidebarOpen} onToggle={handleSidebarToggle} />

        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            width: { md: `calc(100% - ${SIDEBAR_WIDTH}px)` },
            ml: { md: 0 },
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Header */}
          <AppBar
            position="sticky"
            elevation={0}
            sx={{
              backgroundColor: 'background.paper',
              borderBottom: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Toolbar>
              {isMobile && (
                <IconButton
                  color="inherit"
                  edge="start"
                  onClick={handleSidebarToggle}
                  sx={{ mr: 2, color: 'text.primary' }}
                >
                  <MenuIcon />
                </IconButton>
              )}

              {isMobile && (
                <Box display="flex" alignItems="center" gap={1}>
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      background: 'linear-gradient(135deg, #0066CC 0%, #004C99 100%)',
                    }}
                  >
                    <LocalHospital sx={{ fontSize: 18 }} />
                  </Avatar>
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 700,
                      background: 'linear-gradient(135deg, #0066CC 0%, #00A86B 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}
                  >
                    HealthFlow
                  </Typography>
                </Box>
              )}

              <Box sx={{ flexGrow: 1 }} />

              {/* Right side actions */}
              <Box display="flex" alignItems="center" gap={2}>
                <Box
                  sx={{
                    px: 2,
                    py: 0.5,
                    borderRadius: 2,
                    backgroundColor: 'rgba(0, 168, 107, 0.1)',
                    border: '1px solid rgba(0, 168, 107, 0.2)',
                    display: { xs: 'none', sm: 'block' },
                  }}
                >
                  <Typography variant="caption" color="secondary.main" fontWeight={600}>
                    Model: XGBoost + BioBERT
                  </Typography>
                </Box>

                <IconButton sx={{ color: 'text.secondary' }}>
                  <Notifications />
                </IconButton>

                <Avatar
                  sx={{
                    width: 36,
                    height: 36,
                    backgroundColor: 'primary.main',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                  }}
                >
                  Dr
                </Avatar>
              </Box>
            </Toolbar>
          </AppBar>

          {/* Page Content */}
          <Box
            sx={{
              flexGrow: 1,
              p: { xs: 2, sm: 3, md: 4 },
              overflow: 'auto',
            }}
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/patients" element={<PatientList />} />
              <Route path="/analytics" element={<RiskAnalytics />} />
              <Route path="/audit-fairness" element={<AuditFairness />} />
              <Route path="/nlp" element={<NLPInsights />} />
              <Route path="/pipeline" element={<Pipeline />} />
              <Route path="/health" element={<HealthStatus />} />
            </Routes>
          </Box>

          {/* Footer */}
          <Box
            component="footer"
            sx={{
              py: 2,
              px: 3,
              borderTop: '1px solid',
              borderColor: 'divider',
              backgroundColor: 'background.paper',
              textAlign: 'center',
            }}
          >
            <Typography variant="caption" color="text.secondary">
              HealthFlow Analytics Platform • EMSI 2026 • XGBoost ROC-AUC: 88.27%
            </Typography>
          </Box>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
