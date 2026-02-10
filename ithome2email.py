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

def fetch_ithome_hotnews():
    """
    爬取IT之家（ithome.com）热点新闻，返回整理好的字符串。
    如果爬取失败，返回错误信息。
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = 'https://www.ithome.com/'
        print(f"正在爬取 {url} ...")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # 尝试多种选择器来定位热点新闻
        hot_news = []
        # 1. 查找class包含"hot"的div
        hot_div = soup.find('div', class_=lambda c: c and 'hot' in c.lower())
        if hot_div:
            links = hot_div.find_all('a', href=True)
            for a in links:
                title = a.get_text(strip=True)
                href = a['href']
                if title and len(title) > 2:
                    if not href.startswith('http'):
                        href = 'https://www.ithome.com' + href if href.startswith('/') else href
                    hot_news.append((title, href))
        
        # 2. 如果上面没找到，尝试查找class包含"news"或"list"的ul/ol
        if not hot_news:
            for tag in soup.select('ul, ol'):
                if 'news' in tag.get('class', []) or 'list' in tag.get('class', []):
                    for a in tag.find_all('a', href=True):
                        title = a.get_text(strip=True)
                        href = a['href']
                        if title and len(title) > 2:
                            if not href.startswith('http'):
                                href = 'https://www.ithome.com' + href if href.startswith('/') else href
                            hot_news.append((title, href))
        
        # 3. 如果还是没找到，提取首页上所有看起来像新闻的链接
        if not hot_news:
            all_links = soup.find_all('a', href=True)
            for a in all_links:
                title = a.get_text(strip=True)
                href = a['href']
                # 过滤掉太短的标题和非新闻链接
                if title and len(title) > 10 and '/html/' in href:
                    if not href.startswith('http'):
                        href = 'https://www.ithome.com' + href if href.startswith('/') else href
                    hot_news.append((title, href))
        
        # 去重
        seen = set()
        unique_news = []
        for title, href in hot_news:
            if title not in seen:
                seen.add(title)
                unique_news.append((title, href))
        
        # 限制数量
        unique_news = unique_news[:15]
        
        if unique_news:
            news_lines = []
            for i, (title, href) in enumerate(unique_news, 1):
                news_lines.append(f"{i}. {title}\n   {href}")
            return "IT之家热点新闻：\n\n" + "\n\n".join(news_lines)
        else:
            return "未能找到热点新闻，可能页面结构已变化。"
    
    except requests.exceptions.RequestException as e:
        return f"网络请求失败：{e}"
    except Exception as e:
        return f"爬取过程中出现错误：{e}"

# -------------------------- 配置邮件参数 --------------------------
# 发件人邮箱（需开启SMTP，替换成你的）
sender = "3951015514@qq.com"
# 发件人邮箱的SMTP授权码（替换成你的）
auth_code = "gtpruuwjzupacefa"
# 收件人邮箱（可写多个，用逗号分隔）
receivers = ["aydinid@outlook.com"]

# 获取热点新闻内容
print("开始爬取IT之家热点新闻...")
mail_content = fetch_ithome_hotnews()
print("爬取完成，内容长度：", len(mail_content))

# 构建邮件对象
message = MIMEText(mail_content, 'plain', 'utf-8')
# 邮件主题
message['Subject'] = Header('IT之家热点新闻推送', 'utf-8')

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
