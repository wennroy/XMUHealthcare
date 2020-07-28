# -*- coding: utf-8 -*-
"""
Spyder 编辑器

这是一个临时脚本文件。
"""
import requests
import json
from bs4 import BeautifulSoup as bs

# username =
# password = 
def login(username,password):
    r = requests.Session() ## 保持会话https://blog.csdn.net/weixin_42575020/article/details/95179840
    login_url = 'https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu'
    resp1 = r.get(login_url, headers=headers)
    resp1_bs = bs(resp1.text, 'lxml')
    lt = resp1_bs.find('input',attrs = {'name': 'lt'})['value']
    form = {'username': username, 'password': password, 'lt':lt, 'dllt': 'userNamePasswordLogin', 
            'execution': 'e1s1', '_eventId': 'submit','rmShwon': '1', 'rememberMe': 'on'}
    '''
    username: 152xxx
    password: xxxxxx
    lt: LT-556372-O5B9wu3DoO0nB7QxT0h9JsWGgGaQcc1594793971344-NwJs-cas
    dllt: userNamePasswordLogin
    execution: e1s1
    _eventId: submit
    rmShown: 1
    '''
    r.post('https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu',\
                  data = form, headers = headers)
    resp2 = r.get('https://xmuxg.xmu.edu.cn/login/check', headers = headers)
    try:
        name = resp2.json()['data']['name']
        print(f'登陆成功！欢迎您，{name}')
        return r
    except Exception as e:
        print(str(e))
        print('登陆失败')
        raise e

def main():
        
    username = input('输入学号\n')
    password = input('输入密码\n')
    print('登陆中....')
    s = login(username, password)
    '''
    获得最近十四天得打卡情况
    '''
    myform_url = 'https://xmuxg.xmu.edu.cn/api/formEngine/business/644/myFormInstance'
    res = s.get(myform_url, headers = headers)
    res_dict = res.json()
    res_table_value = res_dict['data']['formData'][12]['value']['tableValue']
    no_daka = [0]
   
    for i in range(len(res_table_value)):
        temp_dict = res_table_value[i]
        yesorno = temp_dict['rowData'][4]['value']['stringValue']
        if not yesorno == '是 Yes':
            no_daka.append(i+1)
    temp_str = '0'
    for i in no_daka:
        if i == 0:
            continue
        temp_str += '、' + str(i)
    if temp_str == '0':
        print('您前14天都有坚持打卡，是否打今天的卡？(懒得再查询今天到底有没有打卡了，要打卡默认帮你打上)')
        des = input('输入0打今天的卡，输入-1不打卡，输入其他数字为打对应数字(前n天的卡)\n')
    else:
        print('检测到您有前%s天没有打卡(默认帮您打上今天的卡)'%(temp_str))
        des = input('输入-2打以上天数的卡，输入0打今天的卡，输入-1不打卡\n')
    des = int(des)
    '''
     today_url = 'https://xmuxg.xmu.edu.cn/api/formEngine/business/901/table/fields?playerId=owner'
    '''
    if des == -1:
        print('感谢使用本垃圾打卡系统')
        return
    elif des == 0:
        no_daka = [0]
    elif des >= 1:
        no_daka = []
        [no_daka.append(x) for x in range(round(des))]
        
    resp = s.get('https://xmuxg.xmu.edu.cn/api/app/214/business/now')
    form_dict = resp.json()
    Headers = {'content-type': 'application/json'}
    # change deate in below line ()
    # print(no_daka)
    first_date = form_dict['data'][0]['business']['name']
    import datetime
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if not first_date == today:
    ## 如果检测到当前要填写的表单不是当天的，那么需要找到哪一个表单是今天的，然后向前推
        for i in range(len(form_dict['data'])):
            datei = form_dict['data'][0]['business']['name']
            if today==datei:
                break
        for k in range(len(no_daka)):
            no_daka[k] += i

    for i in no_daka:
        businessId = form_dict['data'][i]['business']['id']
        datei = form_dict['data'][i]['business']['name']
        resp = s.get(f'https://xmuxg.xmu.edu.cn/api/formEngine/business/{businessId}/myFormInstance')
        myFormJson = resp.json()
        formid = myFormJson['data']['id']

        form_url = f'https://xmuxg.xmu.edu.cn/api/formEngine/formInstance/{formid}'
        false = 'false'
        true = 'true'
        form_data = {"formData": [
            {"name": "select_1582538796361", "title": "今日体温 Body temperature today （℃）",
             "value": {"stringValue": "37.3以下 Below 37.3 degree celsius"}, "hide": false},
            {"name": "select_1582538846920",
             "title": "是否出现发热或咳嗽或胸闷或呼吸困难等症状？Do you have sypmtoms such as fever, coughing, chest tightness or breath difficulties?",
             "value": {"stringValue": "否 No"}, "hide": false},
            {"name": "select_1584240106785", "title": "学生本人是否填写", "value": {"stringValue": "是"},
             "hide": false}, {"name": "select_1582538939790",
                              "title": "Can you hereby declare that all the information provided is all true and accurate and there is no concealment, false information or omission. 本人是否承诺所填报的全部内容均属实、准确，不存在任何隐瞒和不实的情况，更无遗漏之处。",
                              "value": {"stringValue": "是 Yes"}, "hide": false},
            {"name": "input_1582538924486", "title": "备注 Notes", "value": {"stringValue": ""},
             "hide": false}], "playerId": "owner"}
        print(f'正在打{datei}天的卡')
        resp = s.post(form_url, data=json.dumps(form_data), headers=Headers)
        print('检测是否打卡成功中...')
        resp = s.get(f'https://xmuxg.xmu.edu.cn/api/formEngine/business/{businessId}/myFormInstance')
        success_Json = resp.json()
        update_time = success_Json['data']['updateTime']
        if update_time.split(' ')[0] == today:
            print(f'打卡成功！{datei}天的打卡时间为{update_time}，与系统时间天数{today}匹配。(若在半夜十二点附近可能会检测失败)')
        else:
            print(f"打卡失败，{datei}天的打卡时间{update_time}与当前系统天数{today}不匹配")
    print('打卡完毕!')

if __name__ == '__main__':
    headers = { 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
        }
    main()