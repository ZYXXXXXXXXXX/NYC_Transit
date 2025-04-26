import React, { useEffect, useState } from 'react';
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
import { scheduler } from 'timers/promises';
import ElevatorIcon from '@mui/icons-material/Elevator';
import BuildIcon from '@mui/icons-material/Build'; 
import LinearProgress from '@mui/material/LinearProgress';
import { useTranslation } from 'react-i18next';


interface StationRoute {
  id: string;
  color: string;
  schedule: string[];
  trip_headsign?: string;
}

interface RawStationInfo {
  id: string;
  name: string;
  accessibility: string;
  routes: { id: string; color: string }[];
}

interface DetailStationInfo {
  id: string;
  name: string;
  accessibility: string;
  routes: { id: string; color: string }[];
}

interface EquipmentInfo {
  equipment_no: string;
  equipment_type: string;
  is_active: boolean;
  serving: string;
}

interface EnrichedStationInfo extends Omit<RawStationInfo, 'routes'> {
  routes: StationRoute[];
}

interface AccessStationInfo extends Omit<DetailStationInfo, 'routes'> {
  accessibility: string;
  equipment: EquipmentInfo[];
  routes: StationRoute[];
}

interface Props {
  open: boolean;
  onClose: () => void;
  station: RawStationInfo | null;
}

