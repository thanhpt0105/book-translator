"""
Main CLI for the translation system.
"""
import sys
from pathlib import Path
from loguru import logger

from config import settings
from crawler import NovelCrawler
from character_extractor import CharacterExtractor, build_character_glossary, update_glossary_translations
from translator import Translator, translate_all_chapters
from models import CharacterGlossary


def setup_logging():
    """Configure logging."""
    settings.ensure_directories()
    
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=settings.log_level,
    )
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation="10 MB",
    )


def cmd_crawl():
    """Crawl chapters from website."""
    logger.info("=== Starting Chapter Crawling ===")
    settings.ensure_directories()
    
    crawler = NovelCrawler()
    start = settings.start_chapter
    end = None if settings.end_chapter == "auto" else int(settings.end_chapter)
    
    chapters = crawler.crawl_chapters(start, end)
    logger.success(f"Crawling completed! Total chapters: {len(chapters)}")


def cmd_extract_characters():
    """Extract character names and build glossary."""
    logger.info("=== Extracting Characters ===")
    build_character_glossary()


def cmd_update_characters():
    """Update character glossary with Vietnamese translations."""
    logger.info("=== Updating Character Translations ===")
    update_glossary_translations()


def cmd_translate():
    """Translate all chapters."""
    logger.info("=== Starting Translation ===")
    translate_all_chapters()


def cmd_translate_local():
    """Translate all chapters using local LLM."""
    logger.info("=== Starting Local LLM Translation ===")
    from local_llm_translator import translate_all_chapters_local
    
    # You can customize the base URL here
    base_url = "http://localhost:1234/v1"
    translate_all_chapters_local(base_url)


def cmd_export():
    """Export translated chapters to readable formats."""
    logger.info("=== Exporting Translations ===")
    settings.ensure_directories()
    
    # Load all translated chapters
    chapter_files = sorted(settings.translated_chapters_dir.glob("chapter_*.json"))
    
    if not chapter_files:
        logger.error("No translated chapters found!")
        return
    
    from models import Chapter
    from exporter import export_to_markdown, export_to_docx, export_to_epub, export_to_pdf
    
    chapters = []
    for chapter_file in chapter_files:
        chapter = Chapter.model_validate_json(chapter_file.read_text(encoding='utf-8'))
        chapters.append(chapter)
    
    # Sort by chapter number
    chapters.sort(key=lambda c: c.chapter_number)
    
    # Get output formats from config
    output_formats = settings.output_formats.lower().split(',')
    
    # Export to requested formats
    if 'markdown' in output_formats or 'md' in output_formats:
        output_file = settings.output_dir / "full_book_vietnamese.md"
        export_to_markdown(chapters, output_file)
    
    if 'docx' in output_formats or 'word' in output_formats:
        output_file = settings.output_dir / "full_book_vietnamese.docx"
        export_to_docx(chapters, output_file)
    
    if 'epub' in output_formats:
        output_file = settings.output_dir / "full_book_vietnamese.epub"
        export_to_epub(chapters, output_file)
    
    if 'pdf' in output_formats:
        output_file = settings.output_dir / "full_book_vietnamese.pdf"
        export_to_pdf(chapters, output_file)
    
    logger.success("Export completed!")


def cmd_generate_audio():
    """Generate audiobook from translated chapters."""
    logger.info("=== Generating Audiobook ===")
    import asyncio
    from tts_generator import generate_audiobook
    
    provider = settings.tts_provider
    voice = settings.tts_voice if settings.tts_voice else None
    merge = settings.tts_merge_chapters
    
    logger.info(f"TTS Provider: {provider}")
    logger.info(f"Voice: {voice or 'default'}")
    logger.info(f"Merge chapters: {merge}")
    
    asyncio.run(generate_audiobook(provider=provider, voice=voice, merge_chapters=merge))


def cmd_status():
    """Show status of the translation project."""
    logger.info("=== Project Status ===")
    
    # Count chapters
    raw_count = len(list(settings.raw_chapters_dir.glob("chapter_*.json")))
    translated_count = len(list(settings.translated_chapters_dir.glob("chapter_*.json")))
    
    logger.info(f"Raw chapters crawled: {raw_count}")
    logger.info(f"Chapters translated: {translated_count}")
    
    # Check glossary
    glossary_path = settings.glossary_dir / "characters.json"
    if glossary_path.exists():
        glossary = CharacterGlossary.load(glossary_path)
        logger.info(f"Characters in glossary: {len(glossary.characters)}")
    else:
        logger.info("No character glossary found")
    
    if raw_count > 0:
        progress = (translated_count / raw_count) * 100
        logger.info(f"Translation progress: {progress:.1f}%")


def main():
    """Main CLI entry point."""
    setup_logging()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        print("\nCommands:")
        print("  crawl              - Crawl chapters from website")
        print("  extract-characters - Extract character names and build glossary")
        print("  update-characters  - Update character names with Vietnamese translations")
        print("  translate          - Translate all crawled chapters (using OpenAI/Anthropic)")
        print("  translate-local    - Translate using local LLM (LM Studio)")
        print("  export             - Export translations to Markdown, Word, EPUB, PDF")
        print("  generate-audio     - Generate audiobook from translations")
        print("  status             - Show project status")
        print("\nFull workflow:")
        print("  1. python main.py crawl")
        print("  2. python main.py extract-characters")
        print("  3. python main.py update-characters  # Auto-translate character names")
        print("  4. (Manually review and edit data/glossary/characters.json)")
        print("  5. python main.py translate-local  # Using local LLM")
        print("  6. python main.py export            # Exports to .md, .docx, .epub, .pdf")
        print("  7. python main.py generate-audio   # Generate audiobook")
        print("\nNote: Configure export formats in .env file (OUTPUT_FORMATS=markdown,docx,epub,pdf)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    commands = {
        'crawl': cmd_crawl,
        'extract-characters': cmd_extract_characters,
        'update-characters': cmd_update_characters,
        'translate': cmd_translate,
        'translate-local': cmd_translate_local,
        'export': cmd_export,
        'generate-audio': cmd_generate_audio,
        'status': cmd_status,
    }
    
    if command not in commands:
        logger.error(f"Unknown command: {command}")
        sys.exit(1)
    
    try:
        commands[command]()
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
