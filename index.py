#coding=utf-8
import requests
import time
RunLogin = int(input('是否拥有登录凭证(是 1/否 0):'))
Authorization = ''
UserName = ''
Password = ''
if RunLogin == 0:
    UserName = input('请输入用户名(登录手机号):')
    Password = input('请输入密码:')
    GetMyAuthUrl = 'https://api-tcoj.aicoders.cn/api/login'
    GetMyAuthHeaders = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    GetMyAuthData = {
        'username': UserName,
        'password': Password
    }
    GetMyAuthResponse = requests.post(GetMyAuthUrl, headers=GetMyAuthHeaders, json=GetMyAuthData)
    if GetMyAuthResponse.json()['message'] != 'success':
        print('登录失败，请检查用户名和密码是否正确。')
        exit(1)
    # 查看响应标头
    Authorization = GetMyAuthResponse.headers.get('Authorization')
    print('登录密钥:(您可以保存方便后续使用)')
    print(Authorization)
else:
    Authorization = input('请输入登录密钥:')
GetMyGroupListUrl = 'https://api-tcoj.aicoders.cn/api/get-mine-group-list'
GetMyGroupListHeaders = {
    'Authorization': Authorization,
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
GetMyGroupListResponse = requests.get(GetMyGroupListUrl, headers=GetMyGroupListHeaders)
# 查看响应内容
MyGroupList = GetMyGroupListResponse.json()['data']
MyGroupLen = len(MyGroupList)
UpPid = []
InquiryLimit = 100 # 每次查询提交记录的数量限制
print('您的团队数量:', MyGroupLen)
if MyGroupLen == 0:
    print('您没有加入任何团队，请先加入团队。')
    print('您的登录凭证可能已过期或错误，请重新登录。')
    exit(1)
print('Ps: 由于API限制，每次提交代码间隔9秒，请耐心等待。\n您可以直接把电脑放在一边，直接睡觉。\n如需退出，请按Ctrl+C。')
for i in range(MyGroupLen): # 遍历每一个组
    ThisGroupId = MyGroupList[i]['id']
    GetMySubmissionListUrl = f'https://api-tcoj.aicoders.cn/api/get-submission-list?onlyMine=true&status=0&currentPage=1&limit={InquiryLimit}&completeProblemID=false&gid={ThisGroupId}'
    GetMySubmissionListResponse = requests.get(GetMySubmissionListUrl, headers=GetMyGroupListHeaders)
    MySubmissionPageCount = GetMySubmissionListResponse.json()['data']['pages']
    # print('MySubmissionPageCount:', MySubmissionPageCount)
    for j in range(MySubmissionPageCount): # 遍历每一页提交记录
        GetMySubmissionListUrl = f'https://api-tcoj.aicoders.cn/api/get-submission-list?onlyMine=true&status=0&currentPage={j+1}&limit={InquiryLimit}&completeProblemID=false&gid={ThisGroupId}'
        GetMySubmissionListResponse = requests.get(GetMySubmissionListUrl, headers=GetMyGroupListHeaders)
        MySubmissionList = GetMySubmissionListResponse.json()['data']['records'] # 获取提交列表
        MySubmissionLen = len(MySubmissionList)
        for k in range(MySubmissionLen): # 遍历每一条提交记录
            ThisSubmissionId = MySubmissionList[k]['submitId']
            CodeUrl = f'https://api-tcoj.aicoders.cn/api/get-submission-detail?submitId={ThisSubmissionId}'
            CodeData = {'submitId': ThisSubmissionId}
            CodeResponse = requests.get(CodeUrl, headers=GetMyGroupListHeaders, json=CodeData)
            Code = CodeResponse.json()['data']['submission']['code']
            CodeLanguage = CodeResponse.json()['data']['submission']['language']
            CodePid = CodeResponse.json()['data']['submission']['pid']
            if CodePid in UpPid:
                continue
            CodeUpUrl = 'https://api-tcoj.aicoders.cn/api/submit-problem-judge'
            CodeUpData = {
                'cid': 0,
                'code': Code,
                'gid': 'null',
                'isRemote': False,
                'language': CodeLanguage,
                'pid': CodePid,
                'tid': 'null'
            }
            CodeUpResponse = requests.post(CodeUpUrl, headers=GetMyGroupListHeaders, json=CodeUpData)
            UpPid.append(CodePid)
            print()
            print('提交代码:', Code[:17] + '...')  # 只打印前17个字符
            print('提交语言:', CodeLanguage)
            print('提交题号:', CodePid)
            time.sleep(9)  # 避免请求过于频繁