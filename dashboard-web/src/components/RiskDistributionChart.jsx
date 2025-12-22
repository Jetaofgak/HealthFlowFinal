import { Box, Typography, useTheme } from '@mui/material';
import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Legend,
    Tooltip,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
} from 'recharts';
import { RISK_COLORS } from '../theme/medicalTheme';

const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        return (
            <Box
                sx={{
                    backgroundColor: 'white',
                    p: 1.5,
                    borderRadius: 2,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                    border: '1px solid',
                    borderColor: 'divider',
                }}
            >
                <Typography variant="subtitle2" fontWeight={600}>
                    {data.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Patients: <strong>{data.value}</strong>
                </Typography>
                {data.percentage && (
                    <Typography variant="body2" color="text.secondary">
                        Percentage: <strong>{data.percentage}%</strong>
                    </Typography>
                )}
            </Box>
        );
    }
    return null;
};

export default function RiskDistributionChart({ data, variant = 'pie' }) {
    const theme = useTheme();

    const chartData = Object.entries(data || {}).map(([level, count]) => {
        const total = Object.values(data || {}).reduce((a, b) => a + b, 0);
        return {
            name: level.charAt(0).toUpperCase() + level.slice(1),
            value: count,
            color: RISK_COLORS[level] || '#95A5A6',
            percentage: total > 0 ? ((count / total) * 100).toFixed(1) : 0,
        };
    });

    if (chartData.length === 0) {
        return (
            <Box
                sx={{
                    height: 300,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'grey.50',
                    borderRadius: 2,
                }}
            >
                <Typography color="text.secondary">No risk data available</Typography>
            </Box>
        );
    }

    if (variant === 'bar') {
        return (
            <Box sx={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                    <BarChart data={chartData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                        <XAxis type="number" />
                        <YAxis dataKey="name" type="category" width={80} />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </Box>
        );
    }

    return (
        <Box sx={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
                <PieChart>
                    <Pie
                        data={chartData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        innerRadius={60}
                        paddingAngle={2}
                        label={({ name, percentage }) => `${name}: ${percentage}%`}
                        labelLine={{ stroke: theme.palette.text.secondary, strokeWidth: 1 }}
                    >
                        {chartData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={entry.color}
                                stroke="white"
                                strokeWidth={2}
                            />
                        ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                    <Legend
                        verticalAlign="bottom"
                        height={36}
                        formatter={(value) => (
                            <span style={{ color: theme.palette.text.primary, fontWeight: 500 }}>
                                {value}
                            </span>
                        )}
                    />
                </PieChart>
            </ResponsiveContainer>
        </Box>
    );
}

// Simple horizontal bar for inline display
export function RiskBar({ distribution }) {
    const total = Object.values(distribution || {}).reduce((a, b) => a + b, 0);
    if (total === 0) return null;

    const segments = Object.entries(distribution || {})
        .filter(([_, count]) => count > 0)
        .map(([level, count]) => ({
            level,
            percentage: (count / total) * 100,
            color: RISK_COLORS[level] || '#95A5A6',
        }));

    return (
        <Box sx={{ display: 'flex', height: 8, borderRadius: 4, overflow: 'hidden' }}>
            {segments.map((segment, index) => (
                <Box
                    key={segment.level}
                    sx={{
                        width: `${segment.percentage}%`,
                        backgroundColor: segment.color,
                        transition: 'width 0.5s ease',
                    }}
                />
            ))}
        </Box>
    );
}
