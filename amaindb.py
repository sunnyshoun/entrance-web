import os
from datetime import datetime
from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from email_validator import validate_email, EmailNotValidError
import pytz
import utils

app = Flask(__name__)

class MAINDB():
    def __init__(self):
        dbkey = os.path.join(app.root_path, 'firebase-dbkey.json')
        dburl = '-----'
        try:
            cred = credentials.Certificate(dbkey)
            firebase_admin.initialize_app(cred, {'databaseURL': dburl})
        except:
            pass
        self.ref = db.reference()

    def get_now(self):
        taipei = pytz.timezone('Asia/Taipei')
        now = datetime.now(taipei)
        return now.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_today(self):
        today = self.get_now()[:10]
        return today

    def get_any_data(self, data_path):
        ref_child = self.ref.child(data_path)
        return ref_child.get()

    def aet_alist(self, data_path):
        alist = self.get_any_data(data_path)
        if isinstance(alist, list):
            return alist
        return None

    def get_arow(self, data_path):
        arow = self.get_any_data(data_path)
        if isinstance(arow, dict):
            return arow
        return None

    def get_acol(self, data_path):
        acol = self.get_any_data(data_path)
        if isinstance(acol, str) or isinstance(acol, int) or isinstance(acol, float):
            return acol
        return None

    def get_users(self):
        return self.get_any_data('main-users')
    
    def show_users(self):
        adict = self.get_users()
        for akey, bdict in adict.items():
            print(f'{akey} /')
            for bkey,bval in bdict.items():
                if bkey == 'password':
                    print(f'{bkey}: ********')
                else:
                    print(f'{bkey}: {bval}')
            print()
    
    def get_userid(self, email):
        try:
            valid = validate_email(email)
            email = valid.email
            return email.replace('.','').strip().split('@')[0]
        except EmailNotValidError as e:
            return 'EmailNotValidError'
            
    def signin(self, email, password):
        userid = self.get_userid(email)
        error_msg = ''
        if userid == 'EmailNotValidError':
            error_msg = '請輸入 Email 帳號'
            
        if not error_msg:
            ref_child = self.ref.child(f'main-users/{userid}')
            user_info = ref_child.get()
            if user_info['email'] == email:
                if user_info['password'] == password and user_info['active']:
                    ref_child.child('signindt').set(self.get_now())
                    return user_info, True, ''
                elif user_info['password'] != password:
                    error_msg = '登入失敗：密碼錯誤'
                else:
                    error_msg = '登入失敗：帳號尚未啟用'
            else:
                error_msg = f'{email} 尚未註冊'
        return {}, False, error_msg
            
    def signup(self, email, password):
        userid = self.get_userid(email)

        if userid == 'EmailNotValidError':
            return {}, False, '請輸入帳號'
        ref_child = self.ref.child(f'main-users/{userid}')
        user_info = ref_child.get()
        
        if user_info:
            if user_info['active'] == True:
                sub_msg = '已經啟用，可以登入'
            else:
                sub_msg = '已經註冊，尚未啟用'
            return {}, True, f"{user_info['email']} {sub_msg}"
        
        ref_child.set({
            'email': email,
            'name': userid,
            'password': password,
            'group': 'rookie',
            'role': 'user',
            'classid': '',
            'signupdt': self.get_now(),
            'signindt': '',
            'active': False
        })
        result = self.send_activation(email)
        return {}, True, result
    
    def reset_password(self, email):
        userid = self.get_userid(email)
        if userid == 'EmailNotValidError':
            return '請輸入 Email 帳號'

        subject = f'掌聲股利 - 魔法密語重製 ({self.get_now()})'
        actlink = f'{utils.app_host}/resetpassword/{userid}'
        embody = render_template('email/password.html', actlink=actlink)
        utils.send_email(subject, embody, recipient=email)
        return '請至 Email 信箱重製魔法密語'
        
    def send_activation(self, email):
        userid = self.get_userid(email)
        if userid == 'EmailNotValidError':
            return '請輸入 Email 帳號'
        
        act_hash = utils.get_sha2(email+self.get_now(), 1)
        ref_child = self.ref.child(f'main-activations/{userid}')
        ref_child.set({
            'act_hash': act_hash,
            'actdt': '',
        })
        
        subject = f'掌聲股利 - 魔法通行證 ({self.get_now()})'
        actlink = f'{utils.app_host}/activate_account/{userid}/{act_hash}'
        embody = render_template('email/activation.html', actlink=actlink)
        utils.send_email(subject, embody, recipient=email)
        return '請到您輸入的 Email 信箱接收魔法通行證'
    
    def activate_user(self, userid, act_hash):
        ref_child = self.ref.child(f'main-activations/{userid}')
        act_info = ref_child.get()
        if act_info and act_info['act_hash'] == act_hash:
            ref_child.child('actdt').set(self.get_now())
            ref_child = self.ref.child(f'main-users/{userid}')
            ref_child.child('active').set(True)
            
            self.open_account(userid)
            return True
        return False
    
    def pw_reset(self, userid, password):
        ref_child = self.ref.child(f'main-users/{userid}')
        ref_child.child('password').set(password)
        
    def get_init_balance(self):
        return self.ref.child('main-settings/init_balance').get()
    
    def set_init_balance(self, balance):
        try:
            balance - int(balance)
        except:
            balance = 3000000
        self.ref.child('main-settings').child('init_balance').set(balance)
        return True
    
    def open_account(self, userid):
        ref_child = self.ref.child(f'main-passbooks/{userid}')
        init_balance = self.get_init_balance()
        ref_child.set({
            self.get_now():{
                'date': self.get_today(),
                'memo': '系統存入',
                'withdrawal': 0,
                'deposit': init_balance,
                'balance': init_balance,
                'remarks': '開戶預設'
            }
        })
        
    def get_passbook(self, account):
        userid = self.get_userid(account)
        return self.get_any_data(f'main-passbooks/{userid}')
    
    def get_passbook_last_row(self, userid):
        rows = self.ref.child(f'main-passbooks/{userid}').order_by_key().limit_to_last(1).get()
        last_row = list(rows.values())[0]
        return last_row
    
    def get_passbook_balance(self, account):
        userid = self.get_userid(account)
        last_row = self.get_passbook_last_row(userid)
        return last_row['balance']
    
    def get_stockex(self, stockid):
        ref_child = self.ref.child(f'main-stocks/{stockid}/stockex')
        return ref_child.get()
    
    def get_stocks(self):
        return self.get_any_data('main-stocks')
    
    def save_stock(self, **row):
        stockid = row['txtStockID']
        data = list(row.values())
        empty_cols = 0
        
        for col in data:
            if len(col.strip()) == 0:
                empty_cols += 1
        
        if empty_cols == 0:
            ref_child = self.ref.child('main-stocks/'+stockid)
            ref_child.child('stockid').set(stockid)
            ref_child.child('stockex').set(row['txtStockEx'])
            ref_child.child('currency').set(row['selCurrency'])
            ref_child.child('name').set(row['txtName'])
            ref_child.child('fullname').set(row['txtFullname'])
            
    def drop_stock(self, **row):
        stockid = row['txtStockID']
        ref_child = self.ref.child('main-stocks/'+stockid)
        
        ref_child.set({})
    
    def get_stock_orders(self,account):
        userid = self.get_userid(account)
        return self.get_any_data(f'stock-orders/{userid}')
    
    def get_stock_profitloss(self, account):
        userid = self.get_userid(account)
        return self.get_any_data(f'stock-profitloss/{userid}')
    
    def get_stock_inventory(self, account):
        userid = self.get_userid(account)
        adict = self.get_any_data(f'stock-inventory/{userid}')

        if not adict:
            return {}
        for stockid, bdict in adict.items():
            bdict['name'] = self.get_acol(f'main-stocks/{stockid}/name')
            bdict['stockex'] = self.get_acol(f'main-stocks/{stockid}/stockex')
        
        return adict
        
    def get_stock_inv(self, account, stockid):
        userid = self.get_userid(account)
        inv_num = self.get_acol(f'stock-inventory/{userid}/{stockid}/inv_num')
        if inv_num is None:
            return 0
        else:
            return inv_num
    
    def get_stock_info(self, stockid):
        return self.get_arow(f'main-stocks/{stockid}')
    
    def entrust_order(self, account, order_row):
        userid = self.get_userid(account)
        stockid = order_row['stockid']
        passbook_last_row = self.get_passbook_last_row(self.get_userid(account))
        
        order_row['stitle'] = self.get_stock_info(stockid)['name']
        
        passbook_row = dict(passbook_last_row)
        passbook_row['data'] = self.get_today()
        passbook_row['memo'] = order_row['stitle']
        if order_row['ent_action'] == 'buy':
            passbook_row['balance'] -= order_row['amount']
            passbook_row['deposit'] = 0
            passbook_row['withdrawal'] = order_row['amount']
            passbook_row['remarks'] = '集買'
            order_row['amount'] = -order_row['amount']
        elif order_row['ent_action'] == 'sell':
            passbook_row['balance'] += order_row['amount']
            passbook_row['deposit'] = order_row['amount']
            passbook_row['withdrawal'] = 0
            passbook_row['remarks'] = '集賣'
        
        profitloss_row = {}
        
        inventory_row = self.ref.child(f'stock-inventory/{userid}/{stockid}').get()
        
        if inventory_row:
            if order_row['ent_action'] == 'buy':
                
                prev_cost = inventory_row['mcost']
                prev_lots = inventory_row['inv_num']
                this_cost = order_row['sprice']
                this_lots = order_row['ent_num']
                
                stotal = prev_cost*prev_lots + this_cost*this_lots
                
                inventory_row['mcost'] = round(stotal / (prev_lots + this_lots), 2)
                inventory_row['inv_num'] += order_row['ent_num']
            elif order_row['ent_action'] == 'sell':
                inventory_row['inv_num'] -= order_row['ent_num']
                profitloss_row['stockid'] = stockid
                profitloss_row['stitle'] = order_row['stitle']
                profitloss_row['plnum'] = order_row['ent_num']
                profitloss_row['plcost'] = inventory_row['mcost']
                profitloss_row['plprice'] = order_row['sprice']
        else:
            inventory_row = {
                'inv_num':order_row['ent_num'],
                'mcost':order_row['sprice']
            }
        
        ref_child = self.ref.child(f'stock-orders/{userid}/{self.get_now()}')
        ref_child.set(order_row)
        
        ref_child = self.ref.child(f'stock-inventory/{userid}/{stockid}')
        ref_child.set(inventory_row)
        
        if inventory_row['inv_num'] == 0:
            ref_child = self.ref.child(f'stock-inventory/{userid}/{stockid}')
            ref_child.set({})
        
        ref_child = self.ref.child(f'main-passbooks/{userid}/{self.get_now()}')
        ref_child.set(passbook_row)
        
        if profitloss_row:
            ref_child = self.ref.child(f'stock-profitloss/{userid}/{self.get_now()}')
            ref_child.set(profitloss_row)
            
        return True