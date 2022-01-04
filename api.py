from flask import Flask, jsonify, request, json
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/price.db'
app.config['SQLALCHEMY_BINDS'] = {
    'price': 'sqlite:///data/price.db',
}

db = SQLAlchemy(app)

@app.route('/api/time')
def get_current_time():
    return { 'time': time.time() }

class Price(object):
    __bind_key__ = 'price'
    __table_args__ = {'extend_existing': True}
    Date = db.Column('date', db.String, primary_key=True)
    Open = db.Column('open', db.Float, nullable=False)
    High = db.Column('high', db.Float, nullable=False)
    Low = db.Column('low', db.Float, nullable=False)
    Close = db.Column('close', db.Float, nullable=False)
    Volume = db.Column('volume', db.Float, nullable=False)
    Ma5 = db.Column('ma5', db.Float, nullable=True)
    Ma10 = db.Column('ma10', db.Float, nullable=True)
    Ma20 = db.Column('ma20', db.Float, nullable=True)
    volumeMa5 = db.Column('volumeMa5', db.Float, nullable=True)
    volumeMa10 = db.Column('volumeMa10', db.Float, nullable=True)
    volumeMa20 = db.Column('volumeMa20', db.Float, nullable=True)
    slowk = db.Column('slowk', db.Float, nullable=True)
    slowd = db.Column('slowd', db.Float, nullable=True)
    slowj = db.Column('slowj', db.Float, nullable=True)


def price_serializer(price):
    return {
        'Date': price.Date,
        'Open': price.Open,
        'High': price.High,
        'Low': price.Low,
        'Close': price.Close,
        'Volume': price.Volume,
        'Ma5': price.Ma5,
        'Ma10': price.Ma10,
        'Ma20': price.Ma20,
        'volumeMa5': price.volumeMa5,
        'volumeMa10': price.volumeMa10,
        'volumeMa20': price.volumeMa20,
        'slowk': price.slowk,
        'slowd': price.slowd,
        'slowj': price.slowj,
    }


@app.route('/api/stockprice', methods=['POST', 'GET'])
def price_display():
    if request.method == 'POST':
        request_data = json.loads(request.data)
        n = type('price_' + request_data.get('table_name'), (Price, db.Model),
                 {'__tablename__': 'price_' + request_data.get('table_name')})
        read_data = jsonify([*map(price_serializer, n.query.all())])
        return read_data
    if request.method == 'GET':
        print('get')
        return '200'