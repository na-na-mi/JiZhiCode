import streamlit as st
import pandas as pd
import sqlite3
import os

# ==========================================
# 🔧 核心配置：自动定位数据库路径
# ==========================================
# 获取当前 app.py 脚本所在的文件夹绝对路径
# 不管你在哪里运行命令，Python 都能通过这个找到它的“老家”
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 拼接出数据库的完整路径
DB_FILE = os.path.join(BASE_DIR, 'financial_data.db')

# ==========================================
# 🛠️ 页面设置与函数
# ==========================================
st.set_page_config(
    page_title="我的财富看板",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_data():
    """读取数据并做简单的预处理"""
    if not os.path.exists(DB_FILE):
        st.error(f"❌ 找不到数据库文件！\n\n程序试图寻找的路径是：`{DB_FILE}`\n\n请确认你已经运行过爬虫脚本生成了数据。")
        return pd.DataFrame(), pd.DataFrame()

    try:
        conn = sqlite3.connect(DB_FILE)

        # 读取基金数据
        df_funds = pd.read_sql_query("SELECT * FROM funds", conn)

        # 读取金银数据
        df_metals = pd.read_sql_query("SELECT * FROM precious_metals", conn)

        conn.close()
        return df_funds, df_metals
    except Exception as e:
        st.error(f"⚠️ 读取数据库时发生错误: {e}")
        return pd.DataFrame(), pd.DataFrame()


# ==========================================
# 🚀 主界面逻辑
# ==========================================

# 侧边栏：显示一些状态信息
with st.sidebar:
    st.header("⚙️ 控制台")
    st.success("数据库连接正常" if os.path.exists(DB_FILE) else "数据库未连接")
    st.code(f"路径: {os.path.basename(DB_FILE)}")  # 只显示文件名，简洁一点
    if st.button("🔄 刷新数据"):
        st.rerun()  # 点击按钮强制刷新页面

st.title("🚀 个人财务监控中心")

# 加载数据
df_fund, df_metal = load_data()

# --- 第一部分：贵金属行情 ---
st.subheader("🟡 贵金属实时行情")

if not df_metal.empty:
    # 找到最新的一天日期
    latest_date = df_metal['record_date'].max()
    # 筛选出那天的数据
    latest_metal = df_metal[df_metal['record_date'] == latest_date]

    # 使用列布局展示
    cols = st.columns(4)  # 创建4列，看起来宽敞一点
    for i, (_, row) in enumerate(latest_metal.iterrows()):
        # 防止列不够用（虽然你有两个数据，但这行代码更健壮）
        if i < 4:
            with cols[i]:
                st.metric(
                    label=f"{row['metal_type']} (现货/期货)",
                    value=f"¥{row['price']}",
                    delta=f"{row['change_percent']}%"
                )
    st.caption(f"更新时间: {latest_date}")
else:
    st.info("暂无金银数据，请运行爬虫脚本。")

st.divider()

# --- 第二部分：基金持仓分析 ---
st.subheader("📊 基金持仓表现")

if not df_fund.empty:
    # 1. 顶部筛选器
    all_funds = df_fund['fund_name'].unique()
    selected_fund = st.selectbox("🔍 请选择一只基金查看详情:", all_funds)

    # 2. 准备数据
    # 选出这只基金的所有数据，并按日期排序
    subset = df_fund[df_fund['fund_name'] == selected_fund].sort_values('record_date')

    if not subset.empty:
        # 取最新一条
        latest = subset.iloc[-1]

        # 3. 显示核心指标
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("基金名称", latest['fund_name'])
        c2.metric("最新净值日期", latest['record_date'])

        # 自动变色逻辑：涨是红(normal)，跌是绿(inverse) - 这里的inverse取决于你的设置，Streamlit默认正数绿
        c3.metric("日涨跌幅", f"{latest['daily_growth']}%")
        c4.metric("今年来收益", f"{latest['year_growth']}%")

        # 4. 绘制走势图
        st.markdown("#### 📈 收益率走势图")
        # 把日期作为索引，这样横坐标就是日期了
        chart_data = subset.set_index('record_date')[['year_growth', 'daily_growth']]
        st.line_chart(chart_data)

        # 5. 数据源表格（折叠起来，不占地）
        with st.expander("查看详细历史数据表格"):
            st.dataframe(subset.style.highlight_max(axis=0))  # 高亮最大值，炫技一下
    else:
        st.warning("该基金暂无历史数据。")
else:
    st.info("暂无基金数据。")