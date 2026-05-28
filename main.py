#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HotPulse - AI舆情热点聚合分析工具
轻量级、可扩展的舆情监控与分析平台
"""

import os
import sys
import json
import time
import asyncio
import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

import aiohttp
import aiofiles
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据模型
@dataclass
class HotItem:
    """热点条目"""
    id: str
    title: str
    source: str
    url: str
    hot_score: int
    category: str
    created_at: str
    content: str = ""
    sentiment: Optional[str] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

class SourceConfig(BaseModel):
    """数据源配置"""
    name: str
    enabled: bool = True
    interval: int = 300  # 抓取间隔(秒)
    params: Dict[str, Any] = Field(default_factory=dict)

class AnalysisResult(BaseModel):
    """分析结果"""
    total_items: int
    sources_breakdown: Dict[str, int]
    sentiment_distribution: Dict[str, int]
    top_keywords: List[Dict[str, Any]]
    trending_topics: List[Dict[str, Any]]
    generated_at: str

# 数据库管理
class DatabaseManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: str = "hotpulse.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 热点数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hot_items (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    url TEXT NOT NULL,
                    hot_score INTEGER DEFAULT 0,
                    category TEXT,
                    content TEXT,
                    sentiment TEXT,
                    keywords TEXT,
                    created_at TEXT NOT NULL,
                    fetched_at TEXT NOT NULL
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_source ON hot_items(source)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at ON hot_items(created_at)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_category ON hot_items(category)
            ''')
            
            conn.commit()
            logger.info("数据库初始化完成")
    
    def save_items(self, items: List[HotItem]):
        """保存热点条目"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            for item in items:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO hot_items 
                        (id, title, source, url, hot_score, category, content, sentiment, keywords, created_at, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.id, item.title, item.source, item.url,
                        item.hot_score, item.category, item.content,
                        item.sentiment, json.dumps(item.keywords, ensure_ascii=False),
                        item.created_at, now
                    ))
                except Exception as e:
                    logger.error(f"保存条目失败 {item.id}: {e}")
            
            conn.commit()
            logger.info(f"成功保存 {len(items)} 条热点数据")
    
    def get_items(self, source: Optional[str] = None, 
                  limit: int = 100, 
                  hours: int = 24) -> List[HotItem]:
        """获取热点条目"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            if source:
                cursor.execute('''
                    SELECT * FROM hot_items 
                    WHERE source = ? AND created_at > ?
                    ORDER BY hot_score DESC
                    LIMIT ?
                ''', (source, since, limit))
            else:
                cursor.execute('''
                    SELECT * FROM hot_items 
                    WHERE created_at > ?
                    ORDER BY hot_score DESC
                    LIMIT ?
                ''', (since, limit))
            
            rows = cursor.fetchall()
            items = []
            for row in rows:
                item = HotItem(
                    id=row['id'],
                    title=row['title'],
                    source=row['source'],
                    url=row['url'],
                    hot_score=row['hot_score'],
                    category=row['category'] or '',
                    content=row['content'] or '',
                    sentiment=row['sentiment'],
                    keywords=json.loads(row['keywords']) if row['keywords'] else []
                )
                items.append(item)
            
            return items
    
    def get_stats(self, hours: int = 24) -> Dict:
        """获取统计数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            # 总数
            cursor.execute('''
                SELECT COUNT(*) FROM hot_items WHERE created_at > ?
            ''', (since,))
            total = cursor.fetchone()[0]
            
            # 各来源数量
            cursor.execute('''
                SELECT source, COUNT(*) as count 
                FROM hot_items 
                WHERE created_at > ?
                GROUP BY source
            ''', (since,))
            sources = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 情感分布
            cursor.execute('''
                SELECT sentiment, COUNT(*) as count 
                FROM hot_items 
                WHERE created_at > ? AND sentiment IS NOT NULL
                GROUP BY sentiment
            ''', (since,))
            sentiments = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'total': total,
                'sources': sources,
                'sentiments': sentiments
            }

