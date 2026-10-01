import axios from 'axios';

export const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_URL ||
    (import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''),
});
export type Sensor={id:number;name:string;sensor_type:string;latitude:number;longitude:number;elevation_m:number;active:boolean;transmission_mode?:string;latest?:Telemetry};
export type Telemetry={id:number;sensor_id:number;rainfall_mm_h:number;river_flow_m3s:number;river_level_m:number;soil_saturation_pct:number;slope_incline_deg:number;api_mm:number;timestamp:string};
export type Shelter={id:number;name:string;latitude:number;longitude:number;max_capacity:number;occupied_beds:number;food_days:number;medical_staff:number;generator_online:boolean;status:string};
