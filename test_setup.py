"""
Test script to verify Python environment setup.
Run this to diagnose installation issues.
"""
import sys

print("=" * 60)
print("Python Environment Diagnostic")
print("=" * 60)
print(f"\nPython Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Python Path: {sys.path[0]}")

print("\n" + "=" * 60)
print("Required Modules Check")
print("=" * 60)

required_modules = {
    'loguru': 'Logging',
    'requests': 'Web scraping',
    'bs4': 'HTML parsing (BeautifulSoup)',
    'lxml': 'XML/HTML parser',
    'openai': 'OpenAI API',
    'anthropic': 'Anthropic API',
    'jieba': 'Chinese text segmentation',
    'pydantic': 'Data validation',
    'pydantic_settings': 'Settings management',
    'dotenv': 'Environment variables',
    'tqdm': 'Progress bars',
    'ebooklib': 'EPUB generation (optional)',
    'edge_tts': 'Text-to-speech (optional)',
}

installed = []
missing = []

for module, description in required_modules.items():
    try:
        __import__(module)
        installed.append(module)
        print(f"✓ {module:<20} - {description}")
    except ImportError as e:
        missing.append(module)
        print(f"✗ {module:<20} - {description} - NOT INSTALLED")
        print(f"  Error: {e}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print(f"Installed: {len(installed)}/{len(required_modules)}")
print(f"Missing: {len(missing)}")

if missing:
    print("\n⚠️  Missing modules:")
    for module in missing:
        print(f"   - {module}")
    print("\nTo install missing modules:")
    print("   pip install -r requirements.txt")
    print("\nOr install individually:")
    for module in missing:
        # Handle special module names
        if module == 'bs4':
            print(f"   pip install beautifulsoup4")
        elif module == 'dotenv':
            print(f"   pip install python-dotenv")
        elif module == 'pydantic_settings':
            print(f"   pip install pydantic-settings")
        else:
            print(f"   pip install {module}")
else:
    print("\n✅ All required modules are installed!")
    print("\nYou can now run:")
    print("   python main.py status")
    print("   python main.py crawl")

print("\n" + "=" * 60)
print("Environment Info")
print("=" * 60)

# Check if in virtual environment
in_venv = hasattr(sys, 'real_prefix') or (
    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
)
print(f"In Virtual Environment: {in_venv}")
if in_venv:
    print(f"Virtual Environment: {sys.prefix}")
else:
    print("⚠️  Not using virtual environment (recommended to use one)")

print("\n" + "=" * 60)
