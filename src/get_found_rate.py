import requests
import re
import json
import smtplib
import time
import os
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from datetime import datetime

# ================= 配置区域 =================
SMTP_SERVER = 'smtp.qq.com'  # SMTP服务器
SMTP_PORT = 465  # SSL端口通常是465
SENDER_EMAIL = os.environ.get('SENDER_EMAIL') 
SENDER_PASS = os.environ.get('SENDER_PASS')

# 收件箱设置 (可以是同一个邮箱，也可以是你的手机139邮箱等)
RECEIVERS = [
    'ljz400216@163.com',
    '1282611712@qq.com'
]

# --- 🎯 我的自选基金 (在这里添加你关注的基金代码) ---
# 自选基金代码 (支持任意数量)
MY_WATCHLIST = ['161226', '270042','160644','017641','161128']

# 2025年底收盘基准价 (根据你的截图修正了2026年现价基准)
# 修正逻辑：现价1121，假设去年底约为1100左右，避免出现+70%的虚假涨幅
BASE_PRICE_GOLD = 980.9
BASE_PRICE_SILVER = 16730


# ===========================================

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "http://fund.eastmoney.com/",
    }


def get_filtered_funds():
    """获取榜单 Top 10"""
    url = "http://fund.eastmoney.com/data/rankhandler.aspx"
    params = {
        'op': 'ph', 'dt': 'kf', 'ft': 'all', 'rs': '', 'gs': '0',
        'sc': 'zzf', 'st': 'desc',
        'qdii': '', 'tabSubtype': ',,,,,',
        'pi': '1', 'pn': '100', 'dx': '1'
    }

    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=10)
        response.encoding = 'utf-8'
        match = re.search(r'datas\s*:\s*(\[.*?])', response.text)
        if not match: return None
        all_funds = json.loads(match.group(1))

        top_funds = []
        count = 0
        for item in all_funds:
            if count >= 10: break
            columns = item.split(',')
            if len(columns) < 15: continue
            code, name, week, month, year = columns[0], columns[1], columns[7], columns[8], columns[14]
            if any(k in name for k in ['债', '货币', '理财', '短融', '定开']): continue
            if name.upper().endswith("A") or "A类" in name: continue
            if not week or week == "": continue
            top_funds.append({'code': code, 'name': name, 'week': week, 'month': month, 'year': year})
            count += 1
        return top_funds
    except Exception as e:
        print(f"❌ 榜单获取错误: {e}")
        return None


def get_my_funds():
    """🎯 获取自选基金 (多重补全版)"""
    if not MY_WATCHLIST: return []
    my_funds_data = []

    print(f"   正在分析自选基金: {MY_WATCHLIST} ...")

    for code in MY_WATCHLIST:
        # 初始化默认值
        fund_info = {
            'code': code, 'name': '获取中...', 'date': '--',
            'day': '--', 'week': '--', 'month': '--', 'year': '--'
        }

        try:
            ts = int(time.time() * 1000)

            # --- 第1步：实时接口 (优先获取 日涨跌) ---
            try:
                url_real = f"http://fundgz.1234567.com.cn/js/{code}.js?rt={ts}"
                res_real = requests.get(url_real, headers=get_headers(), timeout=2)
                if res_real.status_code == 200:
                    start = res_real.text.find('{')
                    end = res_real.text.rfind('}')
                    if start != -1 and end != -1:
                        data_real = json.loads(res_real.text[start:end + 1])
                        # 只有当名字有效时才更新，防止覆盖成空
                        if data_real.get('name'): fund_info['name'] = data_real.get('name')
                        if data_real.get('jzrq'): fund_info['date'] = data_real.get('jzrq')
                        if data_real.get('gszzl'): fund_info['day'] = data_real.get('gszzl')
            except:
                pass  # 实时接口失败不影响后续

            # --- 第2步：静态档案 (补全 名字、历史业绩) ---
            try:
                url_static = f"http://fund.eastmoney.com/pingzhongdata/{code}.js?v={ts}"
                res_static = requests.get(url_static, headers=get_headers(), timeout=3)
                res_static.encoding = 'utf-8'
                content = res_static.text

                # 辅助提取函数
                def get_v(key):
                    m = re.search(f'{key}\s*=\s*"(.*?)";', content)
                    return m.group(1) if m and m.group(1) else ""

                # 1. 名字补救 (关键！如果第1步名字还是"获取中"，这里一定能取到)
                if fund_info['name'] == '获取中...':
                    static_name = get_v("fS_name")
                    if static_name: fund_info['name'] = static_name

                # 2. 补全业绩
                w = get_v("syl_1z")
                m = get_v("syl_1y")
                y = get_v("syl_jn")

                if w: fund_info['week'] = w
                if m: fund_info['month'] = m
                if y: fund_info['year'] = y

            except:
                pass

            # --- 第3步：网页爬虫 (终极补全 "今年来" ) ---
            # 只有当 "今年来" 还是空的时候才启动，节省时间
            if fund_info['year'] == "--" or fund_info['year'] == "":
                # print(f"   >>> {code} 正在尝试网页爬取补全...")
                try:
                    url_f10 = f"http://fundf10.eastmoney.com/jzzzl_{code}.html"
                    res_f10 = requests.get(url_f10, headers=get_headers(), timeout=4)
                    res_f10.encoding = 'utf-8'

                    # 使用更宽松的正则匹配表格里的数据
                    # 匹配 "今年来" 后面出现的第一个百分数
                    match_year = re.search(r'今年来.*?(-?\d+\.\d+)%', res_f10.text, re.S)
                    if match_year:
                        fund_info['year'] = match_year.group(1)

                    # 顺便补一下近一周
                    if fund_info['week'] == "--":
                        match_week = re.search(r'近一周.*?(-?\d+\.\d+)%', res_f10.text, re.S)
                        if match_week:
                            fund_info['week'] = match_week.group(1)
                except:
                    pass

        except Exception as e:
            print(f"   ⚠️ {code} 处理异常: {e}")

        my_funds_data.append(fund_info)

    return my_funds_data


