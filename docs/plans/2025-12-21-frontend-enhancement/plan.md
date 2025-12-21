# HealthFlow Dashboard Enhancement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: use executing-plans skill to implement this plan task-by-task.

**Goal:** Transform the HealthFlow dashboard into a production-grade medical analytics platform with distinctive design, advanced visualizations, and comprehensive patient risk analysis features.

**Architecture:** Modern React dashboard with Material-UI components enhanced by custom medical-themed design system. Integrates with 5 microservices via API Gateway to display real-time health metrics, NLP-extracted insights, and ML-powered risk predictions.

**Tech Stack:** React 18, Vite, Material-UI v5, Recharts, Axios, CSS Variables

---

## Task 1: Establish Medical-Themed Design System

**Files:**

- Create: `dashboard-web/src/theme/medicalTheme.js`
- Create: `dashboard-web/src/theme/colors.css`
- Modify: `dashboard-web/src/index.css`

**Step 1: Create medical color palette**

Create `dashboard-web/src/theme/colors.css`:

```css
:root {
  /* Primary Medical Palette - Clinical Blues */
  --medical-primary: #0066cc;
  --medical-primary-light: #3399ff;
  --medical-primary-dark: #004c99;

  /* Accent - Vital Signs Green */
  --medical-accent: #00a86b;
  --medical-accent-light: #2ecc71;

  /* Risk Levels */
  --risk-critical: #e74c3c;
  --risk-high: #f39c12;
  --risk-moderate: #f1c40f;
  --risk-low: #27ae60;
  --risk-minimal: #95a5a6;

  /* Backgrounds - Clean Clinical */
  --bg-primary: #f8f9fa;
  --bg-secondary: #ffffff;
  --bg-tertiary: #e9ecef;

  /* Text */
  --text-primary: #2c3e50;
  --text-secondary: #7f8c8d;
  --text-muted: #bdc3c7;

  /* Borders */
  --border-light: #dee2e6;
  --border-medium: #ced4da;

  /* Shadows - Subtle Depth */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);

  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

**Step 2: Create Material-UI theme**

Create `dashboard-web/src/theme/medicalTheme.js`:

```javascript
import { createTheme } from "@mui/material/styles";

