enable_mail = False  # 此行表示是否发送邮件提醒，设置为 True 发邮件
smtp_server = 'smtp.qq.com'  # 此行表示 smtp 服务器地址
smtp_username = 'xxx@qq.com'  # 此行表示发件人邮箱地址
smtp_password = 'xxx'  # 此行表示发件人邮箱密码
smtp_to = 'xxx@qq.com'  # 此行表示收件人邮箱地址
smtp_ssl = True  # 此行表示连接邮箱是否使用 SSL

student_no = 'xxx'  # 此行表示登录统一身份认证系统的学号
cas_password = 'xxx'  # 此行表示登录统一身份认证系统的密码

req_timeout = 10  # 此行表示向服务器发查询请求的超时时间（单位：秒）
interval = 60  # 此行表示两次查询的间隔时间（单位：秒）

#是否开启微信通知新成绩功能，如果开启，必须填写下面的sckey
enable_wechat = True
#微信通知功能使用了Server酱提供的API
#获取SCUKEY的方式见：http://sc.ftqq.com/3.version
#按照网页上前两步指示“登入”和“绑定”做，然后把获得的SCKEY填入下一行
sckey = 'xxx'