def get_gold_silver_price():
    """获取金银价格"""
    ts = int(time.time() * 1000)
    url = f"http://hq.sinajs.cn/list=nf_AU0,nf_AG0,g_au99_99,g_ag_td&_={ts}"

    try:
        res = requests.get(url, headers={"Referer": "https://finance.sina.com.cn/"}, timeout=8)
        content = res.text
        metals = []

        def extract_price(code_key, backup_key, name_cn, unit_cn, base_price):
            def parse_val(key, is_fut):
                match = re.search(f'{key}="(.*?)"', content)
                if match:
                    parts = match.group(1).split(',')
                    idx_p = 8 if is_fut else 5
                    idx_pre = 5 if is_fut else 4
                    if len(parts) > max(idx_p, idx_pre):
                        p = float(parts[idx_p])
                        pre = float(parts[idx_pre])
                        if p <= 0 and pre > 0: p = pre
                        return p, pre
                return 0.0, 0.0

            p, pre = parse_val(code_key, True)
            src = "期货"
            if p <= 0:
                p, pre = parse_val(backup_key, False)
                src = "现货"

            if p > 0:
                day_pct = ((p - pre) / pre * 100) if pre > 0 else 0
                ytd_pct = ((p - base_price) / base_price * 100)
                metals.append({
                    'name': f"{name_cn} ({src})",
                    'price': f"{p:.2f}", 'unit': unit_cn,
                    'day_pct': f"{day_pct:+.2f}%",
                    'ytd_pct': ytd_pct
                })

        extract_price("nf_AU0", "g_au99_99", "沪金", "元/克", BASE_PRICE_GOLD)
        extract_price("nf_AG0", "g_ag_td", "沪银", "元/千克", BASE_PRICE_SILVER)

        return metals
    except Exception as e:
        print(f"❌ 金银数据获取错误: {e}")
        return []


