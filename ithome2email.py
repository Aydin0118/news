import smtplib
from email.mime.text import MIMEText
from email.header import Header
import sys

# 检查必要的第三方库
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("错误：缺少必要的第三方库。")
    print("请运行以下命令安装：")
    print("pip install requests beautifulsoup4")
    sys.exit(1)


url='https://www.ithome.com/block/rank.html'



wz = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

res = requests.get(url, headers=wz)

#open("视频.html", "wb").write(res.content)

print(res.status_code)

# -------------------------- 配置邮件参数 --------------------------
# 发件人邮箱（需开启SMTP，替换成你的）
sender = "3951015514@qq.com"
# 发件人邮箱的SMTP授权码（替换成你的）
auth_code = "gtpruuwjzupacefa"
# 收件人邮箱（可写多个，用逗号分隔）
receivers = ['abcdpx@qq.com']

# 获取热点新闻内容
print("开始爬取IT之家热点新闻...")
mail_content = res.content
print("爬取完成，内容长度：", len(mail_content))

# 构建邮件对象
message = MIMEText(mail_content, 'html', 'utf-8')
# 邮件主题
message['Subject'] = Header('IT之家日榜推送', 'utf-8')

# ========== 关键修改：调整From字段格式 ==========
# 方式1：最简合规格式（推荐）- 直接用邮箱地址，无多余名称
message['From'] = sender
# 方式2：带显示名称的合规格式（如需显示自定义名称）
# message['From'] = f"{Header('自定义发件人名称', 'utf-8')} <{sender}>"

# 收件人字段（保持不变）
message['To'] = ",".join(receivers)

# -------------------------- 发送邮件 --------------------------
try:
    # 连接QQ邮箱SMTP服务器
    smtp_obj = smtplib.SMTP_SSL("smtp.qq.com", 465)
    # 登录
    smtp_obj.login(sender, auth_code)
    # 发送邮件
    smtp_obj.sendmail(sender, receivers, message.as_string())
    smtp_obj.quit()
    print("邮件发送成功！")
except smtplib.SMTPException as e:
    print(f"邮件发送失败！错误信息：{e}")