# 数据源抓取器基类
class BaseFetcher:
    """数据源抓取器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'HotPulse/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch(self) -> List[HotItem]:
        """抓取数据，子类必须实现"""
        raise NotImplementedError
    
    def generate_id(self, title: str, source: str) -> str:
        """生成唯一ID"""
        content = f"{source}:{title}"
        return hashlib.md5(content.encode()).hexdigest()

# 知乎热榜抓取器
class ZhihuFetcher(BaseFetcher):
    """知乎热榜抓取器"""
    
    def __init__(self):
        super().__init__("知乎热榜")
        self.api_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
    
    async def fetch(self) -> List[HotItem]:
        """抓取知乎热榜"""
        items = []
        try:
            async with self.session.get(self.api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    for idx, item in enumerate(data.get('data', [])):
                        target = item.get('target', {})
                        title = target.get('title', '')
                        url = target.get('url', '')
                        if not url.startswith('http'):
                            url = f"https://www.zhihu.com{url}"
                        
                        hot_item = HotItem(
                            id=self.generate_id(title, self.name),
                            title=title,
                            source=self.name,
                            url=url,
                            hot_score=item.get('detail_text', '').replace('万', '0000').replace('热度', '').replace(' ', ''),
                            category='social',
                            created_at=datetime.now().isoformat()
                        )
                        # 处理热度值
                        try:
                            hot_item.hot_score = int(float(str(hot_item.hot_score).replace('万', '')) * 10000 if '万' in str(item.get('detail_text', '')) else hot_item.hot_score)
                        except:
                            hot_item.hot_score = 1000 - idx * 10
                        
                        items.append(hot_item)
        except Exception as e:
            logger.error(f"抓取知乎热榜失败: {e}")
        
        return items

# 微博热搜抓取器
class WeiboFetcher(BaseFetcher):
    """微博热搜抓取器"""
    
    def __init__(self):
        super().__init__("微博热搜")
        self.api_url = "https://weibo.com/ajax/side/hotSearch"
    
    async def fetch(self) -> List[HotItem]:
        """抓取微博热搜"""
        items = []
        try:
            async with self.session.get(self.api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    for idx, item in enumerate(data.get('data', {}).get('realtime', [])[:50]):
                        title = item.get('word', '')
                        url = f"https://s.weibo.com/weibo?q={title}"
                        
                        hot_item = HotItem(
                            id=self.generate_id(title, self.name),
                            title=title,
                            source=self.name,
                            url=url,
                            hot_score=item.get('num', 1000000 - idx * 10000),
                            category='social',
                            created_at=datetime.now().isoformat()
                        )
                        items.append(hot_item)
        except Exception as e:
            logger.error(f"抓取微博热搜失败: {e}")
        
        return items

# B站热榜抓取器
class BilibiliFetcher(BaseFetcher):
    """B站热榜抓取器"""
    
    def __init__(self):
        super().__init__("B站热榜")
        self.api_url = "https://api.bilibili.com/x/web-interface/ranking/v2"
    
    async def fetch(self) -> List[HotItem]:
        """抓取B站热榜"""
        items = []
        try:
            params = {'rid': 0, 'type': 'all'}
            async with self.session.get(self.api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    for idx, item in enumerate(data.get('data', {}).get('list', [])[:50]):
                        title = item.get('title', '')
                        bvid = item.get('bvid', '')
                        url = f"https://www.bilibili.com/video/{bvid}"
                        
                        hot_item = HotItem(
                            id=self.generate_id(title, self.name),
                            title=title,
                            source=self.name,
                            url=url,
                            hot_score=item.get('stat', {}).get('view', 1000000 - idx * 10000),
                            category='video',
                            created_at=datetime.now().isoformat()
                        )
                        items.append(hot_item)
        except Exception as e:
            logger.error(f"抓取B站热榜失败: {e}")
        
        return items

# GitHub Trending抓取器
class GitHubTrendingFetcher(BaseFetcher):
    """GitHub Trending抓取器"""
    
    def __init__(self):
        super().__init__("GitHub Trending")
        self.api_url = "https://github.com/trending"
    
    async def fetch(self) -> List[HotItem]:
        """抓取GitHub Trending (简化版，实际可解析HTML)"""
        items = []
        # GitHub Trending需要解析HTML，这里简化处理
        # 实际可使用 BeautifulSoup 或正则表达式解析
        logger.info("GitHub Trending 需要HTML解析，当前为简化实现")
        return items

# AI分析器
class AIAnalyzer:
    """AI分析器 - 用于情感分析和关键词提取"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    
    async def analyze_batch(self, items: List[HotItem]) -> List[HotItem]:
        """批量分析热点条目"""
        if not self.api_key:
            logger.warning("未配置OpenAI API密钥，跳过AI分析")
            return items
        
        # 简化的本地分析（无需API）
        positive_words = ['好', '赞', '优秀', '成功', '突破', '创新', '利好', '上涨', '增长']
        negative_words = ['差', '失败', '问题', '危机', '下跌', '损失', '负面', '批评', '争议']
        
        for item in items:
            title = item.title
            pos_count = sum(1 for w in positive_words if w in title)
            neg_count = sum(1 for w in negative_words if w in title)
            
            if pos_count > neg_count:
                item.sentiment = 'positive'
            elif neg_count > pos_count:
                item.sentiment = 'negative'
            else:
                item.sentiment = 'neutral'
            
            # 简单关键词提取
            item.keywords = self._extract_keywords(title)
        
        return items
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简化版）"""
        # 实际可使用jieba等分词工具
        common_words = ['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这']
        words = []
        for word in text.split():
            if len(word) > 1 and word not in common_words:
                words.append(word)
        return words[:5]

# 推送通知器
class Notifier:
    """推送通知器"""
    
    def __init__(self):
        self.webhooks = []
    
    def add_webhook(self, url: str, headers: Optional[Dict] = None):
        """添加Webhook"""
        self.webhooks.append({'url': url, 'headers': headers or {}})
    
    async def notify(self, items: List[HotItem], analysis: Dict):
        """发送通知"""
        if not items:
            return
        
        message = {
            'title': f'🔥 HotPulse 舆情报告 ({len(items)}条新热点)',
            'summary': analysis,
            'items': [asdict(item) for item in items[:10]],
            'timestamp': datetime.now().isoformat()
        }
        
        for webhook in self.webhooks:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook['url'],
                        json=message,
                        headers=webhook['headers']
                    ) as response:
                        logger.info(f"Webhook通知发送状态: {response.status}")
            except Exception as e:
                logger.error(f"发送Webhook通知失败: {e}")

# 主服务
class HotPulseService:
    """HotPulse核心服务"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analyzer = AIAnalyzer()
        self.notifier = Notifier()
        self.fetchers: List[BaseFetcher] = [
            ZhihuFetcher(),
            WeiboFetcher(),
            BilibiliFetcher(),
            GitHubTrendingFetcher()
        ]
        self.running = False
    
    async def fetch_all(self) -> List[HotItem]:
        """抓取所有数据源"""
        all_items = []
        
        for fetcher in self.fetchers:
            try:
                async with fetcher:
                    items = await fetcher.fetch()
                    all_items.extend(items)
                    logger.info(f"{fetcher.name}: 抓取到 {len(items)} 条数据")
            except Exception as e:
                logger.error(f"抓取 {fetcher.name} 失败: {e}")
        
        return all_items
    
    async def process_items(self, items: List[HotItem]):
        """处理并分析热点条目"""
        # AI分析
        items = await self.analyzer.analyze_batch(items)
        
        # 保存到数据库
        self.db.save_items(items)
        
        return items
    
    def get_analysis(self, hours: int = 24) -> AnalysisResult:
        """获取分析报告"""
        items = self.db.get_items(hours=hours)
        stats = self.db.get_stats(hours=hours)
        
        # 统计关键词
        keyword_counts = {}
        for item in items:
            for kw in item.keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        top_keywords = [
            {'word': k, 'count': v}
            for k, v in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        ]
        
        # 趋势话题（按来源分组）
        trending = {}
        for item in items:
            if item.source not in trending:
                trending[item.source] = []
            trending[item.source].append({
                'title': item.title,
                'score': item.hot_score,
                'sentiment': item.sentiment
            })
        
        trending_topics = [
            {'source': k, 'items': v[:5]}
            for k, v in trending.items()
        ]
        
        return AnalysisResult(
            total_items=len(items),
            sources_breakdown=stats.get('sources', {}),
            sentiment_distribution=stats.get('sentiments', {}),
            top_keywords=top_keywords,
            trending_topics=trending_topics,
            generated_at=datetime.now().isoformat()
        )

