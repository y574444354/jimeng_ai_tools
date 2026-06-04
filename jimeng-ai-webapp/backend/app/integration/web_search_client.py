"""
全网信息搜索客户端
基于 DuckDuckGo 搜索引擎（ddgs 库），封装为后端可调用的接口
"""
import logging
from typing import List, Optional
from dataclasses import dataclass, field
from ddgs import DDGS
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """搜索结果数据结构"""
    title: str = ""
    url: str = ""
    snippet: str = ""
    content: str = ""


class WebSearchClient:
    """全网信息搜索客户端

    封装 DuckDuckGo 搜索能力，作为后端服务层的搜索基础设施。
    """

    def __init__(self):
        self.max_results = settings.SEARCH_MAX_RESULTS
        self.timeout = settings.SEARCH_TIMEOUT
        self.default_language = settings.SEARCH_DEFAULT_LANGUAGE

    def search(self, query: str, max_results: int = 10, language: str = "zh") -> List[SearchResult]:
        """执行网络搜索

        Args:
            query: 搜索关键词
            max_results: 最大搜索结果数（1-20）
            language: 搜索语言

        Returns:
            标准化搜索结果列表
        """
        max_results = min(max(max_results, 1), self.max_results)
        logger.info(f"网络搜索: query='{query}', max_results={max_results}, language={language}")

        try:
            results: List[SearchResult] = []
            with DDGS() as ddgs:
                region = "cn-zh" if language == "zh" else "wt-wt"
                for r in ddgs.text(
                    query,
                    region=region,
                    max_results=max_results,
                    backend="yandex",
                ):
                    results.append(SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        content="",
                    ))
            logger.info(f"搜索完成: 找到 {len(results)} 条结果")
            return results
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}", exc_info=True)
            return []

    def fetch_content(self, url: str, use_browser: bool = False) -> str:
        """获取网页完整内容"""
        logger.info(f"抓取网页内容: url='{url}', use_browser={use_browser}")
        from app.integration.web_content_fetcher import web_content_fetcher
        return web_content_fetcher.fetch(url, use_browser=use_browser)

    def search_and_extract(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """搜索并提取内容（搜索+抓取二合一）"""
        results = self.search(query, max_results)
        for r in results:
            if r.url:
                r.content = self.fetch_content(r.url)
        return results


web_search_client = WebSearchClient()
