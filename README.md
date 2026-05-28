<div align="center">

# 🔥 HotPulse

**AI舆情热点聚合分析工具**

<p align="center">
  <a href="#简体中文">简体中文</a> |
  <a href="#繁體中文">繁體中文</a> |
  <a href="#english">English</a>
</p>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](Dockerfile)

</div>

---

## 🎉 项目介绍

**HotPulse** 是一个轻量级、可扩展的AI舆情热点聚合分析工具，帮助您实时监控多平台热点资讯，通过AI智能分析洞察舆情趋势。

### 灵感来源

本项目灵感来源于 [TrendRadar](https://github.com/sansan0/TrendRadar) 等优秀开源项目，我们致力于打造一个更轻量、更易部署的版本，让个人开发者和小团队也能快速搭建自己的舆情监控系统。

### 自研差异化亮点

- 🚀 **极简部署**：单文件启动，无需复杂配置
- 🔌 **插件化架构**：支持自定义数据源扩展
- 🤖 **AI智能分析**：内置情感分析与关键词提取
- 📊 **实时可视化**：RESTful API + 实时统计数据
- 🐳 **容器化支持**：Docker一键部署

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📡 **多源聚合** | 支持知乎、微博、B站、GitHub等主流平台 |
| 🤖 **AI分析** | 智能情感分析、关键词提取、趋势预测 |
| 💾 **数据持久化** | SQLite轻量级存储，零配置 |
| 🔔 **灵活通知** | Webhook、钉钉、企业微信等多通道推送 |
| 🚀 **高性能** | 异步架构，支持高并发数据抓取 |
| 📈 **实时监控** | 内置定时任务，自动抓取与分析 |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 或 poetry
- (可选) Docker & Docker Compose

### 方式一：本地启动

```bash
# 1. 克隆仓库
git clone https://github.com/gitstq/HotPulse.git
cd HotPulse

# 2. 运行启动脚本
./start.sh
```

或使用手动步骤：

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件

# 4. 启动服务
python main.py
```

服务启动后访问：
- API文档：http://localhost:8000/docs
- API端点：http://localhost:8000

### 方式二：Docker部署

```bash
# 1. 克隆仓库
git clone https://github.com/gitstq/HotPulse.git
cd HotPulse

# 2. 启动容器
docker-compose up -d

# 3. 查看日志
docker-compose logs -f
```

---

## 📖 详细使用指南

### API接口

#### 获取热点列表
```bash
GET /api/hot?source=知乎热榜&limit=20&hours=24
```

#### 获取分析报告
```bash
GET /api/analysis?hours=24
```

#### 触发数据抓取
```bash
POST /api/fetch
```

#### 获取统计数据
```bash
GET /api/stats?hours=24
```

### 配置说明

编辑 `config.yaml` 自定义配置：

```yaml
# 数据源配置
sources:
  zhihu:
    enabled: true
    name: "知乎热榜"
  weibo:
    enabled: true
    name: "微博热搜"

# 抓取配置
fetcher:
  interval: 300  # 抓取间隔（秒）
```

---

## 💡 设计思路与迭代规划

### 技术选型

- **FastAPI**: 高性能异步Web框架
- **SQLite**: 零配置轻量级数据库
- **aiohttp**: 异步HTTP客户端
- **Pydantic**: 数据验证与序列化

### 后续迭代计划

- [ ] 前端可视化面板
- [ ] 更多数据源（抖音、小红书、Twitter）
- [ ] 高级AI分析（主题聚类、传播路径）
- [ ] 告警规则引擎
- [ ] 数据导出功能

---

## 📦 打包与部署

### Docker构建

```bash
docker build -t hotpulse:latest .
docker run -p 8000:8000 hotpulse:latest
```

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥（可选） | - |
| `DATABASE_PATH` | 数据库路径 | hotpulse.db |
| `FETCH_INTERVAL` | 抓取间隔（秒） | 300 |

---

## 🤝 贡献指南

欢迎提交Issue和PR！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 开源协议

本项目基于 [MIT](LICENSE) 协议开源。

---

<div align="center">

**Made with ❤️ by HotPulse Team**

</div>
