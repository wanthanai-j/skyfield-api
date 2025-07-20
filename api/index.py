from flask import Flask, request, jsonify
from skyfield.api import load, Topos
from datetime import datetime

app = Flask(__name__)

# โหลดข้อมูลดาวเคราะห์ (Ephemeris)
eph = load('de421.bsp')
ts = load.timescale()

# รายชื่อดาวเคราะห์ที่ต้องการ
planets = {
    'sun': eph['sun'],
    'moon': eph['moon'],
    'mercury': eph['mercury'],
    'venus': eph['venus'],
    'mars': eph['mars'],
    'jupiter': eph['jupiter barycenter'],
    'saturn': eph['saturn barycenter'],
}

@app.route('/', methods=['GET', 'POST'])
def get_planetary_positions():
    try:
        if request.method == 'POST':
            data = request.json
        else: # GET method
            data = request.args

        # รับค่าจาก request
        # ตัวอย่าง: 2024-12-25T15:30:00Z
        dt_str = data.get('datetime')
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))

        if not all([dt_str, lat, lon]):
            return jsonify({'error': 'Missing required parameters: datetime, lat, lon'}), 400

        # แปลง string เป็น object datetime
        dt_utc = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        t = ts.from_datetime(dt_utc)

        # กำหนดตำแหน่งผู้สังเกตบนโลก
        observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
        earth = eph['earth']

        positions = {}
        for name, body in planets.items():
            astrometric = (earth + observer).at(t).observe(body)
            ra, dec, distance = astrometric.apparent().radec(epoch='date')
            positions[name] = {
                'ra': ra.hours,
                'ra_str': str(ra),
                'dec': dec.degrees,
                'dec_str': str(dec),
                'distance_au': distance.au
            }

        return jsonify(positions)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
