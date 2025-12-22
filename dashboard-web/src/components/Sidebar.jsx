import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    Drawer,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    ListItemButton,
    Box,
    Typography,
    Avatar,
    Divider,
    IconButton,
    useMediaQuery,
    useTheme,
} from '@mui/material';
import {
    Dashboard,
    People,
    Analytics,
    HealthAndSafety,
    Psychology,
    Science,
    Menu as MenuIcon,
    ChevronLeft,
    LocalHospital,
    Gavel,
} from '@mui/icons-material';

const SIDEBAR_WIDTH = 280;

const MENU_ITEMS = [
    { path: '/', label: 'Dashboard', icon: Dashboard, description: 'Overview & Stats' },
    { path: '/patients', label: 'Patients', icon: People, description: 'Patient Records' },
    { path: '/analytics', label: 'Risk Analytics', icon: Analytics, description: 'Risk Analysis' },
    { path: '/audit-fairness', label: 'Audit Fairness', icon: Gavel, description: 'AI Bias & Fairness' },
    { path: '/nlp', label: 'NLP Insights', icon: Psychology, description: 'Clinical Notes AI' },
    { path: '/pipeline', label: 'Data Pipeline', icon: Science, description: 'Process Data' },
    { path: '/health', label: 'System Health', icon: HealthAndSafety, description: 'Service Status' },
];

export default function Sidebar({ open, onToggle }) {
    const navigate = useNavigate();
    const location = useLocation();
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));

    const handleNavigation = (path) => {
        navigate(path);
        if (isMobile) {
            onToggle();
        }
    };

    const drawerContent = (
        <Box
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                background: 'linear-gradient(180deg, #FFFFFF 0%, #F8F9FA 100%)',
            }}
        >
            {/* Logo Section */}
            <Box
                sx={{
                    p: 3,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                }}
            >
                <Avatar
                    sx={{
                        width: 48,
                        height: 48,
                        background: 'linear-gradient(135deg, #0066CC 0%, #004C99 100%)',
                        boxShadow: '0 4px 14px rgba(0, 102, 204, 0.4)',
                    }}
                >
                    <LocalHospital />
                </Avatar>
                <Box>
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
                    <Typography variant="caption" color="text.secondary">
                        Analytics Platform
                    </Typography>
                </Box>
                {isMobile && (
                    <IconButton onClick={onToggle} sx={{ ml: 'auto' }}>
                        <ChevronLeft />
                    </IconButton>
                )}
            </Box>

            {/* Navigation Items */}
            <List sx={{ flex: 1, pt: 2, px: 1 }}>
                {MENU_ITEMS.map((item, index) => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.path;

                    return (
                        <ListItem
                            key={item.path}
                            disablePadding
                            sx={{
                                mb: 0.5,
                                animation: 'slideInLeft 0.3s ease-out forwards',
                                animationDelay: `${index * 50}ms`,
                                opacity: 0,
                            }}
                        >
                            <ListItemButton
                                selected={isActive}
                                onClick={() => handleNavigation(item.path)}
                                sx={{
                                    borderRadius: 2,
                                    py: 1.5,
                                    px: 2,
                                    transition: 'all 0.2s ease',
                                    position: 'relative',
                                    overflow: 'hidden',
                                    '&::before': {
                                        content: '""',
                                        position: 'absolute',
                                        left: 0,
                                        top: 0,
                                        bottom: 0,
                                        width: 4,
                                        borderRadius: '0 4px 4px 0',
                                        backgroundColor: 'primary.main',
                                        transform: isActive ? 'scaleY(1)' : 'scaleY(0)',
                                        transition: 'transform 0.2s ease',
                                    },
                                    '&.Mui-selected': {
                                        backgroundColor: 'rgba(0, 102, 204, 0.08)',
                                    },
                                    '&:hover': {
                                        backgroundColor: isActive
                                            ? 'rgba(0, 102, 204, 0.12)'
                                            : 'rgba(0, 0, 0, 0.04)',
                                        '&::before': {
                                            transform: 'scaleY(1)',
                                        },
                                    },
                                }}
                            >
                                <ListItemIcon
                                    sx={{
                                        minWidth: 44,
                                        color: isActive ? 'primary.main' : 'text.secondary',
                                        transition: 'color 0.2s ease',
                                    }}
                                >
                                    <Icon />
                                </ListItemIcon>
                                <ListItemText
                                    primary={item.label}
                                    secondary={item.description}
                                    primaryTypographyProps={{
                                        fontWeight: isActive ? 600 : 500,
                                        color: isActive ? 'primary.main' : 'text.primary',
                                        fontSize: '0.95rem',
                                    }}
                                    secondaryTypographyProps={{
                                        fontSize: '0.75rem',
                                        mt: 0.25,
                                    }}
                                />
                            </ListItemButton>
                        </ListItem>
                    );
                })}
            </List>

            {/* Footer */}
            <Divider />
            <Box sx={{ p: 2 }}>
                <Box
                    sx={{
                        p: 2,
                        borderRadius: 2,
                        background: 'linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(0, 168, 107, 0.1) 100%)',
                        border: '1px solid rgba(0, 102, 204, 0.2)',
                    }}
                >
                    <Typography variant="caption" color="text.secondary" display="block">
                        Model Performance
                    </Typography>
                    <Typography variant="h6" color="primary" fontWeight={600}>
                        88.27% AUC
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        XGBoost + BioBERT
                    </Typography>
                </Box>
            </Box>
        </Box>
    );

    if (isMobile) {
        return (
            <Drawer
                variant="temporary"
                open={open}
                onClose={onToggle}
                ModalProps={{ keepMounted: true }}
                sx={{
                    '& .MuiDrawer-paper': {
                        width: SIDEBAR_WIDTH,
                        boxSizing: 'border-box',
                    },
                }}
            >
                {drawerContent}
            </Drawer>
        );
    }

    return (
        <Drawer
            variant="permanent"
            sx={{
                width: SIDEBAR_WIDTH,
                flexShrink: 0,
                '& .MuiDrawer-paper': {
                    width: SIDEBAR_WIDTH,
                    boxSizing: 'border-box',
                    borderRight: '1px solid',
                    borderColor: 'divider',
                },
            }}
        >
            {drawerContent}
        </Drawer>
    );
}

export { SIDEBAR_WIDTH };
