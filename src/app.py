import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime

# ==========================================
# 🔧 核心配置
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'financial_data.db')


def _fmt_pct(val, default='--'):
    """格式化涨跌幅，保留百分号"""
    if val is None or (isinstance(val, float) and pd.isna(val)) or str(val) in ['--', '', 'nan']:
        return default
    try:
        v = float(str(val).replace('%', '').replace('+', '').strip())
        return f"{v:+.2f}%"
    except (ValueError, TypeError):
        return f"{val}%" if val is not None and '%' not in str(val) else str(val)


def _weekday_cn(d):
    """返回日期对应的星期几中文"""
    if pd.isna(d):
        return ''
    try:
        dt = pd.to_datetime(d)
        w = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][dt.weekday()]
        return f" ({w})"
    except Exception:
        return ''


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
    """读取数据"""
    if not os.path.exists(DB_FILE):
        st.error(f"❌ 找不到数据库文件！\n\n路径：`{DB_FILE}`\n\n请先运行爬虫脚本生成数据。")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    try:
        conn = sqlite3.connect(DB_FILE)
        df_funds = pd.read_sql_query("SELECT * FROM funds", conn)
        df_metals = pd.read_sql_query("SELECT * FROM precious_metals", conn)
        try:
            df_top = pd.read_sql_query("SELECT * FROM top_funds ORDER BY record_date, rank_num", conn)
        except sqlite3.OperationalError:
            df_top = pd.DataFrame()
        conn.close()
        return df_funds, df_metals, df_top
    except Exception as e:
        st.error(f"⚠️ 读取数据库错误: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


# ==========================================
# 🚀 主界面
# ==========================================

with st.sidebar:
    st.header("⚙️ 控制台")
    st.success("数据库连接正常" if os.path.exists(DB_FILE) else "数据库未连接")
    st.code(f"路径: {os.path.basename(DB_FILE)}")
    st.divider()
    st.subheader("📂 导航菜单")
    page = st.radio(
        "选择页面",
        ["🏠 首页概览", "📊 自选基金", "🚀 Top10 C类基金"],
        label_visibility="collapsed"
    )
    if st.button("🔄 刷新数据"):
        st.rerun()

st.title("🚀 个人财务监控中心")

df_fund, df_metal, df_top = load_data()
is_weekend = datetime.datetime.now().weekday() >= 5
weekend_note = " ⚠️ 周末未更新，显示上一交易日数据" if is_weekend else ""

# ==================== 首页概览 ====================
if page == "🏠 首页概览":
    st.subheader("🟡 贵金属实时行情")
    if not df_metal.empty:
        latest_date = df_metal['record_date'].max()
        latest_metal = df_metal[df_metal['record_date'] == latest_date]
        price_date = latest_metal.iloc[0].get('price_date', latest_date) if 'price_date' in latest_metal.columns else latest_date
        st.caption(f"数据日期: {price_date}{_weekday_cn(price_date)}{weekend_note}")

        cols = st.columns(4)
        for i, (_, row) in enumerate(latest_metal.iterrows()):
            if i < 4:
                with cols[i]:
                    chg = row.get('change_percent')
                    delta = _fmt_pct(chg) if pd.notna(chg) else None
                    st.metric(label=f"{row['metal_type']} (现货/期货)", value=f"¥{row['price']}", delta=delta)
    else:
        st.info("暂无金银数据，请运行爬虫脚本。")

    st.divider()
    st.subheader("📊 自选基金快览")
    if not df_fund.empty:
        latest_date_f = df_fund['record_date'].max()
        latest_funds = df_fund[df_fund['record_date'] == latest_date_f]
        nav_date = latest_funds.iloc[0].get('nav_date', latest_date_f) if 'nav_date' in latest_funds.columns else latest_date_f
        st.caption(f"数据日期: {nav_date}{_weekday_cn(nav_date)}{weekend_note}")

        n_cols = min(4, len(latest_funds))
        cols = st.columns(n_cols)
        for i, (_, row) in enumerate(latest_funds.iterrows()):
            with cols[i % n_cols]:
                name = row['fund_name'][:14] + ("..." if len(row['fund_name']) > 14 else "")
                nav = row.get('nav')
                val = f"净值 {nav:.4f}" if pd.notna(nav) and nav else _fmt_pct(row.get('year_growth'))
                delta = _fmt_pct(row.get('daily_growth'))
                st.metric(label=name, value=val, delta=delta)
    else:
        st.info("暂无基金数据。")

    st.divider()
    st.subheader("🚀 Top 10 C类基金（最新榜单）")
    if not df_top.empty:
        latest_top_date = df_top['record_date'].max()
        latest_top = df_top[df_top['record_date'] == latest_top_date].sort_values('rank_num')
        cols_show = ['rank_num', 'fund_code', 'fund_name']
        if 'nav' in latest_top.columns:
            cols_show.append('nav')
        if 'nav_date' in latest_top.columns:
            cols_show.append('nav_date')
        cols_show.extend(['week_growth', 'month_growth', 'year_growth'])

        df_display = latest_top[[c for c in cols_show if c in latest_top.columns]].copy()
        for c in ['week_growth', 'month_growth', 'year_growth']:
            if c in df_display.columns:
                df_display[c] = df_display[c].apply(lambda x: _fmt_pct(x) if pd.notna(x) else '--')
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.caption(f"榜单日期: {latest_top_date}")
    else:
        st.info("暂无 Top 10 榜单数据，请运行 `get_found_rate.py`。")

# ==================== 自选基金详情 ====================
elif page == "📊 自选基金":
    st.subheader("📊 基金持仓表现")
    if not df_fund.empty:
        all_funds = df_fund['fund_name'].unique()
        selected_fund = st.selectbox("🔍 选择基金:", all_funds)
        subset = df_fund[df_fund['fund_name'] == selected_fund].sort_values('record_date')

        if not subset.empty:
            latest = subset.iloc[-1]
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("基金名称", latest['fund_name'])
            c2.metric("净值", f"{latest['nav']:.4f}" if pd.notna(latest.get('nav')) else "--")
            c3.metric("净值日期", str(latest.get('nav_date', latest['record_date'])))
            c4.metric("日涨跌幅", _fmt_pct(latest.get('daily_growth')))
            c5.metric("今年来收益", _fmt_pct(latest.get('year_growth')))

            chart_type = st.radio("图表类型", ["价格曲线 (净值)", "涨跌幅曲线"], horizontal=True)

            st.markdown("#### 📈 走势图")
            if chart_type == "价格曲线 (净值)" and 'nav' in subset.columns:
                nav_data = subset.set_index('record_date')[['nav']].dropna(how='all').ffill()
                if not nav_data.empty:
                    st.line_chart(nav_data)
                else:
                    st.info("暂无净值历史数据，请持续运行爬虫积累。")
            else:
                chart_data = subset.set_index('record_date')[['year_growth', 'daily_growth']].ffill()
                st.line_chart(chart_data)

            with st.expander("查看详细历史数据"):
                df_show = subset.copy()
                for col in ['daily_growth', 'year_growth']:
                    if col in df_show.columns:
                        df_show[col] = df_show[col].apply(lambda x: _fmt_pct(x) if pd.notna(x) else '--')
                st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.warning("该基金暂无历史数据。")
    else:
        st.info("暂无基金数据。")

# ==================== Top 10 C类基金 ====================
elif page == "🚀 Top10 C类基金":
    st.subheader("🚀 Top 10 C类基金折线图")
    if not df_top.empty:
        chart_type = st.radio("图表类型", ["价格曲线 (净值)", "涨跌幅曲线"], horizontal=True)

        if chart_type == "价格曲线 (净值)" and 'nav' in df_top.columns:
            metric_key = 'nav'
            metric_label = "净值"
        else:
            metric_col = st.selectbox(
                "选择涨跌幅指标",
                ["今年来收益 (year_growth)", "近一月收益 (month_growth)", "近一周收益 (week_growth)"],
                format_func=lambda x: x.split(" (")[0]
            )
            metric_key = metric_col.split(" (")[1].rstrip(")")
            metric_label = metric_col.split(" (")[0]

        all_top_funds = df_top['fund_name'].unique()
        selected_funds = st.multiselect(
            "选择要对比的基金",
            options=all_top_funds,
            default=all_top_funds[:5] if len(all_top_funds) >= 5 else list(all_top_funds)
        )

        if selected_funds:
            df_filtered = df_top[df_top['fund_name'].isin(selected_funds)].copy().sort_values('record_date')
            pivot = df_filtered.pivot_table(index='record_date', columns='fund_name', values=metric_key, aggfunc='first')

            if not pivot.empty:
                st.markdown(f"#### 📈 {metric_label} 走势对比")
                st.line_chart(pivot)

                st.markdown("#### 📋 数据明细")
                with st.expander("展开查看"):
                    df_show = df_filtered[['record_date', 'fund_name', 'rank_num', 'nav', 'nav_date', 'week_growth', 'month_growth', 'year_growth']]
                    df_show = df_show[[c for c in df_show.columns if c in df_filtered.columns]]
                    for c in ['week_growth', 'month_growth', 'year_growth']:
                        if c in df_show.columns:
                            df_show[c] = df_show[c].apply(lambda x: _fmt_pct(x) if pd.notna(x) else '--')
                    st.dataframe(df_show, use_container_width=True, hide_index=True)
            else:
                st.warning("所选基金暂无历史数据。")
        else:
            st.info("请至少选择一只基金。")
    else:
        st.info("暂无 Top 10 榜单数据。请先运行 `python src/get_found_rate.py`。")
