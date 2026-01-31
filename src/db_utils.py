import sqlite3

# 定义数据库文件的名字
DB_FILE = 'financial_data.db'

def init_db():
    """初始化数据库，创建表结构"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. 创建基金数据表
    # 这里的 PRIMARY KEY (fund_code, record_date) 联合主键非常重要
    # 它可以防止同一只基金在同一天被重复写入，保证数据唯一性
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funds (
            fund_code TEXT,
            fund_name TEXT,
            record_date DATE,       -- 记录日期，比如 2026-01-31
            daily_growth REAL,      -- 日涨跌幅
            year_growth REAL,       -- 今年以来涨跌幅
            PRIMARY KEY (fund_code, record_date)
        )
    ''')

    # 2. 创建金银数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS precious_metals (
            metal_type TEXT,        -- 类型：黄金 or 白银
            record_date DATE,
            price REAL,             -- 当前价格
            change_percent REAL,    -- 涨跌幅
            PRIMARY KEY (metal_type, record_date)
        )
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成，表结构已就绪。")

# 如果作为独立脚本运行，则执行初始化
if __name__ == '__main__':
    init_db()