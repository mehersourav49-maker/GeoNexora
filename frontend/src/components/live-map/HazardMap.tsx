import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline } from 'react-leaflet';
import L from 'leaflet';
import type { Sensor, Shelter } from '../../api/client';
import 'leaflet/dist/leaflet.css';
const sensorIcon = L.divIcon({ className: 'geo-marker', html: '<span>●</span>', iconSize: [22,22] });
const shelterIcon = L.divIcon({ className: 'geo-shelter-marker', html: '<span>＋</span>', iconSize: [24,24] });
// Approximate corridor sketch for interface demonstration, not a surveyed flood model.
const corridor: [number,number][] = [[30.74,79.49],[30.65,79.52],[30.56,79.57],[30.49,79.52],[30.43,79.44],[30.40,79.32]];
const arrivalMinutes = [20, 45, 75, 95, 110];
const arrivalColor = (minutes:number) => minutes < 30 ? '#c53030' : minutes < 60 ? '#dd6b20' : '#d69e2e';
const nearestCorridorPoint = (lat:number, lon:number):[number,number] => corridor.reduce((best,point) => Math.hypot(point[0]-lat,point[1]-lon) < Math.hypot(best[0]-lat,best[1]-lon) ? point : best, corridor[0]);
export default function HazardMap({ sensors, shelters }: { sensors: Sensor[]; shelters: Shelter[] }) {
  return <div className="map-wrap"><MapContainer center={[30.52,79.48]} zoom={9} scrollWheelZoom className="hazard-map"><TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    {corridor.slice(0,-1).map((point,i)=><Polyline key={`river-${i}`} positions={[point,corridor[i+1]]} pathOptions={{color:arrivalColor(arrivalMinutes[i]),weight:6,opacity:.9}}><Popup>Illustrative corridor segment · scenario arrival band {arrivalMinutes[i]} min · not a validated live forecast</Popup></Polyline>)}
    {sensors.map(s=><Marker key={'s'+s.id} position={[s.latitude,s.longitude]} icon={sensorIcon}><Popup><b>{s.name}</b><br/>Rainfall: {s.latest?.rainfall_mm_h ?? '—'} mm/h<br/>Flow: {s.latest?.river_flow_m3s ?? '—'} m³/s<br/>Channel: {s.transmission_mode ?? 'CELLULAR_4G'}</Popup><Circle center={[s.latitude,s.longitude]} radius={1200} pathOptions={{color:'#e07a3f',fillOpacity:.08}} /></Marker>)}
    {shelters.map(s=><Polyline key={`evac-${s.id}`} positions={[nearestCorridorPoint(s.latitude,s.longitude),[s.latitude,s.longitude]]} pathOptions={{color:'#27845a',weight:2,dashArray:'5 6',opacity:.8}}><Popup>Illustrative shelter access line to {s.name}; verify safe uphill route locally.</Popup></Polyline>)}
    {shelters.map(s=><Marker key={'h'+s.id} position={[s.latitude,s.longitude]} icon={shelterIcon}><Popup><b>{s.name}</b><br/>Capacity: {s.occupied_beds}/{s.max_capacity}<br/>Available beds: {Math.max(0,s.max_capacity-s.occupied_beds)}<br/>Status: {s.status}</Popup><Circle center={[s.latitude,s.longitude]} radius={350} pathOptions={{color:'#2b8a5b',fillOpacity:.18}} /></Marker>)}
  </MapContainer><div className="map-key"><b>Himalayan command map</b><span>● Sensors</span><span>＋ Relief shelters</span><span style={{color:'#c53030'}}>━ Red: &lt; 30 min</span><span style={{color:'#dd6b20'}}>━ Orange: 30–60 min</span><span style={{color:'#b7791f'}}>━ Yellow: 60–120 min</span><span style={{color:'#27845a'}}>┄ Illustrative shelter access</span><small>Travel-time bands require calibrated hydraulic inputs; route currently illustrative.</small></div></div>;
}
