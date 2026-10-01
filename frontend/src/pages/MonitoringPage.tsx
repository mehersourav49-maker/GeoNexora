import { useEffect, useState } from 'react';
import { api, type Sensor } from '../api/client';
import TelemetryStream from '../components/dashboard/TelemetryStream';

type BackhaulResult = { simulation: boolean; cellular_4g_failed: boolean; changed_sensors: number; fallback_mode: string; telemetry_interval_seconds: number; message: string };
export default function MonitoringPage() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [failed, setFailed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [online, setOnline] = useState(navigator.onLine);
  const [swReady, setSwReady] = useState(false);
  const [queued, setQueued] = useState(0);
  useEffect(() => {
    const refresh = () => api.get<Sensor[]>('/api/monitoring/sensors').then(r => { setSensors(r.data); setFailed(r.data.some(sensor => sensor.transmission_mode === 'LORA_MESH_865MHZ')); }).catch(() => setMessage('Backend unavailable; last locally cached telemetry may be stale.'));
    const onOnline = () => { setOnline(true); navigator.serviceWorker?.controller?.postMessage({type:'FLUSH_OFFLINE_QUEUE'}); }; const onOffline = () => setOnline(false);
    refresh(); const id = window.setInterval(refresh, 15000);
    if ('serviceWorker' in navigator) { navigator.serviceWorker.ready.then(reg => { setSwReady(true); (reg.active ?? navigator.serviceWorker.controller)?.postMessage({type:'GET_OFFLINE_QUEUE_STATUS'}); }).catch(() => setSwReady(false)); }
    const onWorkerMessage = (event: MessageEvent<{type?:string;count?:number}>) => { if (event.data?.type === 'OFFLINE_QUEUE_STATUS') setQueued(event.data.count ?? 0); };
    navigator.serviceWorker?.addEventListener('message', onWorkerMessage);
    window.addEventListener('online', onOnline); window.addEventListener('offline', onOffline);
    return () => { window.clearInterval(id); window.removeEventListener('online', onOnline); window.removeEventListener('offline', onOffline); navigator.serviceWorker?.removeEventListener('message', onWorkerMessage); };
  }, []);
  const simulate = async () => {
    setBusy(true); setMessage('');
    try { const { data } = await api.post<BackhaulResult>(`/api/v1/monitoring/simulate-backhaul-failure?failed=${!failed}`); setFailed(data.cellular_4g_failed); setMessage(`${data.message} ${data.changed_sensors} sensor(s) changed; nominal interval ${data.telemetry_interval_seconds}s.`); const result = await api.get<Sensor[]>('/api/monitoring/sensors'); setSensors(result.data); setFailed(result.data.some(sensor => sensor.transmission_mode === 'LORA_MESH_865MHZ')); }
    catch { setMessage('Could not update simulated backhaul state. Check backend connectivity.'); }
    finally { setBusy(false); }
  };
  return <div>
    <div className="page-head"><div><span className="eyebrow">LIVE IOT</span><h1>Sensor Fleet</h1><p>Current telemetry and simulated backhaul failover state.</p></div></div>
    <section className="panel" style={{ marginBottom: 18 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <div><span className="eyebrow">NETWORK RESILIENCE</span><h2 style={{ margin: '8px 0' }}>Backhaul Resiliency Matrix</h2><p style={{ margin: 0 }}>Mode changes are a software simulation; this does not control physical radio hardware.</p></div>
        <button className="primary" disabled={busy || sensors.length === 0} onClick={simulate}>{busy ? 'Updating…' : failed ? 'Restore 4G (simulation)' : 'Simulate 4G failure'}</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(190px,1fr))', gap: 12, marginTop: 18 }}>
        <StatusCard title="CELLULAR 4G" value={failed ? 'FAILED · SIMULATED' : 'AVAILABLE'} tone={failed ? '#c2413b' : '#22845a'} />
        <StatusCard title="FALLBACK CHANNEL" value={failed ? 'LoRa Mesh · 865 MHz' : 'Standby'} tone={failed ? '#b7791f' : '#22845a'} />
        <StatusCard title="TELEMETRY INTERVAL" value={failed ? '60-second condensed packets' : '5-second target'} tone="#2563a6" />
        <StatusCard title="LOCAL CONNECTION" value={online ? 'Browser online' : 'OFFLINE · local cache only'} tone={online ? '#22845a' : '#c2413b'} />
      </div>
      <p style={{ marginBottom: 0, marginTop: 14, fontSize: 13 }}>Service Worker: <b>{swReady ? 'registered' : 'not confirmed (production HTTPS required)'}</b> · Pending telemetry writes: <b>{queued}</b> · {online ? 'Network connected' : 'Offline; queued writes will retry when connectivity returns'}.</p>
      {message && <p role="status" style={{ marginBottom: 0 }}>{message}</p>}
    </section>
    <div className="panel"><div className="table">{sensors.map(x => <div className="sensor-row" key={x.id}><b>{x.name}</b><span>{x.sensor_type}</span><span>{x.latest?.rainfall_mm_h ?? '—'} mm/h</span><span>{x.latest?.river_flow_m3s ?? '—'} m³/s</span><span>{x.latest?.soil_saturation_pct ?? '—'}% soil</span><i>{x.transmission_mode ?? 'CELLULAR_4G'}</i></div>)}</div></div>
    <section className="panel" style={{ marginTop: 18 }}><h2>Telemetry stream</h2><TelemetryStream sensors={sensors} /></section>
  </div>;
}
function StatusCard({ title, value, tone }: { title: string; value: string; tone: string }) {
  return <div style={{ padding: 14, border: '1px solid var(--line, #dce4e8)', borderRadius: 12 }}><small style={{ display: 'block', opacity: .7, marginBottom: 8 }}>{title}</small><strong style={{ color: tone }}>{value}</strong></div>;
}
