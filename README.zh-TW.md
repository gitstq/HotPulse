<div align="center">

# 🔥 HotPulse

**AI輿論熱點聚合分析工具**

<p align="center">
  <a href="README.md">简体中文</a> |
  <a href="README.zh-TW.md">繁體中文</a> |
  <a href="README.en.md">English</a>
</p>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](Dockerfile)

</div>

---

## 🎉 專案介紹

**HotPulse** 是一個輕量級、可擴展的AI輿論熱點聚合分析工具，幫助您實時監控多平台熱點資訊，透過AI智能分析洞察輿論趨勢。

### 靈感來源

本專案靈感來源於 [TrendRadar](https://github.com/sansan0/TrendRadar) 等優秀開源專案，我們致力於打造一個更輕量、更易部署的版本，讓個人開發者和小團隊也能快速搭建自己的輿論監控系統。

### 自研差異化亮點

- 🚀 **極簡部署**：單檔案啟動，無需複雜配置
- 🔌 **插件化架構**：支援自定義資料源擴展
- 🤖 **AI智能分析**：內建情感分析與關鍵詞提取
- 📊 **實時可視化**：RESTful API + 實時統計數據
- 🐳 **容器化支援**：Docker一鍵部署

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📡 **多源聚合** | 支援知乎、微博、B站、GitHub等主流平台 |
| 🤖 **AI分析** | 智能情感分析、關鍵詞提取、趨勢預測 |
| 💾 **資料持久化** | SQLite輕量級儲存，零配置 |
| 🔔 **靈活通知** | Webhook、釘釘、企業微信等多通道推送 |
| 🚀 **高效能** | 異步架構，支援高併發資料抓取 |
| 📈 **實時監控** | 內建定時任務，自動抓取與分析 |

---

## 🚀 快速開始

### 環境要求

- Python 3.8+
- pip 或 poetry
- (可選) Docker & Docker Compose

### 方式一：本地啟動

```bash
# 1. 克隆倉庫
git clone https://github.com/gitstq/HotPulse.git
cd HotPulse

# 2. 執行啟動腳本
./start.sh
```

或使用手動步驟：

```bash
# 1. 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 配置環境變數（可選）
cp .env.example .env
# 編輯 .env 檔案

# 4. 啟動服務
python main.py
```

服務啟動後訪問：
- API文件：http://localhost:8000/docs
- API端點：http://localhost:8000

### 方式二：Docker部署

```bash
# 1. 克隆倉庫
git clone https://github.com/gitstq/HotPulse.git
cd HotPulse

# 2. 啟動容器
docker-compose up -d

# 3. 查看日誌
docker-compose logs -f
```

---

## 📖 詳細使用指南

### API介面

#### 獲取熱點列表
```bash
GET /api/hot?source=知乎熱榜&limit=20&hours=24
```

#### 獲取分析報告
```bash
GET /api/analysis?hours=24
```

#### 觸發資料抓取
```bash
POST /api/fetch
```

#### 獲取統計數據
```bash
GET /api/stats?hours=24
```

### 配置說明

編輯 `config.yaml` 自定義配置：

```yaml
# 資料源配置
sources:
  zhihu:
    enabled: true
    name: "知乎熱榜"
  weibo:
    enabled: true
    name: "微博熱搜"

# 抓取配置
fetcher:
  interval: 300  # 抓取間隔（秒）
```

---

## 💡 設計思路與迭代規劃

### 技術選型

- **FastAPI**: 高效能異步Web框架
- **SQLite**: 零配置輕量級資料庫
- **aiohttp**: 異步HTTP客戶端
- **Pydantic**: 資料驗證與序列化

### 後續迭代計劃

- [ ] 前端可視化面板
- [ ] 更多資料源（抖音、小紅書、Twitter）
- [ ] 高級AI分析（主題聚類、傳播路徑）
- [ ] 告警規則引擎
- [ ] 資料匯出功能

---

## 📦 打包與部署

### Docker構建

```bash
docker build -t hotpulse:latest .
docker run -p 8000:8000 hotpulse:latest
```

### 環境變數

| 變數名 | 說明 | 預設值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密鑰（可選） | - |
| `DATABASE_PATH` | 資料庫路徑 | hotpulse.db |
| `FETCH_INTERVAL` | 抓取間隔（秒） | 300 |

---

## 🤝 貢獻指南

歡迎提交Issue和PR！

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 建立 Pull Request

---

## 📄 開源協議

本專案基於 [MIT](LICENSE) 協議開源。

---

<div align="center">

**Made with ❤️ by HotPulse Team**

</div>