def format_email_content(top_funds, my_funds, metals):
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    html = f"<h2 style='color:#333;'>📊 投资监控日报 ({today})</h2>"

    # 1. 自选
    html += "<h3 style='border-left: 5px solid #28a745; padding-left:10px;'>🎯 我的自选基金</h3>"
    if my_funds:
        html += "<table border='1' style='border-collapse: collapse; width: 100%; max-width: 700px;'>"
        html += "<tr style='background-color: #e8f5e9;'><th>代码</th><th>名称</th><th>日涨跌</th><th>近一周</th><th>近一月</th><th>今年来</th></tr>"
        for f in my_funds:
            def c(v):
                if not v or v == '--': return 'black'
                if '-' in str(v) and '0.-' not in str(v): return 'green'
                if str(v) == '0.00': return 'black'
                return 'red'

            day_show = f"{f['day']}%" if '%' not in f['day'] and f['day'] != '--' else f['day']
            week_show = f"{f['week']}%" if '%' not in f['week'] and f['week'] != '--' else f['week']
            month_show = f"{f['month']}%" if '%' not in f['month'] and f['month'] != '--' else f['month']
            year_show = f"{f['year']}%" if '%' not in f['year'] and f['year'] != '--' else f['year']

            html += f"<tr><td style='padding:8px;text-align:center'>{f['code']}</td>"
            html += f"<td style='padding:8px'>{f['name']} <span style='font-size:10px;color:gray'>({f['date']})</span></td>"
            html += f"<td style='padding:8px;text-align:center;color:{c(f['day'])};font-weight:bold'>{day_show}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{c(f['week'])}'>{week_show}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{c(f['month'])}'>{month_show}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{c(f['year'])};font-weight:bold'>{year_show}</td></tr>"
        html += "</table>"
    else:
        html += "<p>暂无自选数据</p>"

    # 2. 贵金属
    html += "<br><h3 style='border-left: 5px solid #FFD700; padding-left:10px;'>🟡 贵金属报价</h3>"
    if metals:
        html += "<table border='1' style='border-collapse: collapse; width: 100%; max-width: 600px;'>"
        html += "<tr style='background-color: #fff8e1;'><th>品类</th><th>最新价</th><th>日涨跌</th><th>今年来(YTD)</th></tr>"
        for m in metals:
            d_col = "red" if '+' in m['day_pct'] else "green"
            y_col = "red" if m['ytd_pct'] > 0 else "green"
            html += f"<tr><td style='padding:8px'><b>{m['name']}</b></td><td style='padding:8px;text-align:center'>{m['price']} {m['unit']}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{d_col}'>{m['day_pct']}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{y_col}'><b>{m['ytd_pct']:+.2f}%</b></td></tr>"
        html += "</table>"
    else:
        html += "<p>暂无金银数据</p>"

    # 3. 榜单
    html += "<br><h3 style='border-left: 5px solid #FF6347; padding-left:10px;'>🚀 市场 Top 10 (C类精选)</h3>"
    if top_funds:
        html += "<table border='1' style='border-collapse: collapse; width: 100%; max-width: 650px;'>"
        html += "<tr style='background-color: #f2f2f2;'><th>代码</th><th>名称</th><th>近一周</th><th>近一月</th><th>今年来</th></tr>"
        for f in top_funds:
            w_col = "red" if '-' not in f['week'] else "green"
            html += f"<tr><td style='padding:8px'>{f['code']}</td><td style='padding:8px'>{f['name']}</td>"
            html += f"<td style='padding:8px;color:{w_col}'>{f['week']}%</td><td style='padding:8px'>{f['month']}%</td><td style='padding:8px'>{f['year']}%</td></tr>"
        html += "</table>"

    html += "<p style='margin-top:20px; font-size:12px; color:gray;'>数据来源：天天基金 & 新浪财经 & 机智的python云</p>"
    return html


def send_email(content):
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = formataddr(("财富助手", SENDER_EMAIL))

    # 【修改点1】邮件头显示：把所有邮箱用逗号拼起来显示
    # 这样收件人能看到这封信还发给了谁
    message['To'] = ",".join(RECEIVERS)

    message['Subject'] = Header(f"【投资日报】{datetime.now().strftime('%m-%d')}", 'utf-8')

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASS)

        # 【修改点2】核心发送逻辑：直接传入 RECEIVERS 列表
        # SMTP 协议会自动把邮件分发给列表里的所有人
        server.sendmail(SENDER_EMAIL, RECEIVERS, message.as_string())

        server.quit()
        print(f"✅ 邮件已成功群发给 {len(RECEIVERS)} 位收件人！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")


if __name__ == "__main__":
    print("1. 正在获取 Top 10...")
    top = get_filtered_funds()

    print("2. 正在获取自选基金 (API + 静态 + 爬虫)...")
    my = get_my_funds()

    print("3. 正在获取金银数据...")
    metal = get_gold_silver_price()

    if top or my or metal:
        print("4. 正在发送邮件...")
        send_email(format_email_content(top, my, metal))
    else:
        print("未获取到数据，请检查网络连接。")
