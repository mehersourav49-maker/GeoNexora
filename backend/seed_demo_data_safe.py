
from datetime import datetime

from app.core.database import Base, engine, SessionLocal
from app.models import (
    Sensor,
    Telemetry,
    Shelter,
    AgencyContact,
    Incident,
    Alert,
)

Base.metadata.create_all(bind=engine)


def seed_demo_data():
    db = SessionLocal()

    try:
        # 1. Sensors and telemetry: seed only if sensors are absent.
        if db.query(Sensor).count() == 0:
            nodes = [
                ("Alaknanda Gauge 01", "river_gauge", 30.566, 79.566, 1850, 132, 248, 4.1, 88, 31),
                ("Joshimath Rain Node", "rainfall", 30.558, 79.565, 1875, 118, 180, 3.5, 92, 34),
                ("Chamoli Soil Probe", "soil_moisture", 30.404, 79.321, 1550, 96, 145, 2.8, 96, 29),
                ("Badrinath River Node", "river_gauge", 30.744, 79.493, 3000, 84, 210, 3.7, 79, 32),
                ("Govindghat Rain Node", "rainfall", 30.642, 79.594, 1820, 72, 165, 3.0, 81, 30),
                ("Pipalkoti Soil Node", "soil_moisture", 30.425, 79.432, 1260, 61, 120, 2.5, 74, 27),
                ("Lambagarh Gauge", "river_gauge", 30.741, 79.579, 2550, 105, 225, 3.8, 88, 33),
                ("Nandprayag Rain Node", "rainfall", 30.327, 79.317, 950, 48, 92, 2.0, 67, 24),
                ("Karnaprayag Soil Node", "soil_moisture", 30.259, 79.257, 800, 42, 80, 1.8, 63, 22),
                ("Rishikesh Basin Node", "river_gauge", 30.086, 78.267, 370, 35, 60, 1.4, 51, 18),
            ]

            for n in nodes:
                name, typ, lat, lon, elev, rain, flow, level, soil, slope = n

                sensor = Sensor(
                    name=name,
                    sensor_type=typ,
                    latitude=lat,
                    longitude=lon,
                    elevation_m=elev,
                    active=True,
                )
                db.add(sensor)
                db.flush()

                db.add(Telemetry(
                    sensor_id=sensor.id,
                    rainfall_mm_h=rain,
                    river_flow_m3s=flow,
                    river_level_m=level,
                    soil_saturation_pct=soil,
                    slope_incline_deg=slope,
                    api_mm=min(160, rain * 1.15),
                    timestamp=datetime.utcnow(),
                ))

            print("Sensors and telemetry added.")
        else:
            print("Sensors already exist; skipped.")

        # 2. Shelters: add only if the table is empty.
        if db.query(Shelter).count() == 0:
            shelters = [
                ("Joshimath Inter College Shelter", 30.558, 79.566, 800, 420, 3.5, 8, True),
                ("Govindghat Community Hall", 30.642, 79.594, 500, 185, 5, 5, True),
                ("Chamoli Stadium Relief Centre", 30.404, 79.321, 650, 370, 2.2, 7, True),
                ("Pipalkoti ITI Shelter", 30.425, 79.432, 350, 96, 7, 3, True),
                ("Karnaprayag Polytechnic Shelter", 30.259, 79.257, 600, 240, 6, 6, False),
            ]

            for s in shelters:
                db.add(Shelter(
                    name=s[0],
                    latitude=s[1],
                    longitude=s[2],
                    max_capacity=s[3],
                    occupied_beds=s[4],
                    food_days=s[5],
                    medical_staff=s[6],
                    generator_online=s[7],
                    status="operational",
                ))

            print("Shelters added.")
        else:
            print("Shelters already exist; skipped.")

        # 3. Agency contacts: add only if empty.
        if db.query(AgencyContact).count() == 0:
            for agency, hotline, coverage in [
                ("NDRF", "1078", "National emergency response"),
                ("SDRF Uttarakhand", "112", "State disaster response"),
                ("DEOC Chamoli", "1077", "District emergency operations"),
                ("Army Aviation SAR", "112", "Search and rescue coordination"),
            ]:
                db.add(AgencyContact(
                    agency=agency,
                    hotline=hotline,
                    coverage=coverage,
                ))
            print("Agency contacts added.")
        else:
            print("Agency contacts already exist; skipped.")

        # 4. Historical incidents: add only if empty.
        if db.query(Incident).count() == 0:
            incidents = [
                (
                    "2013 Kedarnath Flash Flood",
                    "Kedarnath / Mandakini Basin",
                    datetime(2013, 6, 16),
                    "Critical", 5700, 340,
                    "Extreme rainfall and cascading debris/flood impacts.",
                ),
                (
                    "2021 Chamoli Flood / GLOF",
                    "Raini / Rishiganga Basin",
                    datetime(2021, 2, 7),
                    "Critical", 204, 120,
                    "Sudden high-energy flood and debris flow in a Himalayan valley.",
                ),
                (
                    "2023 Kullu-Manali Floods",
                    "Kullu-Manali, Himachal Pradesh",
                    datetime(2023, 7, 9),
                    "High", 50, 160,
                    "Monsoon flooding and landslide disruption across river corridors.",
                ),
            ]

            for x in incidents:
                db.add(Incident(
                    title=x[0],
                    location=x[1],
                    date=x[2],
                    severity=x[3],
                    fatalities=x[4],
                    rainfall_mm=x[5],
                    description=x[6],
                ))
            print("Historical incidents added.")
        else:
            print("Incidents already exist; skipped.")

        # 5. Demo alert: add only if the alert table is empty.
        if db.query(Alert).count() == 0:
            db.add(Alert(
                severity="HIGH",
                threat_level="High",
                village="Joshimath corridor",
                message=(
                    "Rapidly rising upstream flow and saturated slopes "
                    "require commander attention."
                ),
                lead_time_min_h=2.4,
                lead_time_max_h=4.8,
            ))
            print("Demo alert added.")
        else:
            print("Alerts already exist; skipped.")

        db.commit()
        print("Safe demo seeding completed successfully.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
