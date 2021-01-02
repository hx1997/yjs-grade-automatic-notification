#!/usr/bin/env python3
import logging
import time

import requests
from bs4 import BeautifulSoup

import shutil
import config
import muggle_ocr
import json
import re
from mail import send_email

s = requests.session()

io_enabled = True
def log(type, message, *args):
    global io_enabled
    if not io_enabled: return
    if type == 'info':
        logging.info(message, *args)
    elif type == 'warning':
        logging.warning(message, *args)
    elif type == 'error':
        logging.error(message, *args)
    elif type == 'exception':
        logging.exception(message, *args)

def recognize(img_path):
    sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.OCR)
    with open('img.jpg', 'rb') as f:
        b = f.read()
        text = sdk.predict(image_bytes=b)
    return text

def cas_login():
    log('info', 'Logging in')
    url = 'http://202.206.3.95/login.do'
    captcha = 'http://202.206.3.95/captcha.jpg'
    s.get(url, timeout=config.req_timeout)
    r = s.get(captcha, stream=True)
    with open('img.jpg', 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
    try:
        text = recognize('img.jpg')
        log('info', text)
    except ValueError:
        return False
    getDanDianInfo = 'http://202.206.3.95/getDanDianInfo.do'
    r = s.post(getDanDianInfo, data={
        'm': 'getLoginInfo',
        'username': config.student_no,
        'pwd': config.cas_password
    }, timeout=config.req_timeout)
    DanDianInfo = r.content.decode('gbk')
    if 'success' in DanDianInfo:
        log('info', 'GetDanDianInfo success')
    else:
        log('error', 'GetDanDianInfo failed')
        return False

    r_json = json.loads(DanDianInfo)
    login_url = 'http://202.206.3.95/j_acegi_login.do'
    r = s.post(login_url, data={
        'm': 'getLoginInfo',
        'j_username': config.student_no,
        'j_password': r_json['password'],
        'j_captcha_response': text,
        'login': 'tongyi'
    }, timeout=config.req_timeout)
    if 'http://202.206.3.95/main.do' in r.url:
        log('info', 'Login success')
        return True
    else:
        log('error', 'Login failed')
        return False

def get_grade():
    r = s.get('http://202.206.3.95/cjgl.v_allcj_yjs.do', timeout=config.req_timeout)
    grades = {}
    p = re.compile('var gridData = (.*?);', re.DOTALL)
    m = p.findall(r.content.decode('gbk'))
    raw_grades = json.loads(m[0])
    for subject in raw_grades:
        subject_name = subject[2]
        subject_score = subject[4]
        grades[subject_name] = subject_score
    log('info', grades)
    return grades

def send_wechat_notif(text):
    server_url = 'https://sc.ftqq.com/{}.send'.format(config.sckey)
    r = s.post(server_url, data={
        'text': '新成绩',
        'desp': text,
    }, timeout=config.req_timeout)
    if r.ok:
        return True
    else:
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s')
    last_grades = {}
    while not cas_login():
        logging.info('Retrying login...')
    logging.info('Fetching grades')

    while True:
        try:
            try:
                log('info', 'Testing I/O...')
            except IOError:
                io_enabled = False
            try:
                grades = get_grade()
                log('info', 'Count = %s', len(grades))
                with open('log.txt', 'a') as f:
                    f.write(str(grades))
            except IOError:
                pass
            except Exception as e:
                log('warning', 'Error occurred, trying to login again')
                cas_login()
            else:
                if grades != last_grades:
                    text = ', '.join(name + ' ' + grade for name, grade in grades.items() if name not in last_grades)
                    if config.enable_wechat:
                        while not send_wechat_notif(text):
                            log('warning', 'Failed to send WeChat notification, retrying...')
                    log('info', 'Sending email: %s', text)
                    if config.enable_mail:
                        send_email(text, text)
                        log('info', 'Mail sent')
                last_grades = grades
            finally:
                time.sleep(config.interval)
        except Exception as e:
            log('exception', e)
