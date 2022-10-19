import os
import json
from datetime import date, timedelta
from functools import wraps
from werkzeug.local import LocalProxy
from ageptdb import GEPTDB
from amaindb import MAINDB
from flask import Flask, render_template, send_from_directory
from flask import session, request, redirect, url_for, current_app
import utils

app = Flask(__name__)
geptDB = GEPTDB()
mainDB = MAINDB()
log = LocalProxy(lambda: current_app.logger)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# SHA-256 from 'flaskblank'
app.config['SECRET_KEY'] = 'ad4daf864b7ef595f5bbb6d1d55aca53c4e1c959827327e91ab15478b5164d9a'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
cyear = date.today().year
nowid = lambda: utils.get_nowid()
dtnow = lambda: utils.get_datetime()

@app.before_request
def before_request():
    if 'DYNO' in os.environ:
        if request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            code = 301
            return redirect(url, code=code)

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('is_auth') is None:
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def index():
    submit_result = ''
    if request.method == 'POST':
        # log.info(request.form)
        # 密碼與帳號相同
        # print(request.form.get('txtPassword'))
        dict_roles = {
            'guest': '-----',
            'admin': '-----'
        }
        if 'selRole' in request.form and 'txtPassword' in request.form:
            the_role = request.form.get('selRole')
            if the_role in dict_roles and request.form.get('txtPassword') == dict_roles[the_role]:
                session['is_auth'] = True
                session['role_name'] = the_role
                session['account'] = the_role
                return redirect(url_for('home'))
            elif the_role not in dict_roles:
                submit_result = '登入失敗：身份識別錯誤'
            else:
                submit_result = '登入失敗：通行密碼錯誤'
        else:
            return redirect(url_for('denied'))
    return render_template('login-home.html', submit_result=submit_result, cyear=cyear, nowid=nowid())

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    next_url = 'home'
    session.clear()
    return redirect(url_for(next_url))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/x-icon')

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'robots.txt', mimetype='text/plain')

@app.route('/denied')
def denied():
    return render_template("denied.html", cyear=cyear, nowid=nowid())

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", cyear=cyear, nowid=nowid()), 404

@app.route('/home')
@login_required
def home():
    # log.info(session)
    return render_template('home.html', cyear=cyear, dtnow=dtnow(), nowid=nowid())

@app.route('/exercise')
@login_required
def exercise():
    return render_template('exercise.html', nowid=nowid())

@app.route('/flaskweb/movies/<act_id>')
@login_required
def movies(act_id):
    json_file=open(app.root_path+'/templates/json_file/movies.json', encoding='utf-8').read()
    list_movies = json.loads(json_file)
    return render_template('flaskweb/movies.html', nowid=nowid(), act_id=act_id, list_movies=list_movies)

@app.route('/opendata')
@login_required
def opendata():
    return render_template('opendata/opendata.html', nowid=nowid())

@app.route('/opendata/Light_Rail')
@login_required
def Light_Rail():
    return render_template('opendata/Light_Rail.html', nowid=nowid())

@app.route('/opendata/Light_Rail_list/<qlimit>')
@login_required
def Light_Rail_list(qlimit):
    from templates.opendata import Light_Rail
    try:
        json_data = Light_Rail.fetch(int(qlimit))
        return {'jsonData':json_data}
    except:
        return {}
    
@app.route('/opendata/vaccine')
@login_required
def vaccine():
    return render_template('opendata/vaccine.html', nowid=nowid())

@app.route('/word_test/abc_word')
@login_required
def abc_word():
    return render_template('/word_test/abc_word.html', nowid=nowid())

@app.route('/gept-words')
@login_required
def gept_words():
    return render_template('gept/gept-words.html', nowid=nowid())

@app.route('/gept_tests_save', methods=['POST'])
@login_required
def gept_tests_save():
    from random import shuffle
    chkw1 = int(request.form.get('chkW1'))
    chkw2 = int(request.form.get('chkW2'))
    chkw3 = int(request.form.get('chkW3'))
    check_wlevel = (chkw1, chkw2, chkw3)
    word_levels = dict(zip(list(geptDB.word_levels.keys()), check_wlevel))
    gept_words = open(os.path.join(app.root_path, 'templates/gept/gept-words.json')).read()
    json_data = json.loads(gept_words)

    # 擷取題型設定
    settings = geptDB.get_settings()
    # 重置測驗
    # geptDB.reset_tests()

    for wlevel_index, wlevel in enumerate(word_levels.keys()):
        # 是否依級別設定測驗
        if word_levels[wlevel] == 1:
            list_words = []
            for wl_words in json_data[wlevel_index]:
                list_words.extend(wl_words['words'])
            # 新增測驗
            shuffle(list_words)
            dict_types = {
                'fill_in_the_blank': int(request.form.get('chkFB')),
                'multiple_choice': int(request.form.get('chkMC'))
            }
            test_id=geptDB.save_tests(wlevel, 1, list_words, settings, dict_types)
    return {'test_id':test_id}

