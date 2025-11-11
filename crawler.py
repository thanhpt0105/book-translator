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
        """Extract chapter number from title like '第1212章 ...' or '第一章 ...' or '第二十一章 ...' or '第723~724章'"""
        # First try numeric pattern (may include ranges like 723~724)
        match = re.search(r'第(\d+)(?:~\d+)?章', title)
        if match:
            return int(match.group(1))
        
        # Try Chinese number pattern (may include ranges)
        match = re.search(r'第([零一二三四五六七八九十百千万]+)(?:~[零一二三四五六七八九十百千万\d]+)?章', title)
        if match:
            chinese_num_str = match.group(1)
            return self.chinese_to_number(chinese_num_str)
        
        return None
    
    def chinese_to_number(self, chinese_str: str) -> Optional[int]:
        """Convert Chinese number string to integer."""
        # Map of Chinese digits
        chinese_nums = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
            '十': 10, '百': 100, '千': 1000, '万': 10000
        }
        
        # Simple cases (1-10)
        if chinese_str in chinese_nums:
            return chinese_nums[chinese_str]
        
        # Handle special case: 十 = 10, 十一 = 11, etc.
        if chinese_str.startswith('十') and '百' not in chinese_str:
            if len(chinese_str) == 1:
                return 10
            remainder = chinese_str[1:].replace('零', '')
            if remainder:
                return 10 + chinese_nums.get(remainder[0], 0)
            return 10
        
        # Handle numbers like 二十, 三十, etc.
        if '十' in chinese_str and '百' not in chinese_str and '千' not in chinese_str:
            parts = chinese_str.split('十')
            if len(parts) == 2:
                tens = chinese_nums.get(parts[0], 1) if parts[0] else 1
                ones_str = parts[1].replace('零', '')
                ones = chinese_nums.get(ones_str, 0) if ones_str else 0
                return tens * 10 + ones
        
        # Handle thousands: 一千二百三十四, 一千零一, etc.
        # IMPORTANT: Check thousands BEFORE hundreds to avoid incorrect splits
        if '千' in chinese_str:
            parts = chinese_str.split('千')
            thousands = chinese_nums.get(parts[0], 1) if parts[0] else 1
            result = thousands * 1000
            
            if len(parts) > 1 and parts[1]:
                remainder_str = parts[1]
                
                # Handle patterns like 一千零一 (1001)
                if '零' in remainder_str:
                    digits = [c for c in remainder_str if c != '零']
                    if len(digits) == 1 and '百' not in remainder_str and '十' not in remainder_str:
                        # Single digit after 零: e.g., 一千零一 -> 1001
                        result += chinese_nums.get(digits[0], 0)
                    else:
                        # Has hundreds or tens, remove 零 and parse
                        clean_str = remainder_str.replace('零', '')
                        sub_result = self.chinese_to_number(clean_str)
                        if sub_result:
                            result += sub_result
                else:
                    # No 零, normal parsing
                    sub_result = self.chinese_to_number(remainder_str)
                    if sub_result:
                        result += sub_result
            
            return result
        
        # Handle hundreds: 一百二十三, 一百零一, 三百, etc.
        if '百' in chinese_str:
            parts = chinese_str.split('百')
            hundreds = chinese_nums.get(parts[0], 1) if parts[0] else 1
            result = hundreds * 100
            
            if len(parts) > 1 and parts[1]:
                remainder_str = parts[1]
                
                # Handle patterns like 一百零一 (101), 三百零五 (305)
                if '零' in remainder_str:
                    # Remove all 零 and get remaining digits
                    digits = [c for c in remainder_str if c != '零']
                    if len(digits) == 1:
                        # Single digit after 零: e.g., 一百零一 -> 101
                        result += chinese_nums.get(digits[0], 0)
                    elif len(digits) > 1 and '十' in remainder_str:
                        # Has tens: e.g., shouldn't normally have 零 with 十
                        # But handle anyway: remove 零 and parse
                        clean_str = remainder_str.replace('零', '')
                        sub_result = self.chinese_to_number(clean_str)
                        if sub_result:
                            result += sub_result
                else:
                    # No 零, normal parsing: e.g., 一百二十三 -> 123
                    sub_result = self.chinese_to_number(remainder_str)
                    if sub_result:
                        result += sub_result
            
            return result
        
        logger.warning(f"Could not parse Chinese number: {chinese_str}")
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
        
        # Find the latest crawled chapter to resume from
        existing_chapters = sorted(settings.raw_chapters_dir.glob("chapter_*.json"))
        if existing_chapters:
            # Get the highest chapter number
            last_chapter_file = existing_chapters[-1]
            try:
                last_chapter = Chapter.model_validate_json(last_chapter_file.read_text(encoding='utf-8'))
                latest_chapter_num = last_chapter.chapter_number
                if latest_chapter_num >= start:
                    start = latest_chapter_num + 1
                    logger.info(f"Resuming from chapter {start} (found {len(existing_chapters)} existing chapters)")
            except Exception as e:
                logger.warning(f"Could not read last chapter file: {e}")
        
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
