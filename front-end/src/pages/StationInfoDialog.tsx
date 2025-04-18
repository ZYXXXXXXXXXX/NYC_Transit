// components/StationInfoDialog.tsx
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Chip,
  Stack,
} from '@mui/material';

interface StationInfo {
  id: string;
  name: string;
  accessibility: string;
  routes: string[];
  color: string;
}

interface Props {
  open: boolean;
  onClose: () => void;
  station: StationInfo | null;
}

export default function StationInfoDialog({ open, onClose, station }: Props) {
  if (!station) return null;

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{station.name}</DialogTitle>
      <DialogContent>
        <Typography variant="subtitle1" gutterBottom>
          Line：
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {station.routes.map(route => (
            <Chip key={route.id}
            label={route.id}
            sx={{
              backgroundColor: `#${route.color}`,
              color: '#fff',
              fontWeight: 'bold'
            }} />
          ))}
        </Stack>
        <Typography variant="subtitle1" gutterBottom>
          Accessibility：{station.accessibility || 'None'}
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}