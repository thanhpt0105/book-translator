"""
Web crawler for extracting Chinese novel chapters.
"""
import time
import re
from typing import Optional, List, Tuple
from pathlib import Path
import requests
import urllib3
from bs4 import BeautifulSoup
from loguru import logger
from tqdm import tqdm

from config import settings
from models import Chapter, ChapterMetadata, BookMetadata

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NovelCrawler:
    """Crawler for ixdzs.tw novel website."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        # Disable SSL verification for sites with self-signed certificates
        self.session.verify = False
        self.base_url = settings.base_url
        self.book_id = settings.book_id
        
    def get_chapter_url(self, chapter_number: int) -> str:
        """Generate chapter URL from chapter number."""
        # URL pattern: https://ixdzs.tw/read/273426/p2.html for chapter 1
        # The page number is chapter_number + 1
        page_num = chapter_number + 1
        return f"https://ixdzs.tw/read/{self.book_id}/p{page_num}.html"
    
    def extract_chapter_number_from_title(self, title: str) -> Optional[int]:
        """Extract chapter number from title like '第1212章 ...' or '第一章 ...'"""
        # First try numeric pattern
        match = re.search(r'第(\d+)章', title)
        if match:
            return int(match.group(1))
        
        # Map Chinese numbers to integers
        chinese_nums = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '百': 100, '千': 1000
        }
        
        # Try Chinese number pattern (e.g., 第一章, 第十二章)
        match = re.search(r'第([一二三四五六七八九十百千]+)章', title)
        if match:
            chinese_num = match.group(1)
            # Simple conversion for common cases
            if chinese_num in chinese_nums:
                return chinese_nums[chinese_num]
            # Handle compound numbers like 十二, 二十三
            if len(chinese_num) == 2:
                if chinese_num[0] == '十':
                    return 10 + chinese_nums.get(chinese_num[1], 0)
                elif chinese_num[1] == '十':
                    return chinese_nums.get(chinese_num[0], 0) * 10
        
        return None
    
    def parse_chapter(self, html: str, url: str) -> Optional[Chapter]:
        """Parse chapter content from HTML."""
        soup = BeautifulSoup(html, 'lxml')
        
        # Find chapter title (usually in h1 or h2)
        title_elem = soup.find(['h1', 'h2', 'h3'])
        if not title_elem:
            logger.warning(f"No title found for {url}")
            return None
        
        title = title_elem.get_text(strip=True)
        chapter_num = self.extract_chapter_number_from_title(title)
        
        if not chapter_num:
            logger.warning(f"Could not extract chapter number from title: {title}")
            return None
        
        # Extract main content
        # The content appears to be in divs or direct text after the title
        content_parts = []
        
        # Find all text content after the title
        for elem in soup.find_all(['p', 'div']):
            text = elem.get_text(strip=True)
            # Filter out navigation, ads, and recommendations
            if text and len(text) > 20:  # Avoid short navigation text
                if '猜您喜歡' not in text and '下一章' not in text and '上一章' not in text:
                    content_parts.append(text)
        
        content = '\n\n'.join(content_parts)
        
        if not content or len(content) < 100:
            logger.warning(f"Content too short for chapter {chapter_num}")
            return None
        
        metadata = ChapterMetadata(
            url=url,
            word_count=len(content),
        )
        
        chapter = Chapter(
            chapter_number=chapter_num,
            title_chinese=title,
            content_chinese=content,
            metadata=metadata,
        )
        
        return chapter
    
    def find_next_chapter_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Find the URL of the next chapter."""
        # Look for link with text "下一章"
        next_link = soup.find('a', string=re.compile(r'下一章|次のページ'))
        if next_link and next_link.get('href'):
            href = next_link['href']
            if not href.startswith('http'):
                href = f"https://ixdzs.tw{href}"
            return href
        return None
    
    def crawl_chapter(self, chapter_number: int) -> Optional[Chapter]:
        """Crawl a single chapter."""
        url = self.get_chapter_url(chapter_number)
        
        try:
            logger.info(f"Crawling chapter {chapter_number}: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            chapter = self.parse_chapter(response.text, url)
            
            if chapter:
                logger.success(f"Successfully crawled chapter {chapter_number}")
                return chapter
            else:
                logger.error(f"Failed to parse chapter {chapter_number}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error crawling chapter {chapter_number}: {e}")
            return None
    
    def crawl_chapters(self, start: int, end: Optional[int] = None) -> List[Chapter]:
        """Crawl multiple chapters."""
        chapters = []
        current = start
        
        # Create progress bar
        if end and end != start:
            pbar = tqdm(total=end - start + 1, desc="Crawling chapters")
        else:
            pbar = None
        
        while True:
            # Check if we've reached the end
            if end and current > end:
                break
            
            chapter = self.crawl_chapter(current)
            
            if chapter:
                chapters.append(chapter)
                # Save immediately
                settings.ensure_directories()
                chapter.save_raw(settings.raw_chapters_dir)
                
                if pbar:
                    pbar.update(1)
                
                current += 1
                
                # Rate limiting
                time.sleep(settings.crawl_delay)
            else:
                # If we can't find the chapter, we might have reached the end
                logger.warning(f"Could not crawl chapter {current}, assuming end of book")
                break
        
        if pbar:
            pbar.close()
        
        logger.info(f"Crawled {len(chapters)} chapters total")
        return chapters


def main():
    """Main crawling function."""
    settings.ensure_directories()
    
    crawler = NovelCrawler()
    
    start = settings.start_chapter
    end = None if settings.end_chapter == "auto" else int(settings.end_chapter)
    
    logger.info(f"Starting crawl from chapter {start}")
    chapters = crawler.crawl_chapters(start, end)
    
    logger.success(f"Crawling completed! Total chapters: {len(chapters)}")


if __name__ == "__main__":
    main()
