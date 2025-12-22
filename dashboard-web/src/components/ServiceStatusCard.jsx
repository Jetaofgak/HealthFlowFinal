import { Card, CardContent, Typography, Box, LinearProgress, Chip } from '@mui/material';
import { CheckCircle, Error, HourglassEmpty, Refresh } from '@mui/icons-material';
import { keyframes } from '@mui/system';

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const rotate = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

const SERVICE_ICONS = {
    'DeID': '🔐',
    'Featurizer': '⚙️',
    'ML-Predictor': '🧠',
    'ScoreAPI': '📊',
    'API Gateway': '🌐',
};

export default function ServiceStatusCard({ service, loading = false }) {
    const isHealthy = service.status === 'healthy';
    const isPending = loading || service.status === 'pending';

    const statusColor = isPending ? '#3498DB' : (isHealthy ? '#27AE60' : '#E74C3C');
    const StatusIcon = isPending ? HourglassEmpty : (isHealthy ? CheckCircle : Error);
    const statusLabel = isPending ? 'Checking...' : (isHealthy ? 'Healthy' : 'Unhealthy');

    return (
        <Card
            sx={{
                position: 'relative',
                overflow: 'hidden',
                height: '100%',
                transition: 'all 0.3s ease',
                '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 4,
                    background: isPending
                        ? 'linear-gradient(90deg, transparent, #3498DB, transparent)'
                        : `linear-gradient(90deg, ${statusColor}, ${statusColor}80)`,
                    animation: !isHealthy && !isPending ? `${pulse} 2s ease-in-out infinite` : 'none',
                },
                '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: `0 12px 32px ${statusColor}20`,
                },
            }}
        >
            {isPending && (
                <LinearProgress
                    sx={{
                        position: 'absolute',
                        top: 4,
                        left: 0,
                        right: 0,
                        height: 2,
                    }}
                />
            )}

            <CardContent sx={{ pt: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box display="flex" alignItems="center" gap={1.5}>
                        <Box
                            sx={{
                                width: 48,
                                height: 48,
                                borderRadius: 2,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.5rem',
                                background: `${statusColor}15`,
                                border: `1px solid ${statusColor}30`,
                            }}
                        >
                            {SERVICE_ICONS[service.name] || '🔧'}
                        </Box>
                        <Box>
                            <Typography variant="h6" fontWeight={600}>
                                {service.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                Port: {service.port}
                            </Typography>
                        </Box>
                    </Box>

                    <Chip
                        icon={
                            <StatusIcon
                                sx={{
                                    fontSize: 18,
                                    animation: isPending ? `${rotate} 2s linear infinite` : 'none',
                                }}
                            />
                        }
                        label={statusLabel}
                        size="small"
                        sx={{
                            backgroundColor: `${statusColor}15`,
                            color: statusColor,
                            fontWeight: 600,
                            border: `1px solid ${statusColor}30`,
                            '& .MuiChip-icon': {
                                color: statusColor,
                            },
                        }}
                    />
                </Box>

                {service.details && (
                    <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                        {Object.entries(service.details).map(([key, value]) => (
                            <Box
                                key={key}
                                display="flex"
                                justifyContent="space-between"
                                alignItems="center"
                                sx={{ py: 0.5 }}
                            >
                                <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                                    {key.replace(/_/g, ' ')}
                                </Typography>
                                <Typography variant="body2" fontWeight={500}>
                                    {typeof value === 'boolean' ? (value ? '✓' : '✗') : String(value)}
                                </Typography>
                            </Box>
                        ))}
                    </Box>
                )}

                {service.error && (
                    <Box
                        sx={{
                            mt: 2,
                            p: 1.5,
                            borderRadius: 1.5,
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            border: '1px solid rgba(231, 76, 60, 0.2)',
                        }}
                    >
                        <Typography variant="body2" color="error" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            ⚠️ {service.error}
                        </Typography>
                    </Box>
                )}
            </CardContent>
        </Card>
    );
}
