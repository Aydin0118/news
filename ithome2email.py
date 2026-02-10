import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
import time
from smtplib import SMTPException

# ---------------------- 配置项（从GitHub Secrets读取） ----------------------
# 发件人信息
smtp_server = "smtp.office365.com"
smtp_port = 587

with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
    server.starttls()
    server.login('aydinid@outlook.com', 'qwertyuiop00')  # 这里用邮箱密码，不是授权码

# 收件人信息
receiver_email = os.getenv("RECEIVER_EMAIL")  # 收件人邮箱（可多个，用逗号分隔）

# ---------------------- 爬取IT之家热点 ----------------------
def crawl_ithome():
    """爬取IT之家首页热点资讯"""
    url = "https://www.ithome.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.ithome.com/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    try:
        # 发送请求，设置超时
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误
        response.encoding = "utf-8"
        
        # 解析页面
        soup = BeautifulSoup(response.text, "html.parser")
        # 定位热点资讯区域（IT之家首页热点的class，若后续页面更新需调整）
        hot_news = soup.find_all("div", class_="pho_cont")[:10]  # 取前10条热点
        
        # 构建邮件内容（HTML格式）
        email_content = "<h2>📰 IT之家今日热点（Top10）</h2><ul>"
        for idx, news in enumerate(hot_news, 1):
            # 提取标题和链接
            title_tag = news.find("a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = "https://www.ithome.com" + title_tag.get("href", "")
            
            # 拼接每条资讯
            email_content += f"<li><strong>{idx}.</strong> <a href='{link}'>{title}</a></li>"
        email_content += "</ul><p>🔔 每日自动推送，数据来源：IT之家</p>"
        
        return email_content
    
    except Exception as e:
        print(f"爬取失败：{str(e)}")
        return f"<h3>爬取失败</h3><p>错误信息：{str(e)}</p>"

# ---------------------- 发送邮件 ----------------------
def send_email(content, max_retries=3):
    """发送HTML格式邮件，带重试机制"""
    retries = 0
    while retries < max_retries:
        try:
            # 构建邮件对象
            msg = MIMEText(content, "html", "utf-8")
            msg["From"] = Header(f"IT之家每日推送 <{sender_email}>", "utf-8")
            msg["To"] = Header(receiver_email, "utf-8")
            msg["Subject"] = Header("📮 IT之家今日热点推送", "utf-8")
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
                server.login(sender_email, sender_auth_code)
                server.sendmail(sender_email, receiver_email.split(","), msg.as_string())
            
            print("邮件发送成功！")
            return
        
        except (SMTPException, ConnectionError) as e:
            retries += 1
            print(f"邮件发送失败，重试 {retries}/{max_retries}：{str(e)}")
            time.sleep(5)  # 等待5秒后重试
    
    print("邮件发送失败，已达到最大重试次数。")
    raise Exception("邮件发送失败")

# ---------------------- 主函数 ----------------------
if __name__ == "__main__":
    # 1. 爬取内容
    news_content = crawl_ithome()
    # 2. 发送邮件
    send_email(news_content)