@app.route('/gept-scores')
@login_required
def gept_scores():
    return render_template('gept/gept-scores.html', nowid=nowid())

@app.route('/gept-sheets')
@login_required
def gept_sheets():
    return render_template('gept/gept-sheets.html', nowid=nowid())

@app.route('/gept_sheets_read', methods=['POST'])
@login_required
def gept_sheets_read():
    test_args = geptDB.get_test_args(request.form)
    test_sheet = geptDB.read_test(test_args)
    return {'test_sheet':test_sheet}

@app.route('/gept_sheets_score', methods=['POST'])
def gept_sheets_score():
    test_id = request.form['TestID']
    # print(request.form)
    result = True
    test_args = geptDB.get_test_args(request.form)
    test_sheet = geptDB.read_test(test_args)
    sheet_count = len(test_sheet)
    sheet_right = 0
    for i, question in enumerate(test_sheet):
        quid = 'q'+str(i)
        if quid in request.form:
            if str(question['ans']) == request.form[quid]:
                # print('{}={}'.format(str(question['ans']), request.form[quid]))
                sheet_right += 1
    # 計算分數
    score = 0
    denominator = sheet_count * sheet_right
    if denominator > 0:
        score = int(100 / sheet_count * sheet_right)
    # 記錄分數
    geptDB.save_score(score, test_args)
    
    return {'result':result, 'score':score}

@app.route('/opendata/vaccine/<qlimit>')
@login_required
def vaccine_list(qlimit):
    from templates.opendata import vaccine
    try:
        json_data = vaccine.fetch(int(qlimit))
        return {'jsonData':json_data}
    except:
        return {}

@app.route('/stock', methods=['GET', 'POST'])
def stock():
    session['is_auth'] = False
    valid_inputs = ['actCode', 'newAccount', 'newPassword',
                    'theAccount','txtAccount', 'txtPassword']
    act_code=''
    submit_result = ''
    
    if request.method == 'POST':
        form_inputs = sorted(list(request.form.keys()))
        if form_inputs == valid_inputs:
            act_code = request.form.get('actCode')
            account = request.form.get('txtAccount')
            password = request.form.get('txtPassword')
            new_account = request.form.get('newAccount')
            new_password = request.form.get('newPassword')
            the_account = request.form.get('theAccount')

            if act_code == 'Signin':
                user_info, isauth, msg = mainDB.signin(account, password)
                if isauth:
                    session['is_auth'] = True
                    session['role_name'] = user_info['role']
                    session['account'] = account
                    session['portal'] = 'stock'
            elif act_code == 'Signup':
                user_info, issignup, msg = mainDB.signup(new_account, new_password)
            elif act_code == 'ResetPassword':
                msg = mainDB.reset_password(the_account)
            elif act_code == 'ResendActivation':
                msg = mainDB.send_activation(the_account)
            if session.get('is_auth') == True:
                return redirect(url_for('stock_assets'))
            else:
                submit_result = msg
        else:
            return redirect(url_for('denied'))
    return render_template('stock/login-stock.html', submit_result=submit_result,
            act_code=act_code, cyear=cyear, nowid=nowid())       

@app.route('/activate_account/<userid>/<act_hash>')
def activate_account(userid, act_hash):
    is_activated = mainDB.activate_user(userid, act_hash)
    return render_template('is-activated.html', cyear=cyear,is_activated=is_activated)

@app.route('/resetpassword/<userid>', methods=['GET', 'POST'])
def password_reset(userid):
    submit_result = ''
    if request.method == 'POST':
        newpassword = request.form.get('newPassword')
        confirm_pass = request.form.get('confirmPassword')
        if len(newpassword) == 0:
            submit_result = '密語不可為空，請重新輸入'
        elif newpassword == confirm_pass:
            mainDB.pw_reset(userid, newpassword)
            return redirect(url_for('resetsuccessful'))
        else:
            submit_result = '密語錯誤，請重新輸入'
    return render_template('resetPassword.html', submit_result=submit_result, nowid=nowid())

@app.route('/resetsuccessful')
def resetsuccessful():
    return render_template("is-resetPassword.html", cyear=cyear, nowid=nowid())

@app.route('/stock-assets')
@login_required
def stock_assets():
    return render_template('stock/stock-assets.html',nowid=nowid())

@app.route('/stock/passbook')
@login_required
def passbook():
    return {'passbook': mainDB.get_passbook(session['account'])}

@app.route('/stock/price/<stockid>')
@login_required
def stock_price(stockid):
    from scraper import ggfinance
    stockex = mainDB.get_stockex(stockid)
    stockpp = ggfinance.get_stock_price(stockex)
    balance = mainDB.get_passbook_balance(session['account'])
    return {'result':stockpp, 'balance':balance}