# FastAPI应用
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("HotPulse 服务启动")
    yield
    logger.info("HotPulse 服务停止")

app = FastAPI(
    title="HotPulse API",
    description="AI舆情热点聚合分析工具",
    version="1.0.0",
    lifespan=lifespan
)

service = HotPulseService()

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "HotPulse",
        "version": "1.0.0",
        "description": "AI舆情热点聚合分析工具",
        "docs": "/docs"
    }

@app.get("/api/hot")
async def get_hot_items(
    source: Optional[str] = None,
    limit: int = 50,
    hours: int = 24
):
    """获取热点列表"""
    items = service.db.get_items(source=source, limit=limit, hours=hours)
    return {
        "items": [asdict(item) for item in items],
        "total": len(items),
        "source": source or "all",
        "hours": hours
    }

@app.get("/api/analysis")
async def get_analysis(hours: int = 24):
    """获取分析报告"""
    result = service.get_analysis(hours=hours)
    return result

@app.post("/api/fetch")
async def trigger_fetch(background_tasks: BackgroundTasks):
    """触发数据抓取"""
    async def do_fetch():
        items = await service.fetch_all()
        await service.process_items(items)
    
    background_tasks.add_task(do_fetch)
    return {"message": "数据抓取任务已启动", "status": "running"}

@app.get("/api/stats")
async def get_stats(hours: int = 24):
    """获取统计数据"""
    return service.db.get_stats(hours=hours)

@app.get("/api/sources")
async def get_sources():
    """获取数据源列表"""
    return {
        "sources": [
            {"name": f.name, "enabled": True}
            for f in service.fetchers
        ]
    }

# 定时任务
async def scheduled_fetch():
    """定时抓取任务"""
    while True:
        try:
            logger.info("执行定时数据抓取...")
            items = await service.fetch_all()
            if items:
                await service.process_items(items)
                analysis = service.get_analysis()
                await service.notifier.notify(items, analysis.dict())
            logger.info("定时数据抓取完成")
        except Exception as e:
            logger.error(f"定时任务执行失败: {e}")
        
        await asyncio.sleep(300)  # 5分钟间隔

if __name__ == "__main__":
    import uvicorn
    
    # 启动定时任务
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled_fetch())
    
    # 启动API服务
    uvicorn.run(app, host="0.0.0.0", port=8000)