export default function StationInfoDialog({ open, onClose, station }: Props) {
  const [enrichedStation, setEnrichedStation] = useState<EnrichedStationInfo | null>(null);
  const [accessStation, setAccessStation] = useState<AccessStationInfo | null>(null);
  const { t } = useTranslation();

  useEffect(() => {
    if (station && open) {
      enrichWithSchedules(station).then(setEnrichedStation);
      accessibility(station).then(setAccessStation)
    }
  }, [station, open]);

  async function enrichWithSchedules(station: RawStationInfo): Promise<EnrichedStationInfo> {
    const routesWithSchedule = await Promise.all(
      station.routes.map(async route => {
        // 请求两个方向的 schedule
        const stationIdN = station.id.replace(/S$/, 'N');
        const stationIdS = station.id.replace(/N$/, 'S');
  
        const [resN, resS] = await Promise.all([
          fetch(`http://127.0.0.1:5000/api/stations/${stationIdN}/routes/${route.id}/schedule`),
          fetch(`http://127.0.0.1:5000/api/stations/${stationIdS}/routes/${route.id}/schedule`)
        ]);
  
        const dataN = await resN.json();
        const dataS = await resS.json();
  
        return {
          ...route,
          northbound: {
            headsign: dataN.schedule[0]?.trip_headsign || 'Northbound',
            schedule: dataN.schedule.map(s => s.departure_time)
          },
          southbound: {
            headsign: dataS.schedule[0]?.trip_headsign || 'Southbound',
            schedule: dataS.schedule.map(s => s.departure_time)
          }
        };
      })
    );
  
    return { ...station, routes: routesWithSchedule };
  }

  async function accessibility(station: DetailStationInfo): Promise<AccessStationInfo> {
    const res = await fetch(`http://127.0.0.1:5000/api/stations/${station.id}/details`);
    const data = await res.json();
  
    return {
      ...station,
      accessibility: data.accessibility?.has_accessibility ? "Yes" : "No",
      equipment: data.accessibility?.equipment || [],
      routes: station.routes.map(r => ({ ...r, schedule: [] }))  // 保持结构一致
    };
  }

  if (!enrichedStation) return null;

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{enrichedStation.name}</DialogTitle>
      <DialogContent>
        <Typography variant="subtitle1" gutterBottom>
          {t('line')}:
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {enrichedStation.routes.map(route => (
            <Chip
              key={route.id}
              label={route.id}
              sx={{
                backgroundColor: `#${route.color}`,
                color: '#fff',
                fontWeight: 'bold'
              }}
            />
          ))}
        </Stack>

        {accessStation && (
          <>
            {/* 显示是否支持辅助功能 */}
            <Typography variant="subtitle1" sx={{ mt: 2 }}>
            {t('accessibility')}: {accessStation.accessibility === 'Yes' ? t('yes') : t('no')}
            </Typography>

            {/* 若有设备则渲染设备列表，否则显示“无设备”提示 */}
            {accessStation.equipment.length > 0 ? (
              <>
                <Typography variant="subtitle2" sx={{ mt: 2 }}>
                  {t('accessibilityequi')}
                  </Typography>
                {accessStation.equipment.map((item, index) => (
                  <Stack direction="row" alignItems="center" spacing={1} key={index} sx={{ ml: 2 }}>
                    {item.equipment_type === "EL" ? (
                      <ElevatorIcon color={item.is_active ? "primary" : "disabled"} />
                    ) : (
                      <BuildIcon color={item.is_active ? "primary" : "disabled"} />
                    )}
                    <Typography variant="body2">
                      {item.equipment_type} ({item.equipment_no}) {" "}
                      {item.is_active ? "Operational" : "Out of Service"}
                      <br />
                      <i>{item.serving}</i>
                    </Typography>
                  </Stack>
                ))}
              </>
            ) : (
              <Typography variant="body2" sx={{ ml: 2, mt: 1, fontStyle: 'italic' }}>
                No accessibility equipment available.
              </Typography>
            )}
          </>
        )}

        <Typography variant="subtitle1" sx={{ mt: 2 }}>
          {t('schedule')}:
        </Typography>

        {enrichedStation.routes.map(route => (
          <div key={route.id} style={{ marginBottom: '1rem' }}>
            {/* Line chip */}
            <Chip
              label={route.id}
              sx={{
                backgroundColor: `#${route.color}`,
                color: '#fff',
                fontWeight: 'bold',
                marginBottom: '0.25rem'
              }}
            />

            {/* Direction display */}
            {route.trip_headsign && (
              <Typography variant="caption" color="textSecondary" sx={{ ml: 1 }}>
                → {route.trip_headsign}
              </Typography>
            )}

            {/* Schedule display */}
            {['northbound', 'southbound'].map((dirKey) => {
            const dir = route[dirKey as 'northbound' | 'southbound'];
            return dir?.schedule?.length ? (
              <div key={dirKey}>
                <Typography variant="caption" color="textSecondary" sx={{ ml: 1 }}>
                  → {dir.headsign}
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {dir.schedule.slice(0, 5).join(', ')}
                </Typography>
                <NextTrainProgress nextTime={dir.schedule[0]} />
              </div>
            ) : (
              <Typography key={dirKey} variant="body2" sx={{ ml: 1 }}>
                No {dirKey} departures
              </Typography>
            );
          })}
          </div>
        ))}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('close')}</Button>
      </DialogActions>
    </Dialog>
  );
}

function NextTrainProgress({ nextTime }: { nextTime: string }) {
  const { t } = useTranslation();
  const [progress, setProgress] = useState(0);
  const [minutesLeft, setMinutesLeft] = useState<number | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const [hour, minute, second] = nextTime.split(':').map(Number);
      const nextTrain = new Date();
      nextTrain.setHours(hour, minute, second, 0);

      const diffMs = nextTrain.getTime() - now.getTime();
      const totalMs = 10 * 60 * 1000;
      const percent = Math.min(100, Math.max(0, 100 - (diffMs / totalMs) * 100));
      setProgress(percent);
      setMinutesLeft(Math.ceil(diffMs / 60000));
    }, 1000);

    return () => clearInterval(interval);
  }, [nextTime]);

  return (
    <div>
      <Typography variant="caption" color="textSecondary">
        {minutesLeft !== null && minutesLeft >= 0
          ? t('nextTrain', { min: minutesLeft })
          : t('departed')}
      </Typography>
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{ height: 8, borderRadius: 5, my: 1 }}
      />
    </div>
  );
}