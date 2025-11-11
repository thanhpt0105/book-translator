"""
AI-powered translation module with context awareness.
"""
import os
from typing import List, Optional, Dict
from pathlib import Path
from openai import OpenAI
from anthropic import Anthropic
from loguru import logger
from tqdm import tqdm

from config import settings
from models import Chapter, CharacterGlossary


class Translator:
    """AI-powered translator with context awareness."""
    
    def __init__(self, glossary: Optional[CharacterGlossary] = None):
        self.provider = settings.ai_provider
        self.model = settings.ai_model
        self.glossary = glossary or CharacterGlossary()
        
        # Initialize AI client
        if self.provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
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
"""
        
        if name_mapping:
            prompt += "\n\nCharacter Name Glossary (Chinese → Vietnamese):\n"
            for chinese, vietnamese in name_mapping.items():
                prompt += f"- {chinese} → {vietnamese}\n"
        
        return prompt
    
    def translate_with_openai(self, text: str, context: str = "") -> str:
        """Translate using OpenAI GPT."""
        system_prompt = self.build_system_prompt()
        
        user_message = f"Translate the following Chinese text to Vietnamese:\n\n{text}"
        if context:
            user_message = f"Context from previous section:\n{context}\n\n" + user_message
        
        try:
            # Use max_completion_tokens for newer models like gpt-5, fall back to max_tokens for older models
            completion_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
            }
            
            # GPT-5 and o1 models use max_completion_tokens and don't support temperature
            if "gpt-5" in self.model or "o1" in self.model:
                completion_params["max_completion_tokens"] = settings.max_tokens_per_request
                # GPT-5 doesn't support custom temperature, only default value of 1
            else:
                completion_params["max_tokens"] = settings.max_tokens_per_request
                completion_params["temperature"] = settings.temperature
            
            response = self.client.chat.completions.create(**completion_params)
            
            translation = response.choices[0].message.content
            if translation:
                translation = translation.strip()
                logger.debug(f"Translation received: {len(translation)} characters")
            else:
                logger.warning("Empty translation received from API")
                translation = ""
            return translation
            
        except Exception as e:
            logger.error(f"OpenAI translation error: {e}")
            raise
    
    def translate_with_anthropic(self, text: str, context: str = "") -> str:
        """Translate using Anthropic Claude."""
        system_prompt = self.build_system_prompt()
        
        user_message = f"Translate the following Chinese text to Vietnamese:\n\n{text}"
        if context:
            user_message = f"Context from previous section:\n{context}\n\n" + user_message
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.max_tokens_per_request,
                temperature=settings.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            translation = response.content[0].text.strip()
            return translation
            
        except Exception as e:
            logger.error(f"Anthropic translation error: {e}")
            raise
    
    def translate_text(self, text: str, context: str = "") -> str:
        """Translate text using the configured AI provider."""
        if self.provider == "openai":
            return self.translate_with_openai(text, context)
        elif self.provider == "anthropic":
            return self.translate_with_anthropic(text, context)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def translate_chapter_title(self, title_chinese: str) -> str:
        """Translate chapter title."""
        prompt = f"Translate this Chinese chapter title to Vietnamese (just the translation, no explanation):\n\n{title_chinese}"
        return self.translate_text(prompt)
    
    def split_into_chunks(self, text: str, max_length: int = 2000) -> List[str]:
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
        chapter.metadata.translator = f"{self.provider}:{self.model}"
        
        logger.success(f"Translated chapter {chapter.chapter_number}")
        return chapter


def translate_all_chapters():
    """Translate all crawled chapters."""
    settings.ensure_directories()
    
    # Load glossary
    glossary_path = settings.glossary_dir / "characters.json"
    glossary = CharacterGlossary.load(glossary_path)
    
    translator = Translator(glossary)
    
    # Find all raw chapters
    raw_chapters = sorted(settings.raw_chapters_dir.glob("chapter_*.json"))
    
    logger.info(f"Found {len(raw_chapters)} chapters to translate")
    
    previous_context = ""
    
    for chapter_file in tqdm(raw_chapters, desc="Translating chapters"):
        # Load chapter
        chapter = Chapter.model_validate_json(chapter_file.read_text(encoding='utf-8'))
        
        # Check if already translated
        translated_file = settings.translated_chapters_dir / chapter_file.name
        if translated_file.exists():
            logger.info(f"Chapter {chapter.chapter_number} already translated, skipping")
            continue
        
        # Translate
        try:
            chapter = translator.translate_chapter(chapter, previous_context)
            
            # Save translated chapter
            chapter.save_translated(settings.translated_chapters_dir)
            
            # Update context for next chapter
            previous_context = chapter.content_vietnamese[-1000:]
            
        except Exception as e:
            logger.error(f"Failed to translate chapter {chapter.chapter_number}: {e}")
            continue


if __name__ == "__main__":
    translate_all_chapters()
