SMTP_SERVER = 'smtp.qq.com'  # SMTP服务器
SMTP_PORT = 465  # SSL端口通常是465
SENDER_EMAIL = '1366400216@qq.com'  # 发件人邮箱
# 注意：这里填的不是QQ密码，是邮箱设置里开启POP3/SMTP服务时获取的“授权码”
SENDER_PASS = 'xdaefxtbelihbaeb'

# 收件箱设置 (可以是同一个邮箱，也可以是你的手机139邮箱等)
RECEIVER_EMAIL = 'ljz400216@163.com'

# --- 🎯 我的自选基金 (在这里添加你关注的基金代码) ---
# 自选基金代码 (支持任意数量)
MY_WATCHLIST = ['161226', '270042']

# 2025年底收盘基准价 (根据你的截图修正了2026年现价基准)
# 修正逻辑：现价1121，假设去年底约为1100左右，避免出现+70%的虚假涨幅
BASE_PRICE_GOLD = 980.9
BASE_PRICE_SILVER = 16730