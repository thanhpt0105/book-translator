"""
Character name extraction and glossary management.
"""
import re
from typing import List, Set
from pathlib import Path
import jieba
from loguru import logger
from collections import Counter

from config import settings
from models import Chapter, Character, CharacterGlossary


class CharacterExtractor:
    """Extract and manage character names from Chinese text."""
    
    def __init__(self):
        # Common Chinese surnames for name detection
        self.common_surnames = {
            '王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴',
            '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '高', '罗',
            '郑', '梁', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹',
            '彭', '曾', '萧', '田', '董', '潘', '袁', '蔡', '蒋', '余',
            '叶', '陶', '姜', '范', '方', '石', '姚', '廖', '邹', '陆',
        }
    
    def extract_potential_names(self, text: str) -> List[str]:
        """Extract potential character names from text."""
        names = []
        
        # Pattern 1: Common Chinese name pattern (2-3 characters starting with surname)
        for surname in self.common_surnames:
            # 2-character names
            pattern_2 = f'{surname}[一-龥](?![一-龥])'
            matches_2 = re.findall(pattern_2, text)
            names.extend(matches_2)
            
            # 3-character names
            pattern_3 = f'{surname}[一-龥]{{2}}(?![一-龥])'
            matches_3 = re.findall(pattern_3, text)
            names.extend(matches_3)
        
        # Pattern 2: Names in quotes or after titles
        title_pattern = r'(局长|警官|先生|女士|小姐|夫人|老板|师傅|大师|将军|总裁|董事长|经理)([一-龥]{2,3})'
        title_matches = re.findall(title_pattern, text)
        names.extend([match[1] for match in title_matches])
        
        return names
    
    def count_name_frequencies(self, chapters: List[Chapter]) -> Counter:
        """Count frequency of potential names across chapters."""
        all_names = []
        
        for chapter in chapters:
            names = self.extract_potential_names(chapter.content_chinese)
            all_names.extend(names)
        
        return Counter(all_names)
    
    def filter_common_names(self, name_freq: Counter, min_frequency: int = 3) -> List[str]:
        """Filter names that appear frequently enough to be characters."""
        return [name for name, count in name_freq.items() if count >= min_frequency]
    
    def build_glossary_from_chapters(
        self, 
        chapters: List[Chapter],
        min_frequency: int = 3
    ) -> CharacterGlossary:
        """Build character glossary from chapters."""
        logger.info(f"Extracting characters from {len(chapters)} chapters")
        
        # Count name frequencies
        name_freq = self.count_name_frequencies(chapters)
        
        # Filter to get actual character names
        character_names = self.filter_common_names(name_freq, min_frequency)
        
        logger.info(f"Found {len(character_names)} potential characters")
        
        # Create glossary
        glossary = CharacterGlossary()
        
        for name in sorted(character_names, key=lambda n: name_freq[n], reverse=True):
            # Find first appearance
            first_chapter = 0
            for chapter in chapters:
                if name in chapter.content_chinese:
                    first_chapter = chapter.chapter_number
                    break
            
            # Determine role based on frequency
            freq = name_freq[name]
            if freq > 50:
                role = "protagonist"
            elif freq > 20:
                role = "major"
            elif freq > 10:
                role = "supporting"
            else:
                role = "minor"
            
            character = Character(
                chinese=name,
                vietnamese="",  # To be filled manually or by AI
                first_appearance=first_chapter,
                role=role,
            )
            
            glossary.add_character(character)
        
        return glossary
    
    def auto_translate_names(self, glossary: CharacterGlossary, translator) -> CharacterGlossary:
        """Auto-translate character names using AI."""
        logger.info("Auto-translating character names")
        
        for character in glossary.characters:
            if not character.vietnamese:
                try:
                    prompt = f"Translate this Chinese name to Vietnamese phonetically (romanization): {character.chinese}\nProvide ONLY the Vietnamese name, nothing else."
                    character.vietnamese = translator.translate_text(prompt).strip()
                    logger.debug(f"{character.chinese} → {character.vietnamese}")
                except Exception as e:
                    logger.error(f"Failed to translate name {character.chinese}: {e}")
                    character.vietnamese = character.chinese
        
        return glossary


def build_character_glossary():
    """Main function to build character glossary."""
    settings.ensure_directories()
    
    # Load all raw chapters
    chapter_files = sorted(settings.raw_chapters_dir.glob("chapter_*.json"))
    
    if not chapter_files:
        logger.error("No chapters found. Run crawler first!")
        return
    
    # Load first N chapters for initial glossary
    num_chapters = min(10, len(chapter_files))
    chapters = []
    
    for chapter_file in chapter_files[:num_chapters]:
        chapter = Chapter.model_validate_json(chapter_file.read_text(encoding='utf-8'))
        chapters.append(chapter)
    
    logger.info(f"Building glossary from first {num_chapters} chapters")
    
    # Extract characters
    extractor = CharacterExtractor()
    glossary = extractor.build_glossary_from_chapters(chapters)
    
    # Save glossary
    glossary_path = settings.glossary_dir / "characters.json"
    glossary.save(glossary_path)
    
    logger.success(f"Glossary saved to {glossary_path}")
    logger.info(f"Total characters: {len(glossary.characters)}")
    
    # Print top characters
    logger.info("Top characters:")
    for char in glossary.characters[:10]:
        logger.info(f"  {char.chinese} ({char.role}, appears in chapter {char.first_appearance})")


if __name__ == "__main__":
    build_character_glossary()
