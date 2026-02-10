import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup
import requests
import time

# ---------------------- 配置项（SMTP 服务器） ----------------------
smtp_server = "smtp.office365.com"
smtp_port = 587  # Outlook SMTP 端口（TLS 加密）

# ---------------------- 从 GitHub Secrets 读取敏感信息 ----------------------
sender_email = os.getenv("SMTP_USER")       # 发件人邮箱（对应 Secrets: SMTP_USER）
sender_auth_code = os.getenv("SMTP_PASSWORD")  # 应用密码（对应 Secrets: SMTP_PASSWORD）
receiver_email = os.getenv("RECEIVER_EMAIL")   # 收件人邮箱（对应 Secrets: RECEIVER_EMAIL）

# ---------------------- 爬取 IT 之家热点 ----------------------
def crawl_ithome():
    """爬取 IT 之家首页热点资讯"""
    url = "https://www.ithome.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.ithome.com/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 抛 HTTP 错误
        response.encoding = "utf-8"
        
        soup = BeautifulSoup(response.text, "html.parser")
        hot_news = soup.find_all("div", class_="pho_cont")[:10]  # 取前 10 条
        
        email_content = "<h2>📰 IT 之家今日热点（Top10）</h2><ul>"
        for idx, news in enumerate(hot_news, 1):
            title_tag = news.find("a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = "https://www.ithome.com" + title_tag["href"]
            email_content += f"<li><strong>{idx}.</strong> <a href='{link}'>{title}</a></li>"
        email_content += "</ul><p>🔔 每日自动推送，数据来源：IT 之家</p>"
        
        return email_content
    
    except Exception as e:
        print(f"爬取失败：{str(e)}")
        return f"<h3>爬取失败</h3><p>错误信息：{str(e)}</p>"

# ---------------------- 发送邮件（带重试） ----------------------
def send_email(content, max_retries=3):
    """发送 HTML 邮件，含重试机制"""
    retries = 0
    while retries < max_retries:
        try:
            # 构建邮件对象
            msg = MIMEText(content, "html", "utf-8")
            msg["From"] = Header(f"IT 之家每日推送 <{sender_email}>", "utf-8")
            msg["To"] = Header(receiver_email, "utf-8")
            msg["Subject"] = Header("📮 IT 之家今日热点推送", "utf-8")
            
            # 连接 SMTP 并发送（TLS 加密）
            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                server.starttls()  # 启动 TLS 加密（必做！）
                server.login(sender_email, sender_auth_code)  # 应用密码登录
                server.sendmail(sender_email, receiver_email.split(","), msg.as_string())
            
            print("邮件发送成功！")
            return
        
        except (smtplib.SMTPException, ConnectionError) as e:
            retries += 1
            print(f"邮件发送失败，重试 {retries}/{max_retries}：{str(e)}")
            time.sleep(5)  # 等待 5 秒后重试
    
    print("邮件发送失败，已达最大重试次数。")
    raise Exception("邮件发送失败")

# ---------------------- 主函数 ----------------------
if __name__ == "__main__":
    # 1. 爬取内容
    news_content = crawl_ithome()
    # 2. 发送邮件
    send_email(news_content)
