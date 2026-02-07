import json
import re
import smtplib
import time
import requests
import datetime  # <-- 【保留这一行】
import sqlite3
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
import os  # 新增这个，为了处理路径



# ================= 配置区域 =================
SMTP_SERVER = 'smtp.qq.com'  # SMTP服务器bbb
SMTP_PORT = 465  # SSL端口通常是465
# ✅ 现在改成这样（去读环境变量，读不到就报错或者给个提示）
# os.getenv('变量名', '默认值') -> 如果找不到变量，就用默认值(可选)
# 但对于密码，建议不要写默认值，直接读
SENDER_EMAIL = os.getenv('MAIL_USER')
SENDER_PASS = os.getenv('MAIL_PASS')

# 如果读不到（比如你刚改完还没配置），为了防止程序莫名其妙报错，可以加个判断
if not SENDER_EMAIL or not SENDER_PASS:
    print("⚠️ 警告：未检测到邮箱配置！请在环境变量中设置 MAIL_USER 和 MAIL_PASS")

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

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Dashboard/financial_data.db')

def init_db():
    """初始化数据库表结构"""
    # 确保目录存在
    db_dir = os.path.dirname(DB_FILE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 建表：基金
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funds (
            fund_code TEXT,
            fund_name TEXT,
            record_date DATE,
            nav REAL,
            nav_date TEXT,
            daily_growth REAL,
            year_growth REAL,
            PRIMARY KEY (fund_code, record_date)
        )
    ''')

    # 建表：金银
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS precious_metals (
            metal_type TEXT,
            record_date DATE,
            price REAL,
            price_date TEXT,
            change_percent REAL,
            PRIMARY KEY (metal_type, record_date)
        )
    ''')

    # 建表：Top 10 C类基金榜单
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS top_funds (
            fund_code TEXT,
            fund_name TEXT,
            record_date DATE,
            rank_num INTEGER,
            nav REAL,
            nav_date TEXT,
            week_growth REAL,
            month_growth REAL,
            year_growth REAL,
            PRIMARY KEY (fund_code, record_date)
        )
    ''')

    # 兼容旧库：若缺少新列则追加
    for table, cols in [
        ('funds', [('nav', 'REAL'), ('nav_date', 'TEXT')]),
        ('precious_metals', [('price_date', 'TEXT')]),
        ('top_funds', [('nav', 'REAL'), ('nav_date', 'TEXT')])
    ]:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            existing = {r[1] for r in cursor.fetchall()}
            for col_name, col_type in cols:
                if col_name not in existing:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "http://fund.eastmoney.com/",
    }


def fetch_fund_nav(code):
    """获取单只基金的净值及净值日期（用于 Top 10 补全）"""
    try:
        ts = int(time.time() * 1000)
        url = f"http://fundgz.1234567.com.cn/js/{code}.js?rt={ts}"
        res = requests.get(url, headers=get_headers(), timeout=3)
        if res.status_code != 200:
            return None, None
        start, end = res.text.find('{'), res.text.rfind('}')
        if start == -1 or end == -1:
            return None, None
        data = json.loads(res.text[start:end + 1])
        nav = data.get('gsz') or data.get('dwjz')
        nav_date = data.get('jzrq')
        if nav:
            return float(nav), nav_date
    except Exception:
        pass
    return None, None


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
            'nav': None, 'nav_date': '--',
            'day': '--', 'week': '--', 'month': '--', 'year': '--'
        }

        try:
            ts = int(time.time() * 1000)

            # --- 第1步：实时接口 (获取 净值、日涨跌、净值日期) ---
            try:
                url_real = f"http://fundgz.1234567.com.cn/js/{code}.js?rt={ts}"
                res_real = requests.get(url_real, headers=get_headers(), timeout=2)
                if res_real.status_code == 200:
                    start = res_real.text.find('{')
                    end = res_real.text.rfind('}')
                    if start != -1 and end != -1:
                        data_real = json.loads(res_real.text[start:end + 1])
                        if data_real.get('name'): fund_info['name'] = data_real.get('name')
                        if data_real.get('jzrq'): fund_info['date'] = data_real.get('jzrq')
                        if data_real.get('gszzl'): fund_info['day'] = data_real.get('gszzl')
                        # 净值：优先 gsz(估值)，否则 dwjz(昨日净值)。周末/休市返回上一交易日数据
                        nav_val = data_real.get('gsz') or data_real.get('dwjz')
                        if nav_val:
                            try:
                                fund_info['nav'] = float(nav_val)
                                fund_info['nav_date'] = data_real.get('jzrq', '--')
                            except (ValueError, TypeError):
                                pass
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

                # 3. 净值补救（若第1步未取到）
                if fund_info['nav'] is None:
                    nav_str = get_v("dwjz") or get_v("gsz")
                    if nav_str:
                        try:
                            fund_info['nav'] = float(nav_str)
                            fund_info['nav_date'] = get_v("jzrq") or fund_info['date']
                        except (ValueError, TypeError):
                            pass

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


def _last_weekday(d):
    """返回日期 d 之前最近的交易日（周一至周五）"""
    while d.weekday() >= 5:  # 5=周六, 6=周日
        d -= datetime.timedelta(days=1)
    return d


def get_gold_silver_price():
    """获取金银价格。周末时 price_date 为上一交易日，便于提示"""
    ts = int(time.time() * 1000)
    url = f"http://hq.sinajs.cn/list=nf_AU0,nf_AG0,g_au99_99,g_ag_td&_={ts}"

    try:
        res = requests.get(url, headers={"Referer": "https://finance.sina.com.cn/"}, timeout=8)
        content = res.text
        metals = []
        today = datetime.date.today()
        is_weekend = today.weekday() >= 5
        price_date = _last_weekday(today).strftime('%Y-%m-%d') if is_weekend else today.strftime('%Y-%m-%d')

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
                    'price_date': price_date,
                    'day_pct': f"{day_pct:+.2f}%",
                    'ytd_pct': ytd_pct
                })

        extract_price("nf_AU0", "g_au99_99", "沪金", "元/克", BASE_PRICE_GOLD)
        extract_price("nf_AG0", "g_ag_td", "沪银", "元/千克", BASE_PRICE_SILVER)

        return metals
    except Exception as e:
        print(f"❌ 金银数据获取错误: {e}")
        return []


def _fmt_pct(val, default='--'):
    """格式化涨跌幅，保留百分号"""
    if val is None or val == '' or str(val) == '--':
        return default
    s = str(val).replace('%', '').strip()
    if not s:
        return default
    try:
        return f"{float(s):+.2f}%"
    except ValueError:
        return f"{s}%" if '%' not in str(val) else str(val)


def format_email_content(top_funds, my_funds, metals):
    today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    is_weekend = datetime.datetime.now().weekday() >= 5
    weekend_hint = " <span style='color:orange;font-size:11px;'>(周末未更新，显示上一交易日数据)</span>" if is_weekend else ""
    html = f"<h2 style='color:#333;'>📊 投资监控日报 ({today})</h2>{weekend_hint}"

    # 1. 自选（含净值）
    html += "<h3 style='border-left: 5px solid #28a745; padding-left:10px;'>🎯 我的自选基金</h3>"
    if my_funds:
        html += "<table border='1' style='border-collapse: collapse; width: 100%; max-width: 800px;'>"
        html += "<tr style='background-color: #e8f5e9;'><th>代码</th><th>名称</th><th>净值</th><th>净值日期</th><th>日涨跌</th><th>近一周</th><th>近一月</th><th>今年来</th></tr>"
        for f in my_funds:
            def c(v):
                if not v or v == '--': return 'black'
                if '-' in str(v) and '0.-' not in str(v): return 'green'
                if str(v) == '0.00': return 'black'
                return 'red'

            nav_show = f"{f['nav']:.4f}" if f.get('nav') is not None else '--'
            date_show = f.get('nav_date') or f.get('date') or '--'
            day_show = _fmt_pct(f['day'])
            week_show = _fmt_pct(f['week'])
            month_show = _fmt_pct(f['month'])
            year_show = _fmt_pct(f['year'])

            html += f"<tr><td style='padding:8px;text-align:center'>{f['code']}</td>"
            html += f"<td style='padding:8px'>{f['name']}</td>"
            html += f"<td style='padding:8px;text-align:center'>{nav_show}</td>"
            html += f"<td style='padding:8px;text-align:center;font-size:11px;color:gray'>{date_show}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{c(f['day'])};font-weight:bold'>{day_show}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{c(f['week'])}'>{week_show}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{c(f['month'])}'>{month_show}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{c(f['year'])};font-weight:bold'>{year_show}</td></tr>"
        html += "</table>"
    else:
        html += "<p>暂无自选数据</p>"

    # 2. 贵金属（含价格、涨跌幅带%）
    html += "<br><h3 style='border-left: 5px solid #FFD700; padding-left:10px;'>🟡 贵金属报价</h3>"
    if metals:
        price_date_hint = " (价格日期: " + (metals[0].get('price_date', '') or '--') + ")" if metals else ""
        html += f"<p style='font-size:11px;color:gray;'>{price_date_hint}</p>" if is_weekend else ""
        html += "<table border='1' style='border-collapse: collapse; width: 100%; max-width: 650px;'>"
        html += "<tr style='background-color: #fff8e1;'><th>品类</th><th>最新价</th><th>日涨跌</th><th>今年来(YTD)</th></tr>"
        for m in metals:
            d_col = "red" if '+' in str(m['day_pct']) else "green"
            y_col = "red" if m['ytd_pct'] > 0 else "green"
            day_pct = m['day_pct'] if '%' in str(m['day_pct']) else f"{m['day_pct']}%"
            ytd_show = f"{m['ytd_pct']:+.2f}%"
            html += f"<tr><td style='padding:8px'><b>{m['name']}</b></td><td style='padding:8px;text-align:center'>{m['price']} {m['unit']}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{d_col}'>{day_pct}</td>"
            html += f"<td style='padding:8px;text-align:center;color:{y_col}'><b>{ytd_show}</b></td></tr>"
        html += "</table>"
    else:
        html += "<p>暂无金银数据</p>"

    # 3. 榜单（含净值，涨跌幅带%）
    html += "<br><h3 style='border-left: 5px solid #FF6347; padding-left:10px;'>🚀 市场 Top 10 (C类精选)</h3>"
    if top_funds:
        html += "<table border='1' style='border-collapse: collapse; width: 100%; max-width: 900px;'>"
        html += "<tr style='background-color: #f2f2f2;'><th>代码</th><th>名称</th><th>净值</th><th>净值日期</th><th>近一周</th><th>近一月</th><th>今年来</th></tr>"
        for f in top_funds:
            w_col = "red" if '-' not in str(f.get('week', '')) else "green"
            nav_show = f"{f['nav']:.4f}" if f.get('nav') is not None else '--'
            nav_d = f.get('nav_date') or '--'
            week_show = _fmt_pct(f.get('week'))
            month_show = _fmt_pct(f.get('month'))
            year_show = _fmt_pct(f.get('year'))
            html += f"<tr><td style='padding:8px'>{f['code']}</td><td style='padding:8px'>{f['name']}</td>"
            html += f"<td style='padding:8px;text-align:center'>{nav_show}</td>"
            html += f"<td style='padding:8px;text-align:center;font-size:11px;color:gray'>{nav_d}</td>"
            html += f"<td style='padding:8px;color:{w_col}'>{week_show}</td>"
            html += f"<td style='padding:8px'>{month_show}</td>"
            html += f"<td style='padding:8px'>{year_show}</td></tr>"
        html += "</table>"
    else:
        html += "<p>暂无榜单数据</p>"

    html += "<p style='margin-top:20px; font-size:12px; color:gray;'>数据来源：天天基金 & 新浪财经</p>"
    return html


def send_email(content):
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = formataddr(("财富助手", SENDER_EMAIL))

    # 【修改点1】邮件头显示：把所有邮箱用逗号拼起来显示
    # 这样收件人能看到这封信还发给了谁
    message['To'] = ",".join(RECEIVERS)

    message['Subject'] = Header(f"【投资日报】{datetime.datetime.now().strftime('%m-%d')}", 'utf-8')

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

def save_fund_data(code, name, day_growth, year_growth, nav=None, nav_date=None):
    """保存单只基金的数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    today = datetime.date.today()
    nav_d = str(nav_date) if nav_date else None

    try:
        cursor.execute('''
            INSERT OR REPLACE INTO funds (fund_code, fund_name, record_date, nav, nav_date, daily_growth, year_growth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (code, name, today, nav, nav_d, day_growth, year_growth))

        conn.commit()
        print(f"✅ 成功存入: {name} ({today})")
    except Exception as e:
        print(f"❌ 存入失败 {name}: {e}")
    finally:
        conn.close()