export const medicalTheme = createTheme({
  palette: {
    primary: {
      main: "#0066CC",
      light: "#3399FF",
      dark: "#004C99",
    },
    secondary: {
      main: "#00A86B",
      light: "#2ECC71",
    },
    error: {
      main: "#E74C3C",
    },
    warning: {
      main: "#F39C12",
    },
    success: {
      main: "#27AE60",
    },
    background: {
      default: "#F8F9FA",
      paper: "#FFFFFF",
    },
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", system-ui, sans-serif',
    h1: {
      fontSize: "2.5rem",
      fontWeight: 700,
      letterSpacing: "-0.02em",
    },
    h2: {
      fontSize: "2rem",
      fontWeight: 600,
      letterSpacing: "-0.01em",
    },
    h4: {
      fontSize: "1.5rem",
      fontWeight: 600,
    },
    h6: {
      fontSize: "1.125rem",
      fontWeight: 600,
    },
    body1: {
      fontSize: "1rem",
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    "none",
    "0 1px 3px rgba(0,0,0,0.08)",
    "0 4px 12px rgba(0,0,0,0.1)",
    "0 8px 24px rgba(0,0,0,0.12)",
    // ... extend as needed
  ],
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
          transition: "transform 250ms, box-shadow 250ms",
          "&:hover": {
            transform: "translateY(-2px)",
            boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          borderRadius: 8,
        },
      },
    },
  },
});
```

**Step 3: Apply theme globally**

Modify `dashboard-web/src/main.jsx`:

```javascript
import React from "react";
import ReactDOM from "react-dom/client";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import App from "./App.jsx";
import { medicalTheme } from "./theme/medicalTheme.js";
import "./theme/colors.css";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider theme={medicalTheme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
```

**Step 4: Verify theme application**

```bash
cd dashboard-web
npm run dev
```

Expected: Dashboard loads with new medical color scheme and typography

---

## Task 2: Enhanced Patient Risk Card Component

**Files:**

- Modify: `dashboard-web/src/components/PatientCard.jsx`
- Create: `dashboard-web/src/components/RiskBadge.jsx`

**Step 1: Create reusable risk badge**

Create `dashboard-web/src/components/RiskBadge.jsx`:

```javascript
import { Chip } from "@mui/material";
import { Warning, CheckCircle, Error, Info } from "@mui/icons-material";

const RISK_CONFIG = {
  critical: { color: "#E74C3C", icon: Error, label: "Critical Risk" },
  high: { color: "#F39C12", icon: Warning, label: "High Risk" },
  moderate: { color: "#F1C40F", icon: Info, label: "Moderate Risk" },
  low: { color: "#27AE60", icon: CheckCircle, label: "Low Risk" },
  minimal: { color: "#95A5A6", icon: CheckCircle, label: "Minimal Risk" },
};

export default function RiskBadge({ riskLevel, score }) {
  const config = RISK_CONFIG[riskLevel] || RISK_CONFIG.minimal;
  const Icon = config.icon;

  return (
    <Chip
      icon={<Icon />}
      label={`${config.label} (${(score * 100).toFixed(1)}%)`}
      sx={{
        backgroundColor: `${config.color}15`,
        color: config.color,
        fontWeight: 600,
        border: `2px solid ${config.color}`,
        "& .MuiChip-icon": {
          color: config.color,
        },
      }}
    />
  );
}
```

**Step 2: Enhance PatientCard with NLP insights**

Modify `dashboard-web/src/components/PatientCard.jsx` to add NLP features section:

```javascript
// Add after vital signs section
{
  patient.nlp_features && (
    <Box sx={{ mt: 2, p: 2, bgcolor: "grey.50", borderRadius: 2 }}>
      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
        📝 Clinical Notes Insights (NLP)
      </Typography>
      <Grid container spacing={1}>
        <Grid item xs={6}>
          <Typography variant="body2">
            Conditions: {patient.nlp_num_conditions || 0}
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <Typography variant="body2">
            Medications: {patient.nlp_num_medications || 0}
          </Typography>
        </Grid>
        {patient.nlp_has_diabetes === 1 && (
          <Grid item xs={12}>
            <Chip label="Diabetes Mentioned" size="small" color="warning" />
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
```

**Step 3: Verify enhanced card**

```bash
npm run dev
```

Expected: Patient cards show NLP insights and improved risk badges

---

## Task 3: Real-Time Service Health Dashboard

**Files:**

- Modify: `dashboard-web/src/components/HealthStatus.jsx`
- Create: `dashboard-web/src/components/ServiceStatusCard.jsx`

**Step 1: Create animated service status card**

Create `dashboard-web/src/components/ServiceStatusCard.jsx`:

```javascript
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
} from "@mui/material";
import { CheckCircle, Error, HourglassEmpty } from "@mui/icons-material";
import { keyframes } from "@mui/system";

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

export default function ServiceStatusCard({ service }) {
  const isHealthy = service.status === "healthy";
  const statusColor = isHealthy ? "#27AE60" : "#E74C3C";
  const StatusIcon = isHealthy ? CheckCircle : Error;

  return (
    <Card
      sx={{
        position: "relative",
        overflow: "hidden",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          backgroundColor: statusColor,
          animation: !isHealthy ? `${pulse} 2s ease-in-out infinite` : "none",
        },
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6">{service.name}</Typography>
            <Typography variant="caption" color="text.secondary">
              Port: {service.port}
            </Typography>
          </Box>
          <StatusIcon sx={{ fontSize: 40, color: statusColor }} />
        </Box>

        {service.details && (
          <Box sx={{ mt: 2 }}>
            {Object.entries(service.details).map(([key, value]) => (
              <Typography key={key} variant="body2" color="text.secondary">
                {key}: {String(value)}
              </Typography>
            ))}
          </Box>
        )}

        {service.error && (
          <Typography variant="body2" color="error" sx={{ mt: 1 }}>
            ⚠️ {service.error}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
```

**Step 2: Update HealthStatus to use new card**

Modify `dashboard-web/src/components/HealthStatus.jsx`:

```javascript
import ServiceStatusCard from "./ServiceStatusCard";

// Replace ServiceCard component with:
{
  services.map((service) => (
    <Grid item xs={12} md={6} lg={4} key={service.name}>
      <ServiceStatusCard service={service} />
    </Grid>
  ));
}
```

**Step 3: Verify health dashboard**

```bash
npm run dev
```

Expected: Animated service status cards with pulsing indicators for unhealthy services

---

## Task 4: Advanced Risk Analytics Dashboard

**Files:**

- Create: `dashboard-web/src/components/RiskAnalytics.jsx`
- Create: `dashboard-web/src/components/RiskDistributionChart.jsx`
- Modify: `dashboard-web/src/App.jsx` (add route)

**Step 1: Create risk distribution chart**

Create `dashboard-web/src/components/RiskDistributionChart.jsx`:

```javascript
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { Box, Typography } from "@mui/material";

const RISK_COLORS = {
  critical: "#E74C3C",
  high: "#F39C12",
  moderate: "#F1C40F",
  low: "#27AE60",
  minimal: "#95A5A6",
};

export default function RiskDistributionChart({ data }) {
  const chartData = Object.entries(data).map(([level, count]) => ({
    name: level.charAt(0).toUpperCase() + level.slice(1),
    value: count,
    color: RISK_COLORS[level],
  }));

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Risk Distribution
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={100}
            label
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
}
```

**Step 2: Create analytics page**

Create `dashboard-web/src/components/RiskAnalytics.jsx`:

```javascript
import { useState, useEffect } from "react";
import { Grid, Card, CardContent, Typography, Box } from "@mui/material";
import { getPredictionStats, getHighRiskPatients } from "../services/api";
import RiskDistributionChart from "./RiskDistributionChart";

export default function RiskAnalytics() {
  const [stats, setStats] = useState(null);
  const [highRiskPatients, setHighRiskPatients] = useState([]);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const statsData = await getPredictionStats();
      const highRisk = await getHighRiskPatients();
      setStats(statsData);
      setHighRiskPatients(highRisk);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    }
  };

  if (!stats) return <Typography>Loading analytics...</Typography>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Risk Analytics Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <RiskDistributionChart data={stats.risk_distribution} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                High-Risk Patients
              </Typography>
              <Typography variant="h3" color="error">
                {highRiskPatients.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Require immediate attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
```

**Step 3: Add route to App**

Modify `dashboard-web/src/App.jsx`:

```javascript
import RiskAnalytics from "./components/RiskAnalytics";

// Add route
<Route path="/analytics" element={<RiskAnalytics />} />;
```

**Step 4: Verify analytics page**

```bash
npm run dev
```

Navigate to http://localhost:3000/analytics

Expected: Risk distribution chart and high-risk patient count displayed

---

## Task 5: NLP Insights Visualization

**Files:**

- Create: `dashboard-web/src/components/NLPInsights.jsx`
- Create: `dashboard-web/src/components/ConditionCloud.jsx`

**Step 1: Create word cloud for conditions**

Create `dashboard-web/src/components/ConditionCloud.jsx`:

```javascript
import { Box, Chip, Typography } from "@mui/material";

export default function ConditionCloud({ conditions }) {
  const conditionCounts = conditions.reduce((acc, cond) => {
    acc[cond] = (acc[cond] || 0) + 1;
    return acc;
  }, {});

  const sorted = Object.entries(conditionCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 20);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Most Common Conditions (NLP Extracted)
      </Typography>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 2 }}>
        {sorted.map(([condition, count]) => (
          <Chip
            key={condition}
            label={`${condition} (${count})`}
            size={count > 10 ? "medium" : "small"}
            color={count > 20 ? "error" : count > 10 ? "warning" : "default"}
          />
        ))}
      </Box>
    </Box>
  );
}
```

**Step 2: Create NLP insights page**

Create `dashboard-web/src/components/NLPInsights.jsx`:

```javascript
import { useState, useEffect } from "react";
import { Grid, Card, CardContent, Typography } from "@mui/material";
import { getFeatures } from "../services/api";
import ConditionCloud from "./ConditionCloud";

export default function NLPInsights() {
  const [features, setFeatures] = useState([]);

  useEffect(() => {
    loadFeatures();
  }, []);

  const loadFeatures = async () => {
    const data = await getFeatures();
    setFeatures(data);
  };

  const allConditions = features
    .flatMap((f) => f.nlp_conditions || [])
    .filter(Boolean);

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        NLP Insights from Clinical Notes
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <ConditionCloud conditions={allConditions} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
}
```

**Step 3: Verify NLP insights**

```bash
npm run dev
```

Expected: Word cloud showing most common conditions extracted from clinical notes

---

## Task 6: Responsive Navigation Enhancement

**Files:**

- Modify: `dashboard-web/src/App.jsx`
- Create: `dashboard-web/src/components/Sidebar.jsx`

**Step 1: Create sidebar navigation**

Create `dashboard-web/src/components/Sidebar.jsx`:

```javascript
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
} from "@mui/material";
import {
  Dashboard,
  People,
  Analytics,
  HealthAndSafety,
  Psychology,
} from "@mui/icons-material";
import { useNavigate, useLocation } from "react-router-dom";

const MENU_ITEMS = [
  { path: "/", label: "Dashboard", icon: Dashboard },
  { path: "/patients", label: "Patients", icon: People },
  { path: "/analytics", label: "Risk Analytics", icon: Analytics },
  { path: "/health", label: "System Health", icon: HealthAndSafety },
  { path: "/nlp", label: "NLP Insights", icon: Psychology },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 240,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: 240,
          boxSizing: "border-box",
          backgroundColor: "var(--bg-secondary)",
          borderRight: "1px solid var(--border-light)",
        },
      }}
    >
      <List sx={{ pt: 8 }}>
        {MENU_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                selected={isActive}
                onClick={() => navigate(item.path)}
                sx={{
                  borderLeft: isActive
                    ? "4px solid var(--medical-primary)"
                    : "4px solid transparent",
                  backgroundColor: isActive
                    ? "var(--medical-primary)10"
                    : "transparent",
                }}
              >
                <ListItemIcon>
                  <Icon color={isActive ? "primary" : "inherit"} />
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Drawer>
  );
}
```

**Step 2: Integrate sidebar into App**

Modify `dashboard-web/src/App.jsx`:

```javascript
import Sidebar from "./components/Sidebar";

// Wrap routes with sidebar
<Box sx={{ display: "flex" }}>
  <Sidebar />
  <Box component="main" sx={{ flexGrow: 1, p: 3, ml: "240px" }}>
    <Routes>{/* existing routes */}</Routes>
  </Box>
</Box>;
```

**Step 3: Verify navigation**

```bash
npm run dev
```

Expected: Persistent sidebar with active state highlighting

---

## Task 7: Performance Optimization

**Files:**

- Modify: `dashboard-web/src/components/PatientList.jsx`
- Modify: `dashboard-web/src/services/api.js`

**Step 1: Add pagination to patient list**

Modify `dashboard-web/src/components/PatientList.jsx`:

```javascript
import { Pagination } from "@mui/material";

const PATIENTS_PER_PAGE = 12;

function PatientList() {
  const [page, setPage] = useState(1);
  const [patients, setPatients] = useState([]);

  const paginatedPatients = patients.slice(
    (page - 1) * PATIENTS_PER_PAGE,
    page * PATIENTS_PER_PAGE
  );

  const totalPages = Math.ceil(patients.length / PATIENTS_PER_PAGE);

  return (
    <>
      <Grid container spacing={3}>
        {paginatedPatients.map((patient) => (
          <Grid item xs={12} md={6} lg={4} key={patient.patient_id}>
            <PatientCard patient={patient} />
          </Grid>
        ))}
      </Grid>

      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <Pagination
          count={totalPages}
          page={page}
          onChange={(e, value) => setPage(value)}
          color="primary"
          size="large"
        />
      </Box>
    </>
  );
}
```

**Step 2: Add caching to API calls**

Modify `dashboard-web/src/services/api.js`:

```javascript
const cache = new Map();
const CACHE_TTL = 60000; // 1 minute

export const getFeatures = async () => {
  const cacheKey = "features";
  const cached = cache.get(cacheKey);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const response = await api.get("/features/features");
  cache.set(cacheKey, { data: response.data, timestamp: Date.now() });
  return response.data;
};
```

**Step 3: Verify performance**

```bash
npm run dev
```

Expected: Faster page loads with pagination and caching

---

## Task 8: Final Verification and Documentation

**Files:**

- Create: `dashboard-web/README_FEATURES.md`
- Modify: `README.md`

**Step 1: Test all features**

```bash
# Run dashboard
cd dashboard-web
npm run dev

# Test checklist:
# ✓ Dashboard loads with medical theme
# ✓ Health Status shows all 5 services
# ✓ Patient List displays with pagination
# ✓ Risk Analytics shows charts
# ✓ NLP Insights displays condition cloud
# ✓ Navigation sidebar works
# ✓ All pages responsive on mobile
```

**Step 2: Create feature documentation**

Create `dashboard-web/README_FEATURES.md`:

```markdown
# HealthFlow Dashboard Features

## Pages

### Dashboard (/)

- System overview with key metrics
- Quick stats cards
- Recent patient activity

### Patients (/patients)

- Paginated patient list (12 per page)
- Enhanced patient cards with NLP insights
- Risk level badges with color coding

### Risk Analytics (/analytics)

- Risk distribution pie chart
- High-risk patient count
- Trend analysis

### System Health (/health)

- Real-time service status (5 microservices)
- Animated health indicators
- Service details and error messages

### NLP Insights (/nlp)

- Condition word cloud from clinical notes
- Most common medications
- Symptom frequency analysis

## Design System

### Colors

- Primary: Clinical Blue (#0066CC)
- Accent: Vital Green (#00A86B)
- Risk Levels: Critical (Red), High (Orange), Moderate (Yellow), Low (Green)

### Typography

- Font: Inter (system fallback)
- Headings: 600-700 weight
- Body: 400 weight, 1.6 line-height

### Components

- Cards: Elevated with hover effects
- Chips: Rounded, bold labels
- Charts: Recharts with medical color palette
```

**Step 3: Update main README**

Add to `README.md`:

```markdown
## 🎨 Dashboard Features

The HealthFlow dashboard provides:

- **Real-Time Monitoring**: Live health status of all 5 microservices
- **Patient Analytics**: Comprehensive patient list with risk predictions
- **NLP Insights**: BioBERT-extracted conditions from 8,722 clinical notes
- **Risk Analytics**: Distribution charts and high-risk patient identification
- **Medical Design**: Clinical color palette with accessibility focus

Access: http://localhost:3000
```

**Step 4: Final verification**

```bash
# Build for production
npm run build

# Check bundle size
npm run preview
```

Expected: Production build succeeds, bundle < 500KB gzipped

---

## Completion Checklist

- [ ] Medical theme applied globally
- [ ] All 5 pages functional and styled
- [ ] Navigation sidebar with active states
- [ ] Patient cards show NLP insights
- [ ] Health status with animated indicators
- [ ] Risk analytics with charts
- [ ] NLP insights visualization
- [ ] Pagination on patient list
- [ ] API caching implemented
- [ ] Documentation complete
- [ ] Production build successful
- [ ] Mobile responsive verified

## Next Steps

After implementation:

1. Deploy dashboard to production
2. Add user authentication
3. Implement real-time WebSocket updates
4. Add export functionality (PDF reports)
5. Create admin panel for model management
