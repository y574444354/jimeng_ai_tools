"""网页内容抓取器

主方案：httpx + BeautifulSoup4（轻量、快速、覆盖 70% 页面）
可选增强：Playwright（处理 JS 渲染页面，use_browser=True 时触发）
"""
import logging
from typing import Optional
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebContentFetcher:
    """网页内容抓取器"""

    def __init__(self):
        self._client: Optional[httpx.Client] = None
        self.timeout = 30.0

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/125.0.0.0 Safari/537.36"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                },
                follow_redirects=True,
            )
        return self._client

    def fetch(self, url: str, use_browser: bool = False) -> str:
        """抓取网页正文内容

        Args:
            url: 目标网页地址
            use_browser: 是否使用浏览器引擎（Playwright）处理 JS 渲染页面

        Returns:
            提取的纯文本内容
        """
        logger.info(f"抓取网页内容: url='{url}', use_browser={use_browser}")

        if use_browser:
            return self._fetch_with_browser(url)

        return self._fetch_with_httpx(url)

    def _fetch_with_httpx(self, url: str) -> str:
        """httpx + BS4 抓取"""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            # 自动检测编码
            response.encoding = response.charset_encoding or "utf-8"
            html = response.text
            return self._extract_text(html)
        except httpx.HTTPError as e:
            logger.error(f"HTTP 抓取失败: {str(e)}")
            # 如果是 403/5xx 等错误，尝试用浏览器模式
            logger.info("HTTP 抓取失败，请尝试 use_browser=true")
            return ""
        except Exception as e:
            logger.error(f"抓取异常: {str(e)}", exc_info=True)
            return ""

    def _fetch_with_browser(self, url: str) -> str:
        """Playwright 浏览器抓取（按需启用）"""
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                html = page.content()
                browser.close()
                return self._extract_text(html)
        except ImportError:
            logger.warning("Playwright 未安装，无法使用浏览器模式。运行: playwright install chromium")
            return self._fetch_with_httpx(url)
        except Exception as e:
            logger.error(f"浏览器抓取失败: {str(e)}", exc_info=True)
            return ""

    def _extract_text(self, html: str) -> str:
        """从 HTML 中提取正文纯文本

        优先级：
        1. <article> 标签
        2. <main> 标签
        3. 常见内容容器（.content, .article, .post 等）
        4. <body> 全部内容
        """
        soup = BeautifulSoup(html, "lxml")

        # 移除干扰元素
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # 按优先级提取正文
        content_selectors = [
            "article",
            "main",
            '[class*="content"]',
            '[class*="article"]',
            '[class*="post"]',
            '[id*="content"]',
            '[id*="article"]',
            '[id*="post"]',
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator="\n", strip=True)
                if len(text) > 100:
                    # 压缩多余空行
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    return "\n".join(lines)

        # 兜底：取 body 全文（限制长度）
        body = soup.body
        if body:
            text = body.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            # 限制最大 300 行
            return "\n".join(lines[:300])

        return ""

    def close(self):
        """释放 HTTP 客户端"""
        if self._client:
            self._client.close()
            self._client = None


web_content_fetcher = WebContentFetcher()
