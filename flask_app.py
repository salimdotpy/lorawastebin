from flask import Flask, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

import pytz

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config["DEBUG"] = True
app.config["threaded"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="lorawastebin",
    password="lora2023",
    hostname="lorawastebin.mysql.pythonanywhere-services.com",
    databasename="lorawastebin$wastebin",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.secret_key = "LoRa-based Smart Waste Bin Level Notification System"

def getDate(plus=1):
    date, time = str(datetime.now()).split()
    h, m, s = time.split(':')
    h = int(h) + plus
    time = ':'.join([str(h), m, s])
    dt = date + ' ' + time
    return dt

class Wastebin(db.Model):

    __tablename__ = "wastebins"

    id = db.Column(db.Integer, primary_key=True)
    binId = db.Column(db.String(50))
    lon = db.Column(db.String(28))
    lat = db.Column(db.String(28))
    level = db.Column(db.String(50))
    seenby = db.Column(db.Text(), default='[]')
    date = db.Column(db.String(40), default=getDate)

    def to_dict(self):
        return {
            'id':self.id,
            'binId': self.binId,
            'lon': self.lon,
            'lat': self.lat,
            'level': self.level,
            'seenby': eval(self.seenby),
            'date': self.date
        }

class binNotify(db.Model):

    __tablename__ = "binnotifys"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text())
    status = db.Column(db.Boolean, nullable=False, default=False)
    bId = db.Column(db.Integer, db.ForeignKey('wastebins.id'), nullable=True)
    bin = db.relationship('Wastebin', foreign_keys=bId)
    binDate = db.Column(db.String(40), nullable=True)
    date = db.Column(db.String(40), default=datetime.now)
    def to_dict(self):
        return {
            'id':self.id,
            'text': self.text,
            'status': self.status,
            'bId': self.bId,
            'bin': self.bin.to_dict(),
            'binDate': self.binDate,
            'date': self.date
        }

# Route to serve the service worker from the root
@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

@app.route("/", methods=["POST","GET"])
def index():
    binInfo = None
    if request.method == "POST":
        if 'newNotify' in request.get_json():
            data = request.get_json()
            # binId = data["binId"]
            userToken = data["userToken"]
            binDate = data["binDate"]
            getam = Wastebin.query.filter_by(date=binDate).first()#.to_dict()
            sb = [] if len(eval(getam.seenby)) == 0 else eval(getam.seenby)
            try:
                if userToken not in sb:
                    sb.append(userToken)
                    getam.seenby = str(sb)
                    db.session.commit()
                    return {'status': True, 'data': 'added succefully!'}#getam.to_dict()}
                return {'status': False, 'data': getam.to_dict(), 'send': data}
            except Exception as e:
                db.session.rollback()
                return {'status': False, 'data': 'Something went wrong, please try again later! '+ str(e)}
        if 'newBin' in request.get_json():
            bins = Wastebin.query.all()
            seenby = request.get_json()['seenby']
            try:
                newBins = [
                    {'id':bin.id,'binId': bin.binId, 'lon': bin.lon, 'lat': bin.lat, 'level': bin.level, 'date': bin.date, 'seenby': bin.seenby}
                    for bin in bins if seenby not in eval(bin.seenby)
                ]
                # content = [newBins[cnt] for cnt in range(len(newBins)) if cnt < 1 ]
                return newBins
            except Exception as e:
                return {'status': False, 'data': str(e)}
        return {'error': 'Invalid request'}, 400
    return render_template("index.html", binInfo=binInfo)

@app.route("/getdate")
def dd():
    #import pytz
    from datetime import datetime, timedelta
    # Nigeria is UTC+1
    nigeria_offset = timezone(timedelta(hours=20))
    nigeria_time = datetime.now(nigeria_offset)
    datetime_in_Lagos = pytz.timezone('Africa/Lagos').localize(datetime.now())
    return {'systemDate': datetime.now(), 'Date': datetime_in_Lagos, 'mine':nigeria_time}

@app.route("/get-token", methods=["POST","GET"])
def user_token():
    return {'user_token': generate_password_hash(str(datetime.now()))}

@app.route("/waste-bin", methods=["POST","GET"])
def waste_bin():
    if request.method == "POST":
        binId = request.form["binId"]
        lon = request.form["lon"]
        lat = request.form['lat']
        level = request.form['level']
        try:
            db.session.add(Wastebin(binId=binId, lon=lon, lat=lat, level=level))
            db.session.commit()
            return 'wastebin data added succefully!'
        except:
            db.session.rollback()
            return 'Unable to save wastebin data, please try again later'
    else:
        if request.args.get("who") == 'selim':
            binId = request.args.get("binid")
            lon = request.args.get("lon")
            lat = request.args.get('lat')
            level = request.args.get('level')
            try:
                db.session.add(Wastebin(binId=binId, lon=lon, lat=lat, level=level))
                db.session.commit()
                return 'wastebin data added succefully!'
            except Exception as e:
                db.session.rollback()
                return e #'Unable to save wastebin data, please try again later'
        return 'Method not allowed'

@app.route("/waste-report", methods=["POST","GET"])
def waste_report():
    binInfo = Wastebin.query.order_by(Wastebin.id.desc()).all()
    try:
        binInfo = [
            {'id':bin.id,'binId': bin.binId, 'lon': bin.lon, 'lat': bin.lat, 'level': bin.level, 'date': datetime.strptime(bin.date, "%Y-%m-%d %H:%M:%S.%f"), 'seenby': bin.seenby}
            for bin in binInfo
        ]
    except:
        binInfo = []
    return render_template("index.html", binInfo=binInfo)

@app.route("/waste-map", methods=["POST","GET"])
def waste_map():
    id = request.args.get("id")
    if id:
        bin = Wastebin.query.get(int(id))
        binInfo = [{'id':bin.id,'binId': bin.binId, 'lon': bin.lon, 'lat': bin.lat, 'level': bin.level,'date': datetime.strptime(bin.date, "%Y-%m-%d %H:%M:%S.%f").strftime("%a, %d %b %Y at %I:%M:%S%p")}]
    else:
        binInfo = Wastebin.query.all()#.order_by(Wastebin.id.desc()).all()
        try:
            binInfos = {}
            for bin in binInfo:
                binInfos[f'"{bin.binId}"'] = {'id':bin.id,'binId': bin.binId, 'lon': bin.lon, 'lat': bin.lat, 'level': bin.level,'date': datetime.strptime(bin.date, "%Y-%m-%d %H:%M:%S.%f").strftime("%a, %d %b %Y at %I:%M:%S%p")}
                binInfo = list(binInfos.values())
        except:
            pass
    return render_template("map.html", binInfo=binInfo)
