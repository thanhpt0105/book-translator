"""
Data models for the translation system.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field


class ChapterMetadata(BaseModel):
    """Metadata for a chapter."""
    crawled_at: Optional[datetime] = None
    translated_at: Optional[datetime] = None
    word_count: int = 0
    url: str = ""
    translator: str = ""  # AI model used


class Chapter(BaseModel):
    """Represents a book chapter in both Chinese and Vietnamese."""
    chapter_number: int
    title_chinese: str
    title_vietnamese: str = ""
    content_chinese: str
    content_vietnamese: str = ""
    metadata: ChapterMetadata = Field(default_factory=ChapterMetadata)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(mode='json')
    
    def save_raw(self, base_dir: Path):
        """Save raw Chinese content."""
        file_path = base_dir / f"chapter_{self.chapter_number:04d}.json"
        file_path.write_text(self.model_dump_json(indent=2), encoding='utf-8')
    
    def save_translated(self, base_dir: Path):
        """Save translated Vietnamese content."""
        file_path = base_dir / f"chapter_{self.chapter_number:04d}.json"
        file_path.write_text(self.model_dump_json(indent=2), encoding='utf-8')


class Character(BaseModel):
    """Represents a character in the story."""
    chinese: str
    vietnamese: str = ""
    pinyin: str = ""
    role: str = "unknown"  # protagonist, antagonist, supporting, minor
    first_appearance: int = 0
    aliases: List[str] = Field(default_factory=list)
    description: str = ""


class CharacterGlossary(BaseModel):
    """Collection of characters and their translations."""
    characters: List[Character] = Field(default_factory=list)
    
    def add_character(self, character: Character):
        """Add a character to the glossary."""
        self.characters.append(character)
    
    def get_by_chinese_name(self, name: str) -> Optional[Character]:
        """Find character by Chinese name."""
        for char in self.characters:
            if char.chinese == name or name in char.aliases:
                return char
        return None
    
    def get_name_mapping(self) -> dict:
        """Get a simple Chinese -> Vietnamese name mapping."""
        return {char.chinese: char.vietnamese for char in self.characters if char.vietnamese}
    
    def save(self, file_path: Path):
        """Save glossary to file."""
        file_path.write_text(self.model_dump_json(indent=2), encoding='utf-8')
    
    @classmethod
    def load(cls, file_path: Path) -> "CharacterGlossary":
        """Load glossary from file."""
        if not file_path.exists():
            return cls()
        return cls.model_validate_json(file_path.read_text(encoding='utf-8'))


class BookMetadata(BaseModel):
    """Metadata about the entire book."""
    book_id: int
    title_chinese: str = ""
    title_vietnamese: str = ""
    author: str = ""
    genre: str = ""
    total_chapters: int = 0
    base_url: str = ""
    crawl_started: Optional[datetime] = None
    crawl_completed: Optional[datetime] = None
    translation_started: Optional[datetime] = None
    translation_completed: Optional[datetime] = None
