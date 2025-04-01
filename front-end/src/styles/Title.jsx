import { Typography } from '@mui/material';

export default function Title({ children, level = 'h4', color = 'primary', ...props }) {
  return (
    <Typography
      variant={level}
      sx={{
        color: (theme) => theme.palette[color].main,
        fontWeight: 700,
        lineHeight: 1.2,
      }}
      {...props}
    >
      {children}
    </Typography>
  );
}