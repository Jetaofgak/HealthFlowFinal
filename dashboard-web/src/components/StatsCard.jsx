import { Card, CardContent, Typography, Box } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

export default function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'primary',
  trend = null,
  trendValue = null,
}) {
  const colorMap = {
    primary: {
      gradient: 'linear-gradient(135deg, #0066CC 0%, #004C99 100%)',
      light: 'rgba(0, 102, 204, 0.1)',
      main: '#0066CC',
    },
    success: {
      gradient: 'linear-gradient(135deg, #27AE60 0%, #1E8449 100%)',
      light: 'rgba(39, 174, 96, 0.1)',
      main: '#27AE60',
    },
    warning: {
      gradient: 'linear-gradient(135deg, #F39C12 0%, #D68910 100%)',
      light: 'rgba(243, 156, 18, 0.1)',
      main: '#F39C12',
    },
    error: {
      gradient: 'linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)',
      light: 'rgba(231, 76, 60, 0.1)',
      main: '#E74C3C',
    },
    info: {
      gradient: 'linear-gradient(135deg, #3498DB 0%, #2980B9 100%)',
      light: 'rgba(52, 152, 219, 0.1)',
      main: '#3498DB',
    },
  };

  const colors = colorMap[color] || colorMap.primary;

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : TrendingFlat;
  const trendColor = trend === 'up' ? '#27AE60' : trend === 'down' ? '#E74C3C' : '#95A5A6';

  return (
    <Card
      sx={{
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        '&::after': {
          content: '""',
          position: 'absolute',
          top: -50,
          right: -50,
          width: 150,
          height: 150,
          borderRadius: '50%',
          background: colors.light,
          opacity: 0.5,
        },
      }}
    >
      <CardContent sx={{ position: 'relative', zIndex: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontSize: '0.75rem',
                mb: 1,
              }}
            >
              {title}
            </Typography>
            <Typography
              variant="h4"
              fontWeight={700}
              sx={{
                color: colors.main,
                lineHeight: 1.2,
              }}
            >
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          {Icon && (
            <Box
              sx={{
                width: 56,
                height: 56,
                borderRadius: 3,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: colors.gradient,
                boxShadow: `0 8px 24px ${colors.main}40`,
              }}
            >
              <Icon sx={{ fontSize: 28, color: 'white' }} />
            </Box>
          )}
        </Box>

        {trend && (
          <Box
            display="flex"
            alignItems="center"
            gap={0.5}
            sx={{
              mt: 2,
              pt: 2,
              borderTop: '1px solid',
              borderColor: 'divider',
            }}
          >
            <TrendIcon sx={{ fontSize: 18, color: trendColor }} />
            <Typography
              variant="body2"
              sx={{ color: trendColor, fontWeight: 600 }}
            >
              {trendValue}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              vs last period
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
