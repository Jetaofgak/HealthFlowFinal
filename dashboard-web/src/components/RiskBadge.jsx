import { Chip, Box } from '@mui/material';
import {
    Warning,
    CheckCircle,
    Error,
    Info,
    PriorityHigh
} from '@mui/icons-material';

const RISK_CONFIG = {
    critical: {
        color: '#E74C3C',
        bgColor: 'rgba(231, 76, 60, 0.12)',
        icon: Error,
        label: 'Critical'
    },
    high: {
        color: '#F39C12',
        bgColor: 'rgba(243, 156, 18, 0.12)',
        icon: Warning,
        label: 'High'
    },
    moderate: {
        color: '#D4AC0D',
        bgColor: 'rgba(241, 196, 15, 0.12)',
        icon: Info,
        label: 'Moderate'
    },
    low: {
        color: '#27AE60',
        bgColor: 'rgba(39, 174, 96, 0.12)',
        icon: CheckCircle,
        label: 'Low'
    },
    minimal: {
        color: '#95A5A6',
        bgColor: 'rgba(149, 165, 166, 0.12)',
        icon: CheckCircle,
        label: 'Minimal'
    },
};

export function getRiskLevel(score) {
    if (score >= 0.8) return 'critical';
    if (score >= 0.6) return 'high';
    if (score >= 0.4) return 'moderate';
    if (score >= 0.2) return 'low';
    return 'minimal';
}

export function getRiskConfig(riskLevel) {
    return RISK_CONFIG[riskLevel] || RISK_CONFIG.minimal;
}

export default function RiskBadge({ riskLevel, score, size = 'medium', showScore = true }) {
    const level = riskLevel || getRiskLevel(score || 0);
    const config = RISK_CONFIG[level] || RISK_CONFIG.minimal;
    const Icon = config.icon;

    const displayLabel = showScore && score !== undefined
        ? `${config.label} (${(score * 100).toFixed(1)}%)`
        : config.label;

    return (
        <Chip
            icon={<Icon />}
            label={displayLabel}
            size={size}
            sx={{
                backgroundColor: config.bgColor,
                color: config.color,
                fontWeight: 600,
                border: `1.5px solid ${config.color}`,
                borderRadius: '20px',
                '& .MuiChip-icon': {
                    color: config.color,
                },
                '& .MuiChip-label': {
                    px: 1,
                },
                transition: 'all 0.2s ease',
                '&:hover': {
                    transform: 'scale(1.02)',
                    boxShadow: `0 4px 12px ${config.bgColor}`,
                },
            }}
        />
    );
}

// Simple dot indicator for compact spaces
export function RiskDot({ score, size = 12 }) {
    const level = getRiskLevel(score || 0);
    const config = RISK_CONFIG[level];

    return (
        <Box
            sx={{
                width: size,
                height: size,
                borderRadius: '50%',
                backgroundColor: config.color,
                boxShadow: `0 0 8px ${config.color}80`,
                animation: level === 'critical' ? 'pulse 2s ease-in-out infinite' : 'none',
            }}
        />
    );
}
