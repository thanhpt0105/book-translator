"""
Configuration management for the translation system.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    elevenlabs_api_key: str = ""
    google_application_credentials: str = ""  # Path to Google Cloud credentials JSON
    
    # Crawler Settings
    base_url: str = "https://ixdzs.tw/read/273426/"
    book_id: int = 273426
    start_chapter: int = 1
    end_chapter: str = "auto"
    crawl_delay: float = 2.0
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    # Translation Settings
    ai_provider: str = "openai"  # "openai" or "anthropic"
    ai_model: str = "gpt-4o"  # GPT-4o - best for translation
    max_tokens_per_request: int = 4000
    translation_batch_size: int = 5
    context_window_paragraphs: int = 3
    temperature: float = 0.3
    
    # Text-to-Speech Settings
    tts_provider: str = "edge-tts"  # "edge-tts", "openai", "elevenlabs", "google"
    tts_voice: str = "vi-VN-NamMinhNeural"  # Default Vietnamese voice
    tts_merge_chapters: bool = False  # Merge all chapters into single audio file
    
    # Storage Paths
    data_dir: Path = Path("./data")
    output_dir: Path = Path("./output")
    
    # Output Formats
    output_formats: str = "json,markdown,docx,epub,pdf"  # Supported: markdown/md, docx/word, epub, pdf
    
    # Logging
    log_level: str = "INFO"
    log_file: Path = Path("./logs/translation.log")
    
    @property
    def raw_chapters_dir(self) -> Path:
        """Directory for raw Chinese chapters."""
        return self.data_dir / "raw" / "chapters"
    
    @property
    def translated_chapters_dir(self) -> Path:
        """Directory for translated Vietnamese chapters."""
        return self.data_dir / "translated" / "chapters"
    
    @property
    def glossary_dir(self) -> Path:
        """Directory for glossaries."""
        return self.data_dir / "glossary"
    
    def ensure_directories(self):
        """Create all required directories."""
        dirs = [
            self.data_dir / "raw" / "chapters",
            self.data_dir / "translated" / "chapters",
            self.data_dir / "glossary",
            self.output_dir,
            self.log_file.parent,
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
