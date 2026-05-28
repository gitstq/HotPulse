<div align="center">

# 🔥 HotPulse

**AI-Powered Trend Aggregation & Analysis Tool**

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

## 🎉 Introduction

**HotPulse** is a lightweight, extensible AI-powered trend aggregation and analysis tool that helps you monitor hot topics across multiple platforms in real-time, with intelligent AI analysis to uncover sentiment trends.

### Inspiration

This project is inspired by excellent open-source projects like [TrendRadar](https://github.com/sansan0/TrendRadar). We aim to create a more lightweight and easier-to-deploy version, enabling individual developers and small teams to quickly build their own trend monitoring systems.

### Differentiation Highlights

- 🚀 **Minimal Deployment**: Single-file startup, no complex configuration
- 🔌 **Plugin Architecture**: Support for custom data source extensions
- 🤖 **AI-Powered Analysis**: Built-in sentiment analysis and keyword extraction
- 📊 **Real-time Visualization**: RESTful API + real-time statistics
- 🐳 **Containerized**: Docker one-click deployment

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 📡 **Multi-Source Aggregation** | Support Zhihu, Weibo, Bilibili, GitHub and more |
| 🤖 **AI Analysis** | Smart sentiment analysis, keyword extraction, trend prediction |
| 💾 **Data Persistence** | SQLite lightweight storage, zero configuration |
| 🔔 **Flexible Notifications** | Webhook, DingTalk, WeChat Work multi-channel push |
| 🚀 **High Performance** | Async architecture, high-concurrency data fetching |
| 📈 **Real-time Monitoring** | Built-in scheduled tasks, automatic fetching and analysis |

---

## 🚀 Quick Start

### Requirements

- Python 3.8+
- pip or poetry
- (Optional) Docker & Docker Compose

### Option 1: Local Startup

```bash
# 1. Clone the repository
git clone https://github.com/gitstq/HotPulse.git
cd HotPulse

# 2. Run startup script
./start.sh
```

Or manual steps:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables (optional)
cp .env.example .env
# Edit .env file

# 4. Start service
python main.py
```

After startup, visit:
- API Docs: http://localhost:8000/docs
- API Endpoint: http://localhost:8000

### Option 2: Docker Deployment

```bash
# 1. Clone repository
git clone https://github.com/gitstq/HotPulse.git
cd HotPulse

# 2. Start containers
docker-compose up -d

# 3. View logs
docker-compose logs -f
```

---

## 📖 Detailed Usage Guide

### API Endpoints

#### Get Hot Items
```bash
GET /api/hot?source=知乎热榜&limit=20&hours=24
```

#### Get Analysis Report
```bash
GET /api/analysis?hours=24
```

#### Trigger Data Fetch
```bash
POST /api/fetch
```

#### Get Statistics
```bash
GET /api/stats?hours=24
```

### Configuration

Edit `config.yaml` for custom configuration:

```yaml
# Data source configuration
sources:
  zhihu:
    enabled: true
    name: "知乎热榜"
  weibo:
    enabled: true
    name: "微博热搜"

# Fetcher configuration
fetcher:
  interval: 300  # Fetch interval (seconds)
```

---

## 💡 Design & Roadmap

### Tech Stack

- **FastAPI**: High-performance async web framework
- **SQLite**: Zero-config lightweight database
- **aiohttp**: Async HTTP client
- **Pydantic**: Data validation and serialization

### Roadmap

- [ ] Frontend visualization dashboard
- [ ] More data sources (Douyin, Xiaohongshu, Twitter)
- [ ] Advanced AI analysis (topic clustering, propagation path)
- [ ] Alert rule engine
- [ ] Data export functionality

---

## 📦 Packaging & Deployment

### Docker Build

```bash
docker build -t hotpulse:latest .
docker run -p 8000:8000 hotpulse:latest
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |
| `DATABASE_PATH` | Database path | hotpulse.db |
| `FETCH_INTERVAL` | Fetch interval (seconds) | 300 |

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

---

## 📄 License

This project is open-sourced under the [MIT](LICENSE) License.

---

<div align="center">

**Made with ❤️ by HotPulse Team**

</div>
