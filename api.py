from flask import Flask, jsonify, request, json
from flask_sqlalchemy import SQLAlchemy
import time
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
headers = {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',     'Expires': '0',
    'Access-Control-Allow-Origin': 'http://localhost:3000',
    # 'Access-Control-Allow-Origin': 'http://18.217.169.110:80',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token'
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/cashFlow_sheet.db'
app.config['SQLALCHEMY_BINDS'] = {
    'pocket_stock': 'sqlite:///data/pocket_stock.db',
    'stockinfo': 'sqlite:///data/balance_sheet.db',
    'stock_name_id': 'sqlite:///data/stockinfo.db',
    'balance_sheet': 'sqlite:///data/balance_sheet.db',
    'income_sheet': 'sqlite:///data/income_sheet.db',
    'cashFlow_sheet': 'sqlite:///data/cashFlow_sheet.db',
    'legal_person': 'sqlite:///data/legal_person.db',
    'legalPerson': 'sqlite:///data/legalPerson.db',
    'price': 'sqlite:///data/price.db',
    'marginTrade': 'sqlite:///data/marginTrading.db',
    'top_sell': 'sqlite:///data/top_sell.db',
    'top_buy': 'sqlite:///data/top_buy.db',
}

db = SQLAlchemy(app)


@app.route('/')
def server():
    # return send_from_directory(app.static_folder, 'index.html')
    return {
        'hello': '你好'
    }


class StockInfo(object):
    __table_args__ = {'extend_existing': True}
    id = db.Column('index', db.Integer, primary_key=True)
    date = db.Column('date', db.String, nullable=False)
    # cash = db.Column('現金及約當現金', db.Float, nullable=True)
    # total = db.Column('資產總額', db.Float, nullable=True)


def stock_serializer(stock):
    return {
        'index': stock.id,
        'date': stock.date,
        # 'cash': stock.cash,
        # 'total': stock.total
    }


names = ['_1101', '_2317', '_2330', '_3481']
stocks = []
for name in names:
    n = type(name.title(), (StockInfo, db.Model), {'__tablename__': name})
    stocks.append(n)


@app.route('/api/allStock')
def index():
    for stock in stocks:
        results = db.session.query(stock).all()
        print(results)
        for r in results:
            print(r.date)
    read_data = db.session.query(stocks[1]).all()
    print('read_data:', read_data)
    return jsonify([*map(stock_serializer, read_data)])


class StockIdName(db.Model):
    __bind_key__ = 'stock_name_id'
    __tablename__ = 'stock_name'
    id_and_name = db.Column('有價證券代號及名稱', db.String, primary_key=True)

    def __init__(self, id_and_name):
        self.id_and_name = id_and_name


def id_and_name_serializer(stock):
    return {
        'id_name': stock.id_and_name
    }


@app.route('/api/search', methods=['GET', 'POST'])
def search_stock():
    if request.method == 'GET':
        data = [*map(id_and_name_serializer, StockIdName.query.all())]
        del(data[651])
        data = data[1:952]
        read_data = jsonify(data)
        return read_data


class Balance(object):
    __bind_key__ = 'balance_sheet'
    __table_args__ = {'extend_existing': True}
    id = db.Column('index', db.Integer, primary_key=True)
    date = db.Column('date', db.String, nullable=False)
    accounts_receivable = db.Column('應收帳款淨額', db.Float, nullable=False)
    accounts_payable = db.Column('應付帳款', db.Float, nullable=False)
    total_liabilities = db.Column('負債總額', db.Float, nullable=False)
    total_assets = db.Column('資產總額', db.Float, nullable=False)
    non_current_assets = db.Column('非流動資產合計', db.Float, nullable=False)
    stock_holders_equity = db.Column('權益總額', db.Float, nullable=True)
    common_stock = db.Column('普通股股本', db.Float, nullable=True)
    inventory = db.Column('存貨', db.Float, nullable=True)
    # stocks_total = db.Column('股本合計', db.Float, nullable=True)
    capital_reserve = db.Column('資本公積合計', db.Float, nullable=True)
    re = db.Column('保留盈餘合計', db.Float, nullable=True)


def balance_serializer(balance):
    return {
        'id': balance.id,
        'date': balance.date,
        'accounts_receivable': balance.accounts_receivable,
        'accounts_payable': balance.accounts_payable,
        'total_liabilities': balance.total_liabilities,
        'total_assets': balance.total_assets,
        'non_current_assets': balance.non_current_assets,
        'stock_holders_equity': balance.stock_holders_equity,
        'common_stock': balance.common_stock,
        'inventory': balance.inventory,
        # 'stocks_total': balance.stocks_total,
        'capital_reserve': balance.capital_reserve,
        're': balance.re,
    }


@app.route('/api/balance', methods=['POST', 'GET'])
def balance_display():
    if request.method == 'POST':
        request_data = json.loads(request.data)
        n = type('balance_' + request_data.get('table_name'), (Balance, db.Model),
                 {'__tablename__': 'balance_' + request_data.get('table_name')})
    read_data = jsonify([*map(balance_serializer, n.query.all())])
    return read_data


class Income(object):
    __bind_key__ = 'income_sheet'
    __table_args__ = {'extend_existing': True}
    id = db.Column('index', db.Integer, primary_key=True)
    date = db.Column('date', db.String, nullable=False)
    benefit_total = db.Column('營業收入合計', db.Float, nullable=False)
    benefit = db.Column('營業利益（損失）', db.Float, nullable=False)
    cost_total = db.Column('營業成本合計', db.Float, nullable=False)
    non_operating_income = db.Column('營業外收入及支出合計', db.Float, nullable=False)
    profit_before_tax = db.Column('稅前淨利（淨損）', db.Float, nullable=False)
    net_income = db.Column('繼續營業單位本期淨利（淨損）', db.Float, nullable=True)
    # 稅後淨利, 每股盈餘


def income_serializer(income):
    return {
        'id': income.id,
        'date': income.date,
        'benefit_total': income.benefit_total,
        'benefit': income.benefit,
        'cost_total': income.cost_total,
        'non_operation_income': income.non_operating_income,
        'profit_before_tax': income.profit_before_tax,
        'net_income': income.net_income,
    }


@app.route('/api/income', methods=['POST', 'GET'])
def income_display():
    if request.method == 'POST':
        request_data = json.loads(request.data)
        n = type('_' + request_data.get('table_name'), (Income, db.Model),
                 {'__tablename__': '_' + request_data.get('table_name')})

    read_data = jsonify([*map(income_serializer, n.query.all())])
    return read_data


class CashFlow(object):
    __bind_key__ = 'cashFlow_sheet'
    __table_args__ = {'extend_existing': True}
    id = db.Column('index', db.Integer, primary_key=True)
    inventory_increase = db.Column('存貨（增加）減少', db.Float, nullable=False)
    depreciation_expense = db.Column('折舊費用', db.Float, nullable=False)
    amortization_fee = db.Column('攤銷費用', db.Float, nullable=False)
    cashFlow_operating = db.Column('營業活動之淨現金流入（流出）', db.Float, nullable=True)


def cash_serializer(cash):
    return {
        'id': cash.id,
        'inventory_increase': cash.inventory_increase,
        'depreciation_expense': cash.depreciation_expense,
        'amortization_fee': cash.amortization_fee,
        'cashFlow_operating': cash.cashFlow_operating,
    }


@app.route('/api/cashFlow', methods=['POST', 'GET'])
def cashFlow_display():
    if request.method == 'POST':
        request_data = json.loads(request.data)
        n = type('cashFlow_' + request_data.get('table_name'), (CashFlow, db.Model),
                 {'__tablename__': 'cashFlow_' + request_data.get('table_name')})

    read_data = jsonify([*map(cash_serializer, n.query.all())])
    return read_data

# @app.route('/price', methods=['POST', 'GET'])
# def price_csv():
#     if request.method == 'POST':
#         request_data = json.loads(request.data)
#         print(request_data['table_name']) # 2330
#         absPath = os.path.dirname(os.path.abspath(__file__))
#         path = os.path.join(absPath, 'data', 'price_data', 'price_' + request_data['table_name'] +  '.csv')
#         csv_file = pd.read_csv(path)
#         print(csv_file)
#     return 'csv_file'


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


class LegalPerson(object):
    __bind_key__ = 'legalPerson'
    __table_args__ = {'extend_existing': True}
    index = db.Column('index', db.Integer, primary_key=True)
    # stock_id = db.Column('stock_id', db.String, primary_key=True)
    date = db.Column('date', db.String,  nullable=True)
    foreign_invest = db.Column('外陸資買賣超股數(不含外資自營商)', db.Integer, nullable=True)
    credit = db.Column('投信買賣超股數', db.Integer, nullable=True)
    self_employee = db.Column('自營商買賣超股數', db.Integer, nullable=True)
    total_invest = db.Column('三大法人買賣超股數', db.Integer, nullable=True)


def legalPerson_serializer(item):
    return {
        # 'stock_id': item.stock_id,
        'date': item.date,
        'foreign_invest': item.foreign_invest,
        'credit': item.credit,
        'self_employee': item.self_employee,
        'total_invest': item.total_invest,
    }


@app.route('/api/legalPerson', methods=['POST'])
def legalPerson_display():
    request_data = json.loads(request.data)
    n = type('legalPerson_' + request_data.get('table_name'), (LegalPerson, db.Model),
             {'__tablename__': 'legalPerson_' + request_data.get('table_name')})
    read_data = jsonify([*map(legalPerson_serializer, n.query.all())])
    return read_data


class MarginTrade(object):
    __bind_key__ = 'marginTrade'
    __table_args__ = {'extend_existing': True}
    index = db.Column('index', db.Integer, primary_key=True)
    margin_trade_total = db.Column(
        'margin_trade_total', db.Integer, nullable=True)
    short_sell_total = db.Column('short_sell_total', db.Integer, nullable=True)
    total_offset = db.Column('total_offset', db.Integer, nullable=True)
    date = db.Column('date', db.String, nullable=False)


def marginTrade_serializer(item):
    return {
        'index': item.index,
        'margin_trade_total': item.margin_trade_total,
        'short_sell_total': item.short_sell_total,
        'total_offset': item.total_offset,
        'date': item.date,
    }


@app.route('/api/marginTrade', methods=['POST'])
def marginTrade_display():
    request_data = json.loads(request.data)
    n = type('marginTrading_' + request_data.get('table_name'), (MarginTrade, db.Model),
             {'__tablename__': 'marginTrading_' + request_data.get('table_name')})
    read_data = jsonify([*map(marginTrade_serializer, n.query.all())])
    return read_data


class PocketStock(db.Model):
    __bind_key__ = 'pocket_stock'
    __tablename__ = 'stock'
    stockid = db.Column('stock_id', db.String, primary_key=True)


def stockid_serializer(stock):
    return {
        'stockid': stock.stockid,
    }


@app.route('/api/add_pocket_stock', methods=['POST', 'GET'])
def addStock():
    if request.method == 'POST':
        request_data = json.loads(request.data)
        stock = PocketStock(stockid=request_data['stockid'])
        db.session.add(stock)
        db.session.commit()
        return {
            '201': 'add stock successfully'
        }
    if request.method == 'GET':
        # [
        #     {
        #         stockid: '2330',
        #         close: 600.00,
        #         '漲跌': 1.00,
        #         '幅度': '0.05%',
        #         'volume': 100M,
        #         'open':
        #     },
        # ]
        stock_list = [*map(stockid_serializer, PocketStock.query.all())]
        print('stock_list: ', stock_list[0]['stockid'])
        stockid_list = []
        stocks_array = []
        income_array = []
        for item in stock_list:
            item_to_list = item['stockid'].split('\u3000')[0]
            stockid_list.append(item_to_list)
        for item in stockid_list:
            n = type(item.title(), (Price, db.Model), {
                     '__tablename__': 'price_' + item})
            stocks_array.append(n)
            n1 = type(item.title(), (Income, db.Model),
                      {'__tablename__': '_' + item})
            income_array.append(n1)

        # stock_result = []
        # for stock in stocks_array:
        #     results = db.session.query(stock).all()
        #     _id = { 'stockid': '2330' }
        # return jsonify([*map(price_serializer, results)][-1])

        info_arr = []
        for i in range(0, len(stocks_array)):
            results = db.session.query(stocks_array[i]).all()
            _id = {'stockid': stock_list[i]['stockid']}
            lastDay_close = [*map(price_serializer, results)][-2]['Close']
            lastDay_close_dict = {'last_close': lastDay_close}

            income_results = db.session.query(income_array[i]).all()

            benefit_total = [
                *map(income_serializer, income_results)][-1]['benefit_total']
            dict_benefit = {'benefit_total': benefit_total}
            cost_total = [
                *map(income_serializer, income_results)][-1]['cost_total']
            grossMargin = int(
                (benefit_total - cost_total) / benefit_total * 100)
            dict_grossMargin = {'grossMargin': grossMargin}

            stockinfo = dict([*map(price_serializer, results)][-1], **_id,
                             **lastDay_close_dict, **dict_benefit, **dict_grossMargin)
            info_arr.append(stockinfo)
        # return jsonify([*map(stockid_serializer, PocketStock.query.all())])
        return jsonify(info_arr)


@app.route('/api/remove_pocket_stock', methods=['GET', 'POST', 'DELETE'])
def removeStock():
    request_data = json.loads(request.data)
    PocketStock.query.filter_by(stockid=request_data['stockid']).delete()
    db.session.commit()
    return {
        '204': 'remove stock successfully'
    }


class TopBuy(object):
    __bind_key__ = 'top_buy'
    __table_args__ = {'extend_existing': True}
    buy_name = db.Column('券商', db.String, primary_key=True)
    top_buy = db.Column('top_buy', db.Integer, nullable=False)
    top_buy_buy = db.Column('top_buy_buy', db.Integer, nullable=False)
    top_buy_sell = db.Column('top_buy_sell', db.Integer, nullable=False)


def topBuy_serializer(item):
    return {
        'buy_name': item.buy_name,
        'top_buy': item.top_buy,
        'top_buy_buy': item.top_buy_buy,
        'top_buy_sell': item.top_buy_sell
    }


@app.route('/api/topBuy', methods=['POST'])
def topBuy_display():
    request_data = json.loads(request.data)
    n = type('buy_' + request_data.get('table_name'), (TopBuy, db.Model),
             {'__tablename__': 'buy_' + request_data.get('table_name')})
    read_data = jsonify([*map(topBuy_serializer, n.query.all())])
    return read_data


class TopSell(object):
    __bind_key__ = 'top_sell'
    __table_args__ = {'extend_existing': True}
    sell_name = db.Column('券商', db.String, primary_key=True)
    top_sell = db.Column('top_sell', db.Integer, nullable=False)
    top_sell_buy = db.Column('top_sell_buy', db.Integer, nullable=False)
    top_sell_sell = db.Column('top_sell_sell', db.Integer, nullable=False)


def topSell_serializer(item):
    return {
        'sell_name': item.sell_name,
        'top_sell': item.top_sell,
        'top_sell_buy': item.top_sell_buy,
        'top_sell_sell': item.top_sell_sell
    }


@app.route('/api/topSell', methods=['POST'])
def topSell_display():
    request_data = json.loads(request.data)
    n = type('sell_' + request_data.get('table_name'), (TopSell, db.Model),
             {'__tablename__': 'sell_' + request_data.get('table_name')})
    read_data = jsonify([*map(topSell_serializer, n.query.all())])
    return read_data