@app.route('/stock-entrust')
@login_required
def stock_entrust():
    list_stocks = mainDB.get_stocks()
    return render_template('stock/stock-entrust.html', list_stocks=list_stocks, nowid=nowid(), na='Japen')

@app.route('/stock-settings')
@login_required
def stock_settings():
    list_stocks = mainDB.get_stocks()
    return render_template('stock/stock-settings.html', list_stocks=list_stocks, nowid=nowid())

@app.route('/stock_stocks_save', methods=['POST'])
@login_required
def stock_stocks_save():
    stock = request.form
    if stock.get('act') == 'Save':
        mainDB.save_stock(**stock)
    elif stock.get('act') == 'Drop':
        mainDB.drop_stock(**stock)
    main_stocks = mainDB.get_stocks()
    return {'main_stocks':main_stocks}

@app.route('/stock_set_init_balance', methods=['POST'])
@login_required
def stock_set_init_balance():
    init_balance = request.form.get('txtInitBalance', 0)
    result = mainDB.set_init_balance(init_balance)
    return {'result':result}

@app.route('/stock/entrust_order', methods=['POST'])
@login_required
def stock_entrust_order():
    from scraper import ggfinance
    stockid = request.form['stockID']
    ent_num = int(request.form['entNum'])
    ent_action = request.form['entAction']
    stockex = mainDB.get_stockex(stockid)
    if stockex:
        balance = mainDB.get_passbook_balance(session['account'])
        stockpp = ggfinance.get_stock_price(stockex)
        sprice = float(stockpp[1]['sprice'].lstrip('$').replace(',',''))
        amount = ent_num * sprice * 1000
        inv_num = int(mainDB.get_stock_inv(session['account'], stockid))
        if ent_action == 'buy' and balance < amount:
            return {'result':False, 'msg':'帳戶餘額不足'}
        elif ent_action == 'sell' and inv_num < ent_num:
            return {'result':False, 'msg':'股票庫存不足'}
        else:
            adict = {
                'stockid':stockid,
                'stitle':stockpp[1]['stitle'],
                'sprice':sprice,
                'ent_num':ent_num,
                'ent_action':ent_action,
                'amount':amount
            }
            result = mainDB.entrust_order(session['account'], adict)
            return {'result':result, 'msg':'交易完成'}
    else:
        return {'result':False, 'msg':'股票代碼錯誤'}
    
@app.route('/stock/inventory_list')
@login_required
def stock_inventory_list():
    from scraper import ggfinance
    
    inventory = mainDB.get_stock_inventory(session['account'])
    for stockid, sdict in inventory.items():
        stockpp = ggfinance.get_stock_price(sdict['stockex'])
        sdict['mcost'] = mc = f"{sdict['mcost']:.2f}"
        if stockpp[0]:
            sdict['sprice'] =  sp = stockpp[1]['sprice'].strip('$').replace(',','')
            formula = f"({sp}-{mc})*{sdict['inv_num']}"
            sdict['profitloss'] = eval(formula)
            sdict['profitloss'] = f"{sdict['profitloss']*1000:.0f}"
            roi = eval(f"({sp}-{mc})/{mc}*100")
            sdict['roi'] = f"{roi:.2f}%"
        else:
            sdict['sprice'] = '-'
            sdict['profitloss'] = '-'
            sdict['roi'] = '-'
    return {'inventory': inventory}
    
@app.route('/stock-orders')
@login_required
def stock_orders():
    return render_template('stock/stock-orders.html', nowid=nowid())

@app.route('/stock-profitloss')
@login_required
def stock_profitloss():
    return render_template('stock/stock-profitloss.html', nowid=nowid())
    
@app.route('/stock/orders_list')
@login_required
def stock_orders_list():
    orders = mainDB.get_stock_orders(session['account'])
    if orders:
        for orderid, odict in orders.items():
            odict['sprice'] = f"{odict['sprice']:.2f}"
    return {'orders':orders}

@app.route('/stock/profitloss_list')
@login_required
def stock_profitloss_list():
    profitloss_list = mainDB.get_stock_profitloss(session['account'])
    if profitloss_list:
        for tdate, pldict in profitloss_list.items():
            pldict['total_cost'] = pldict['plnum'] * pldict['plcost'] * 1000
            pldict['total_revenue'] = pldict['plnum'] * pldict['plprice'] * 1000
            
            pldict['plcost'] = f"{pldict['plcost']:.2f}"
            pldict['plprice'] = f"{pldict['plprice']:.2f}"
            pldict['difference'] = pldict['total_revenue'] - pldict['total_cost']
            pldict['roi'] = round((pldict['difference'] / pldict['total_cost']) * 100, 2)
        return {'profitloss': profitloss_list}
    return {'profitloss':{}}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)