def save_metal_data(metal_type, price, change, price_date=None):
    """保存金银数据。price_date 为实际价格对应的日期（周末时为上一交易日）"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    today = datetime.date.today()
    pd_str = price_date or str(today)

    try:
        cursor.execute('''
            INSERT OR REPLACE INTO precious_metals (metal_type, record_date, price, price_date, change_percent)
            VALUES (?, ?, ?, ?, ?)
        ''', (metal_type, today, price, pd_str, change))
        conn.commit()
        print(f"✅ 成功存入: {metal_type}")
    finally:
        conn.close()


def save_top_funds(top_funds):
    """保存 Top 10 C类基金榜单，并补全每只基金的净值"""
    if not top_funds:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    today = datetime.date.today()

    def clean_val(val):
        if not val or str(val) in ['--', '', 'NaN', 'None']:
            return None
        try:
            return float(str(val).replace('%', '').replace('+', '').replace(',', ''))
        except:
            return None

    try:
        for rank, f in enumerate(top_funds, 1):
            w_val = clean_val(f.get('week'))
            m_val = clean_val(f.get('month'))
            y_val = clean_val(f.get('year'))
            nav_val = f.get('nav')
            nav_d = f.get('nav_date')
            if nav_val is None and f.get('code'):
                nav_val, nav_d = fetch_fund_nav(f['code'])
            cursor.execute('''
                INSERT OR REPLACE INTO top_funds (fund_code, fund_name, record_date, rank_num, nav, nav_date, week_growth, month_growth, year_growth)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f['code'], f['name'], today, rank, nav_val, str(nav_d) if nav_d else None, w_val, m_val, y_val))
        conn.commit()
        print(f"✅ 成功存入 Top 10 榜单 ({len(top_funds)} 只)")
    except Exception as e:
        print(f"❌ Top 10 存入失败: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    print("0. 正在初始化数据库...")
    init_db()  # 确保数据库和表结构存在

    print("1. 正在获取 Top 10...")
    top = get_filtered_funds()

    print("2. 正在获取自选基金 (API + 静态 + 爬虫)...")
    my = get_my_funds()

    print("3. 正在获取金银数据...")
    metal = get_gold_silver_price()

    # --- 【修改】保存数据到 SQLite (智能清洗版) ---
    print("4. 正在保存数据到 SQLite...")


    # 定义一个临时清洗函数：把无效数据转为 None (空)，而不是 0
    def clean_data(val):
        if not val or str(val) in ['--', '', 'NaN', 'None']:
            return None
        try:
            # 去掉 %, +, , 等非数字符号
            clean_str = str(val).replace('%', '').replace('+', '').replace(',', '')
            return float(clean_str)
        except:
            return None


    # 1. 保存自选基金（含净值）
    if my:
        for f in my:
            d_val = clean_data(f['day'])
            y_val = clean_data(f['year'])
            nav_val = f.get('nav')
            nav_d = f.get('nav_date') if isinstance(f.get('nav_date'), str) else None

            if f.get('name') and f['name'] != '获取中...':
                if d_val is None:
                    print(f"   ℹ️ {f['name']} 今日无实时数据 (可能休市)，存为空值")
                save_fund_data(f['code'], f['name'], d_val, y_val, nav=nav_val, nav_date=nav_d)

    # 2. 保存金银（含价格日期，周末时为上一交易日）
    if metal:
        for m in metal:
            try:
                p_match = re.search(r"(\d+\.?\d*)", str(m['price']))
                p_val = float(p_match.group(1)) if p_match else None
                c_val = clean_data(m['day_pct'])
                name_clean = m['name'].split(' ')[0]
                price_date = m.get('price_date')

                save_metal_data(name_clean, p_val, c_val, price_date=price_date)
            except Exception as e:
                print(f"   保存 {m['name']} 失败: {e}")

    # 3. 保存 Top 10 C类基金（先补全净值，再入库和发邮件）
    if top:
        for f in top:
            if f.get('nav') is None:
                f['nav'], f['nav_date'] = fetch_fund_nav(f['code'])
        save_top_funds(top)

    # ------------------------------------------------

    if top or my or metal:
        print("5. 正在发送邮件...")
        send_email(format_email_content(top, my, metal))
    else:
        print("未获取到数据，请检查网络连接。")