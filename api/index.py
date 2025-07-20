from flask import Flask, request, jsonify
from skyfield.api import load, Topos
from datetime import datetime
import os # <-- เพิ่ม import os

app = Flask(__name__)

# --- ส่วนที่แก้ไข ---
# กำหนด path สำหรับดาวน์โหลดข้อมูลไปยัง /tmp
# ซึ่งเป็นที่เดียวที่ Vercel อนุญาตให้เขียนไฟล์ได้
data_path = '/tmp'
# สร้าง object loader ที่รู้ว่าต้องใช้ path ไหน
loader = load.Loader(data_path)
# --- จบส่วนที่แก้ไข ---


# โหลดข้อมูลดาวเคราะห์ (Ephemeris) โดยใช้ loader ที่เราสร้างขึ้น
eph = loader('de421.bsp')
ts = loader.timescale() # <-- ใช้ loader.timescale() แทน load.timescale()

# รายชื่อดาวเคราะห์ที่ต้องการ (เหมือนเดิม)
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

        # รับค่าจาก request (เหมือนเดิม)
        dt_str = data.get('datetime')
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))

        if not all([dt_str, lat, lon]):
            return jsonify({'error': 'Missing required parameters: datetime, lat, lon'}), 400

        # แปลง string เป็น object datetime (เหมือนเดิม)
        dt_utc = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        t = ts.from_datetime(dt_utc)

        # กำหนดตำแหน่งผู้สังเกตบนโลก (เหมือนเดิม)
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