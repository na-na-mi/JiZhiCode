# 📈 JiZhiCode - 个人脚本仓库

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![GitHub Actions](https://github.com/na-na-mi/JiZhiCode/actions/workflows/main.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green)

> 一个基于 GitHub Actions 的全自动化基金 & 金价监控系统，集成了数据抓取、邮件推送与可视化看板。

## 📖 项目简介

**Fund_moniter** 是一个轻量级的个人金融数据助手。它利用 GitHub Actions 实现**零成本**的云端自动化运行，解决了“需要每天手动查净值”和“本地电脑必须开机”的痛点。

**核心功能：**
- 🤖 **自动巡航**：每周一、三、五上午 10:15 (北京时间) 自动运行。
- 📧 **邮件日报**：自动抓取自选基金估值、贵金属（金/银）实时报价，并发送 HTML 格式日报。
- 📊 **可视化看板**：基于 Streamlit 的数据大屏，通过 SQLite 数据库回溯历史资产走势（开发中）。
- ☁️ **云端原生**：完全部署在 GitHub，无需购买服务器。

## 📂 项目结构

```text
JiZhiCode/
├── .github/workflows/   # CI/CD 自动化配置 (定时任务核心)
├── Dashboard/           # 数据可视化大屏 (Streamlit App)
│   ├── app.py           # 看板启动入口
│   └── financial_data.db # 历史数据存储 (SQLite)
├── Fund_monitor/        # 核心监控脚本
│   └── get_found_rate.py # 爬虫与邮件发送逻辑
├── requirements.txt     # 项目依赖库
└── README.md            # 项目说明文档
