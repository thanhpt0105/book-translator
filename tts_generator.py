"""
Text-to-Speech generator for Vietnamese audiobook creation.
Supports multiple TTS providers with natural storytelling voice.
"""
import os
from pathlib import Path
from typing import Optional, Literal
from loguru import logger
from tqdm import tqdm
import json

from config import settings
from models import Chapter


TTSProvider = Literal["edge-tts", "openai", "elevenlabs", "google"]


class TTSGenerator:
    """Generate audio from Vietnamese text using various TTS providers."""
    
    def __init__(
        self,
        provider: TTSProvider = "edge-tts",
        voice: Optional[str] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize TTS generator.
        
        Args:
            provider: TTS service to use
            voice: Voice ID/name (provider-specific)
            output_dir: Directory to save audio files
        """
        self.provider = provider
        self.output_dir = output_dir or settings.data_dir / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default voices for each provider
        self.default_voices = {
            "edge-tts": "vi-VN-NamMinhNeural",  # Male, natural Vietnamese
            "openai": "nova",  # Multilingual, good for storytelling
            "elevenlabs": "21m00Tcm4TlvDq8ikWAM",  # Rachel (can be cloned)
            "google": "vi-VN-Standard-A"  # Vietnamese female
        }
        
        self.voice = voice or self.default_voices.get(provider)
        
        # Initialize provider
        if provider == "edge-tts":
            self._init_edge_tts()
        elif provider == "openai":
            self._init_openai_tts()
        elif provider == "elevenlabs":
            self._init_elevenlabs()
        elif provider == "google":
            self._init_google_tts()
    
    def _init_edge_tts(self):
        """Initialize Microsoft Edge TTS (FREE, good quality)."""
        try:
            import edge_tts
            self.edge_tts = edge_tts
            logger.info(f"Initialized Edge TTS with voice: {self.voice}")
        except ImportError:
            logger.error("edge-tts not installed. Run: pip install edge-tts")
            raise
    
    def _init_openai_tts(self):
        """Initialize OpenAI TTS (PAID, excellent quality)."""
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
            logger.info(f"Initialized OpenAI TTS with voice: {self.voice}")
        except ImportError:
            logger.error("openai not installed. Run: pip install openai")
            raise
    
    def _init_elevenlabs(self):
        """Initialize ElevenLabs TTS (PAID, very natural)."""
        try:
            from elevenlabs import VoiceSettings, set_api_key
            set_api_key(settings.elevenlabs_api_key)
            logger.info(f"Initialized ElevenLabs TTS with voice: {self.voice}")
        except ImportError:
            logger.error("elevenlabs not installed. Run: pip install elevenlabs")
            raise
    
    def _init_google_tts(self):
        """Initialize Google Cloud TTS (PAID, good quality)."""
        try:
            from google.cloud import texttospeech
            self.google_client = texttospeech.TextToSpeechClient()
            logger.info(f"Initialized Google TTS with voice: {self.voice}")
        except ImportError:
            logger.error("google-cloud-texttospeech not installed")
            raise
    
    async def generate_audio_edge(self, text: str, output_file: Path) -> Path:
        """Generate audio using Microsoft Edge TTS (FREE)."""
        communicate = self.edge_tts.Communicate(text, self.voice)
        await communicate.save(str(output_file))
        logger.debug(f"Generated audio: {output_file}")
        return output_file
    
    def generate_audio_openai(self, text: str, output_file: Path) -> Path:
        """Generate audio using OpenAI TTS."""
        response = self.openai_client.audio.speech.create(
            model="tts-1-hd",  # or "tts-1" for faster/cheaper
            voice=self.voice,
            input=text,
            speed=1.0  # Adjust for storytelling pace
        )
        response.stream_to_file(str(output_file))
        logger.debug(f"Generated audio: {output_file}")
        return output_file
    
    def generate_audio_elevenlabs(self, text: str, output_file: Path) -> Path:
        """Generate audio using ElevenLabs."""
        from elevenlabs import generate, save
        
        audio = generate(
            text=text,
            voice=self.voice,
            model="eleven_multilingual_v2"  # Best for Vietnamese
        )
        save(audio, str(output_file))
        logger.debug(f"Generated audio: {output_file}")
        return output_file
    
    def generate_audio_google(self, text: str, output_file: Path) -> Path:
        """Generate audio using Google Cloud TTS."""
        from google.cloud import texttospeech
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="vi-VN",
            name=self.voice,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )
        
        response = self.google_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        output_file.write_bytes(response.audio_content)
        logger.debug(f"Generated audio: {output_file}")
        return output_file
    
    async def generate_chapter_audio(
        self,
        chapter: Chapter,
        split_paragraphs: bool = True
    ) -> list[Path]:
        """
        Generate audio for a single chapter.
        
        Args:
            chapter: Chapter with Vietnamese translation
            split_paragraphs: If True, generate separate audio for each paragraph
        
        Returns:
            List of generated audio file paths
        """
        logger.info(f"Generating audio for chapter {chapter.chapter_number}")
        
        # Create chapter audio directory
        chapter_dir = self.output_dir / f"chapter_{chapter.chapter_number:04d}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        
        audio_files = []
        
        # Add title narration
        title_text = f"Chương {chapter.chapter_number}: {chapter.title_vietnamese}"
        title_file = chapter_dir / "00_title.mp3"
        
        if self.provider == "edge-tts":
            await self.generate_audio_edge(title_text, title_file)
        elif self.provider == "openai":
            self.generate_audio_openai(title_text, title_file)
        elif self.provider == "elevenlabs":
            self.generate_audio_elevenlabs(title_text, title_file)
        elif self.provider == "google":
            self.generate_audio_google(title_text, title_file)
        
        audio_files.append(title_file)
        
        # Process content
        if split_paragraphs:
            paragraphs = chapter.content_vietnamese.split('\n\n')
            for i, paragraph in enumerate(paragraphs, 1):
                if not paragraph.strip():
                    continue
                
                output_file = chapter_dir / f"{i:03d}_paragraph.mp3"
                
                if self.provider == "edge-tts":
                    await self.generate_audio_edge(paragraph, output_file)
                elif self.provider == "openai":
                    self.generate_audio_openai(paragraph, output_file)
                elif self.provider == "elevenlabs":
                    self.generate_audio_elevenlabs(paragraph, output_file)
                elif self.provider == "google":
                    self.generate_audio_google(paragraph, output_file)
                
                audio_files.append(output_file)
        else:
            # Generate single audio file for entire chapter
            output_file = chapter_dir / "full_chapter.mp3"
            
            if self.provider == "edge-tts":
                await self.generate_audio_edge(chapter.content_vietnamese, output_file)
            elif self.provider == "openai":
                self.generate_audio_openai(chapter.content_vietnamese, output_file)
            elif self.provider == "elevenlabs":
                self.generate_audio_elevenlabs(chapter.content_vietnamese, output_file)
            elif self.provider == "google":
                self.generate_audio_google(chapter.content_vietnamese, output_file)
            
            audio_files.append(output_file)
        
        logger.success(f"Generated {len(audio_files)} audio files for chapter {chapter.chapter_number}")
        return audio_files
    
    def merge_audio_files(self, audio_files: list[Path], output_file: Path):
        """Merge multiple audio files into one using ffmpeg."""
        try:
            import subprocess
            
            # Create temp file list for ffmpeg
            list_file = output_file.parent / "filelist.txt"
            with open(list_file, 'w') as f:
                for audio in audio_files:
                    f.write(f"file '{audio.absolute()}'\n")
            
            # Merge using ffmpeg
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_file),
                '-c', 'copy',
                str(output_file)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            list_file.unlink()
            
            logger.success(f"Merged {len(audio_files)} files into {output_file}")
            
        except FileNotFoundError:
            logger.error("ffmpeg not found. Install: brew install ffmpeg")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to merge audio: {e}")
            raise


async def generate_audiobook(
    provider: TTSProvider = "edge-tts",
    voice: Optional[str] = None,
    merge_chapters: bool = False
):
    """
    Generate audiobook from all translated chapters.
    
    Args:
        provider: TTS service to use
        voice: Voice ID (optional, uses default if not specified)
        merge_chapters: If True, merge all chapter audio into single file
    """
    settings.ensure_directories()
    
    tts = TTSGenerator(provider=provider, voice=voice)
    
    # Find all translated chapters
    translated_chapters = sorted(settings.translated_chapters_dir.glob("chapter_*.json"))
    
    logger.info(f"Found {len(translated_chapters)} translated chapters")
    logger.info(f"Using {provider} with voice: {tts.voice}")
    
    all_audio_files = []
    
    for chapter_file in tqdm(translated_chapters, desc="Generating audiobook"):
        # Load chapter
        chapter = Chapter.model_validate_json(chapter_file.read_text(encoding='utf-8'))
        
        # Check if audio already exists
        chapter_dir = tts.output_dir / f"chapter_{chapter.chapter_number:04d}"
        if chapter_dir.exists() and any(chapter_dir.glob("*.mp3")):
            logger.info(f"Audio for chapter {chapter.chapter_number} already exists, skipping")
            if merge_chapters:
                all_audio_files.extend(sorted(chapter_dir.glob("*.mp3")))
            continue
        
        # Generate audio
        try:
            audio_files = await tts.generate_chapter_audio(chapter, split_paragraphs=False)
            if merge_chapters:
                all_audio_files.extend(audio_files)
        except Exception as e:
            logger.error(f"Failed to generate audio for chapter {chapter.chapter_number}: {e}")
            continue
    
    # Merge all chapters into single audiobook file
    if merge_chapters and all_audio_files:
        final_output = settings.output_dir / "audiobook_full.mp3"
        logger.info("Merging all chapters into single audiobook...")
        tts.merge_audio_files(all_audio_files, final_output)
    
    logger.success("Audiobook generation complete!")


if __name__ == "__main__":
    import asyncio
    
    # Generate audiobook using free Edge TTS
    asyncio.run(generate_audiobook(provider="edge-tts"))
