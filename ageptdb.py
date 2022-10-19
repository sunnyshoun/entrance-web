import os
import json
from random import randint
from datetime import datetime
from flask import Flask
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import utils

app = Flask(__name__)

class GEPTDB():
    def __init__(self):
        dbkey = os.path.join(app.root_path, 'firebase-dbkey.json')
        dburl = '-----'
        try:
            cred = credentials.Certificate(dbkey)
            firebase_admin.initialize_app(cred, {'databaseURL': dburl})
        except:
            pass
        self.ref = db.reference()

        self.word_levels = {'w1': '初級', 'w2': '中級', 'w3': '中高'}
        self.type_questions = (10, 20, 25, 50, 100, 200)
        self.type_options = {
            'multiple_choice': {3: '三選一', 4: '四選一', 5: '五選一'},
            'fill_in_the_blank': {1: '提示首字母', 2: '提示首尾字母'}
        }

    def get_now(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def get_any_data(self, data_path):
        ref_child = self.ref.child(data_path)
        return ref_child.get()

    def init_settings(self):
        print('還原設定')
        ref_child = self.ref.child('gept-settings')
        ref_child.set({
            'multiple_choice': {
                'typename': '選擇題',
                'questions': 10,
                'option': 4
            },
            'fill_in_the_blank': {
                'typename': '填空題',
                'questions': 10,
                'option': 1
            }
        })
        print('清空試卷')
        self.ref.child('gept-tests').set({})
        print('清空成績')
        self.ref.child('gept-scores').set({})

    def get_settings(self):
        return self.get_any_data('gept-settings')

    def save_settings(self, new_sets):
        ref_child = self.ref.child('gept-settings')
        ref_child.set({
            'multiple_choice': {
                'typename': '選擇題',
                'questions': new_sets['selQnsMC'],
                'option': new_sets['selOptMC']
            },
            'fill_in_the_blank': {
                'typename': '填空題',
                'questions': new_sets['selQnsFB'],
                'option': new_sets['selOptFB']
            }
        })

    def show_settings(self):
        ref_child = self.ref.child('gept-settings')
        settings = ref_child.get()
        divider = '-'*30
        print(divider)
        if isinstance(settings, dict):
            json_settings = json.dumps(settings, sort_keys=True, indent=4)
            print(json_settings)
            print()

            for typeid, ss in settings.items():
                print('type:', typeid)
                if isinstance(ss, dict):
                    for key, value in ss.items():
                        print(' - {}: {}'.format(key, value))
        print(divider)

    def modify_settings(self):
        opt = input('a.選擇題  b.填空題  q.離開: ')[0].lower()
        if opt == 'q':
            return
        elif opt == 'a':
            typeid = 'multiple_choice'
            typename = '選擇題'
            questions = int(input('請輸入題數: '))
            option = int(input('3.三選一 4.四選一 5.五選一: '))
        elif opt == 'b':
            typeid = 'fill_in_the_blank'
            typename = '填空題'
            questions = int(input('請輸入題數: '))
            option = int(input('1.提示首字母 2.提示首尾字母: '))

        ref_child = self.ref.child('gept-settings/' + typeid)
        ref_child.set({'typename': typename, 'questions': questions, 'option': option})

    def get_test_id(self, i):
        now = datetime.now()
        # idprefix = now.strftime("%y%m%d%H%M%S%f")[2:-4]
        idprefix = now.strftime("%y%m%d%f")[:-4]
        return '-'.join((idprefix, str(i+1).zfill(3)))

    def get_test_id_hash(self, i):
        now = datetime.now()
        return utils.get_sha2(now.strftime("%y%m%d%H%M%S%f"),'256')
    
    def get_test_args(self, req_post):
        test_args = {
            'wlevel': req_post['WordLevel'],
            'type_id': req_post['TypeID'],
            'test_id': req_post['TestID']
        }
        return test_args

    def reset_tests(self):
        ref_child = self.ref.child('gept-tests')
        ref_child.set({})

    def get_tests(self):
        return self.get_any_data('gept-tests')

    def save_tests(self, wlevel, tests_num, list_words, settings, dict_types):
        if tests_num > 10:
            tests_num = 10

        # 新增測驗
        for type_id, type_val in dict_types.items():
            if type_val == 1:
                dict_tests = {}
                option = settings[type_id]['option']
                questions = settings[type_id]['questions']

                for i in range(tests_num):
                    test_id = self.get_test_id_hash(i)
                    dict_tests[test_id] = []
                    for q in range(questions):
                        dict_q = {'quid':q}
                        # 設定填充題
                        if type_id == 'fill_in_the_blank':
                            ex_word = list_words[0]
                            del list_words[0]
                            dict_q['ans'] = ex_word[1]
                            dict_q['qhint'] = ex_word[2]

                            dict_q['qtest'] = ex_word[1][0] + ' _'*(len(ex_word[1])-option)
                            if option == 2:
                                dict_q['qtest'] = dict_q['qtest'] + ' ' + ex_word[1][-1]
                        # 設定選擇題
                        elif type_id == 'multiple_choice':
                            ex_words = list_words[:option]
                            del list_words[:option]
                            ans = randint(1, option)
                            qwords = []
                            for windex, word in enumerate(ex_words):
                                if windex == ans-1:
                                    dict_q['ans'] = ans
                                    dict_q['qtest'] = word[2]
                                qwords.append(word[1])
                            dict_q['qwords'] = ','.join(qwords)

                        # 新增題目
                        dict_tests[test_id].append(dict_q)
                ref_child = self.ref.child('gept-tests/{}/{}/{}'.format(wlevel, type_id, test_id))
                ref_child.set(dict_tests[test_id])
                return test_id

    def read_test(self, test_args):
        return self.get_any_data('gept-tests/{wlevel}/{type_id}/{test_id}'.format(**test_args))

    def init_examinees(self):
        ref_child = self.ref.child('gept-examinees')
        names = ('apple', 'banana', 'cherry', 'durian')
        for name in names:
            sub_child = ref_child.child(name)
            sub_child.set({
                'account': name,
                'username': name,
                'password': f'{name}87',
            })

    def get_examinees(self):
        return self.get_any_data('gept-examinees')

    def show_examinees(self):
        adict = self.get_examinees()
        for akey, bdict in adict.items():
            print(f'{akey} /')
            for bkey, bval, in bdict.items():
                print(f'{bkey}: {bval}')
            print()

    def check_examinee(self, examinee_id, examinee_pw):
        examinee = self.get_any_data('gept-examinees/{}'.format(examinee_id))
        if examinee == {} or examinee_id.strip() == '':
            return False, {}
        elif examinee_pw != examinee['password']:
            return False, {}
        else:
            return True, examinee

    def save_examinee(self, row):
        examinee_data = list(row.values())
        empty_cols = 0
        # 所有欄位必填資料
        for col in examinee_data:
            if len(col.strip()) == 0:
                empty_cols += 1
        # 新增或更新考生資料
        if empty_cols == 0:
            ref_child = self.ref.child('gept-examinees/'+row['txtAccount'])
            ref_child.set({
                'account': row['txtAccount'],
                'username': row['txtName'],
                'password': row['txtPassword']
            })

    def drop_examinee(self, row):
        ref_child = self.ref.child('gept-examinees/'+row['txtAccount'])
        # 設空 {} 表示刪除
        ref_child.set({})
        # 刪除成績
        ref_child = self.ref.child('gept-scores/'+row['txtAccount'])
        ref_child.set({})

    def save_score(self, score, test_args):
        ref_child = self.ref.child('gept-scores/{}'.format(test_args['test_id']))
        ref_child.set({
            'wlevel': test_args['wlevel'],
            'type_id': test_args['type_id'],
            'score': score,
            'test_time': self.get_now()
        })

    def get_scores(self):
        return self.get_any_data('gept-scores')

    def get_score_examinee(self, examinee_id):
        return self.get_any_data('gept-scores/{}'.format(examinee_id))


if __name__ == '__main__':
    geptDB = GEPTDB()
    is_init = input('是否重新設定 (y/N)? ').lower()
    if is_init == 'y':
        geptDB.init_settings()
        geptDB.init_examinees()

    while True:
        opt = input('1.顯示設定  2.修改設定  3.顯示帳號  0.離開: ')[0]
        if opt == '0':
            break
        elif opt == '1':
            geptDB.show_settings()
        elif opt == '2':
            geptDB.modify_settings()
        elif opt == '3':
            geptDB.show_examinees()
    