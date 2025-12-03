"""
Local LLM translator using LM Studio or any OpenAI-compatible API.
"""
from typing import Optional
import requests
from loguru import logger
from tqdm import tqdm

from config import settings
from models import Chapter, CharacterGlossary


class LocalLLMTranslator:
    """Translator using local LLM via OpenAI-compatible API."""
    
    def __init__(self, 
                 base_url: str = "http://localhost:1234/v1",
                 model: str = "local-model",
                 glossary: Optional[CharacterGlossary] = None):
        self.base_url = base_url
        self.model = model
        self.glossary = glossary or CharacterGlossary()
        self.api_url = f"{base_url}/chat/completions"
        
    def build_system_prompt(self) -> str:
        """Build the system prompt for translation."""
        name_mapping = self.glossary.get_name_mapping()
        
        prompt = """You are a professional Chinese-to-Vietnamese translator specializing in novels.

Your task is to translate Chinese text to Vietnamese while:
1. Maintaining character name consistency using the provided glossary
2. Preserving the narrative tone, style, and atmosphere
3. Keeping cultural nuances and idioms natural in Vietnamese
4. Ensuring smooth, readable Vietnamese prose

Translation Guidelines:
- Use consistent character names from the glossary
- Maintain paragraph structure
- Keep dialogue natural and flowing
- Preserve emotional tone and intensity
- Use appropriate Vietnamese honorifics and formal/informal speech
- ONLY output the Vietnamese translation, no explanations or comments
"""
        
        if name_mapping:
            prompt += "\n\nCharacter Name Glossary (Chinese → Vietnamese):\n"
            for chinese, vietnamese in name_mapping.items():
                prompt += f"- {chinese} → {vietnamese}\n"
        
        return prompt
    
    def translate_text(self, text: str, context: str = "") -> str:
        """Translate text using local LLM."""
        system_prompt = self.build_system_prompt()
        
        user_message = f"Translate the following Chinese text to Vietnamese:\n\n{text}"
        if context:
            user_message = f"Context from previous section:\n{context}\n\n" + user_message
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.3,
                "max_tokens": 4000,
                "stream": False
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=300  # 5 minute timeout for long translations
            )
            response.raise_for_status()
            
            result = response.json()
            translation = result['choices'][0]['message']['content']
            
            if translation:
                translation = translation.strip()
                logger.debug(f"Translation received: {len(translation)} characters")
            else:
                logger.warning("Empty translation received from local LLM")
                translation = ""
                
            return translation
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Local LLM API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise
    
    def translate_chapter_title(self, title_chinese: str) -> str:
        """Translate chapter title."""
        prompt = f"Translate this Chinese chapter title to Vietnamese (just the translation, no explanation):\n\n{title_chinese}"
        return self.translate_text(prompt)
    
    def split_into_chunks(self, text: str, max_length: int = 2000) -> list:
        """Split text into chunks for translation."""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            if current_length + para_length > max_length and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def translate_chapter(self, chapter: Chapter, previous_context: str = "") -> Chapter:
        """Translate a complete chapter."""
        logger.info(f"Translating chapter {chapter.chapter_number}: {chapter.title_chinese}")
        
        # Translate title
        chapter.title_vietnamese = self.translate_chapter_title(chapter.title_chinese)
        
        # Split content into chunks if needed
        chunks = self.split_into_chunks(chapter.content_chinese)
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            logger.debug(f"Translating chunk {i+1}/{len(chunks)}")
            
            # Use previous chunk as context for continuity
            context = previous_context if i == 0 else translated_chunks[-1][-500:]
            
            translated = self.translate_text(chunk, context)
            translated_chunks.append(translated)
        
        chapter.content_vietnamese = '\n\n'.join(translated_chunks)
        chapter.metadata.translator = f"local-llm:{self.model}"
        
        logger.success(f"Translated chapter {chapter.chapter_number}")
        return chapter


def translate_all_chapters_local(base_url: str = "http://localhost:1234/v1", chapter_from: int = None, chapter_to: int = None):
    """Translate all crawled chapters using local LLM, with optional chapter range."""
    settings.ensure_directories()
    
    # Load glossary
    glossary_path = settings.glossary_dir / "characters.json"
    glossary = CharacterGlossary.load(glossary_path)
    
    translator = LocalLLMTranslator(base_url=base_url, glossary=glossary)
    
    # Find all raw chapters
    raw_chapters = sorted(settings.raw_chapters_dir.glob("chapter_*.json"))
    
    logger.info(f"Found {len(raw_chapters)} chapters to translate")
    
    previous_context = ""
    
    for chapter_file in tqdm(raw_chapters, desc="Translating chapters"):
        # Load chapter
        chapter = Chapter.model_validate_json(chapter_file.read_text(encoding='utf-8'))
        
        # Filter by chapter range if specified
        if chapter_from is not None and chapter_to is not None:
            if not (chapter_from <= chapter.chapter_number <= chapter_to):
                continue
        
        # Check if already translated
        translated_file = settings.translated_chapters_dir / chapter_file.name
        if translated_file.exists():
            logger.info(f"Chapter {chapter.chapter_number} already translated, skipping")
            # Load previous context from existing translation
            existing = Chapter.model_validate_json(translated_file.read_text(encoding='utf-8'))
            previous_context = existing.content_vietnamese[-1000:]
            continue
        
        # Translate
        try:
            chapter = translator.translate_chapter(chapter, previous_context)
            # Remove <think>...</think> tags from translation and title
            import re
            chapter.content_vietnamese = re.sub(r'<think>.*?</think>', '', chapter.content_vietnamese, flags=re.DOTALL)
            chapter.title_vietnamese = re.sub(r'<think>.*?</think>', '', chapter.title_vietnamese, flags=re.DOTALL)
            # Save translated chapter
            chapter.save_translated(settings.translated_chapters_dir)
            # Update context for next chapter
            previous_context = chapter.content_vietnamese[-1000:]
        except Exception as e:
            logger.error(f"Failed to translate chapter {chapter.chapter_number}: {e}")
            continue


if __name__ == "__main__":
    # Test with local LM Studio
    translate_all_chapters_local()
