import type { Sensor } from '../../api/client';
export default function TelemetryStream({ sensors }: { sensors: Sensor[] }) {
  return <div className="telemetry">{sensors.map(s => <div key={s.id}>
    <span className="live-dot" />
    <div><b>{s.name}</b><small>{s.sensor_type} · {s.latest ? new Date(s.latest.timestamp).toLocaleTimeString() : 'No reading'} · {s.transmission_mode ?? 'CELLULAR_4G'}</small></div>
    <strong>{s.latest?.rainfall_mm_h ?? '—'}<small> mm/h</small></strong>
  </div>)}</div>;
}
