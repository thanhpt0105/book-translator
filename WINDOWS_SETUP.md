# Windows Setup Guide

## Common Issue: "No module named 'loguru'" after pip install

### Problem
After running `pip install -r requirements.txt` on Windows, you get:
```
ModuleNotFoundError: No module named 'loguru'
```

### Root Cause
Windows often has multiple Python installations, and `pip` and `python` may be using different Python environments.

---

## Solution 1: Use Virtual Environment (Recommended)

### Step 1: Create Virtual Environment
```powershell
# Open PowerShell or Command Prompt
cd path\to\translation

# Create virtual environment
python -m venv .venv
```

### Step 2: Activate Virtual Environment

**PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**If you get execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

**Command Prompt (cmd):**
```cmd
.venv\Scripts\activate.bat
```

### Step 3: Install Dependencies
```powershell
# Make sure you see (.venv) in your prompt
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify Installation
```powershell
python -c "import loguru; print('loguru installed successfully')"
pip list | findstr loguru
```

### Step 5: Run the Project
```powershell
# Crawl chapters
python main.py crawl

# Check status
python main.py status
```

---

## Solution 2: Use Python Module Flag

If you don't want to use virtual environment:

```powershell
# Install using python -m pip instead of just pip
python -m pip install -r requirements.txt

# Run main.py using python -m
python main.py crawl
```

---

## Solution 3: Verify Python/Pip Match

### Check which Python pip is using:
```powershell
# Check Python version
python --version

# Check which pip
pip --version

# Check where Python is installed
where python

# Check where pip is installed
where pip
```

### If they don't match:
```powershell
# Use the full path to Python's pip
python -m pip install -r requirements.txt
```

---

## Solution 4: Reinstall Everything

### Uninstall and reinstall:
```powershell
# Uninstall all packages
pip freeze > installed.txt
pip uninstall -r installed.txt -y

# Reinstall from requirements.txt
pip install -r requirements.txt
```

---

## Complete Windows Setup (Step-by-Step)

### 1. Install Python 3.13
- Download from [python.org](https://www.python.org/downloads/)
- ✅ Check "Add Python to PATH" during installation
- Install for all users or current user

### 2. Clone/Download Project
```powershell
cd C:\Users\YourName\Documents
git clone https://github.com/thanhpt0105/book-translator.git
cd book-translator
```

### 3. Create Virtual Environment
```powershell
python -m venv .venv
```

### 4. Activate Virtual Environment
**PowerShell (Recommended):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
.venv\Scripts\activate.bat
```

You should see `(.venv)` at the beginning of your prompt.

### 5. Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### 6. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 7. Create Configuration
```powershell
# Copy example to .env
copy env.example .env

# Edit .env with your settings (use Notepad)
notepad .env
```

### 8. Test Installation
```powershell
python -c "import loguru; import requests; import bs4; print('All modules installed!')"
```

### 9. Run the Project
```powershell
# Check status
python main.py status

# Crawl chapters (set END_CHAPTER in .env or use environment variable)
set END_CHAPTER=1348
python main.py crawl
```

---

## Windows-Specific Notes

### PowerShell Execution Policy
If you can't run `.ps1` scripts:
```powershell
# Check current policy
Get-ExecutionPolicy

# Set to RemoteSigned (allows local scripts)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### File Paths
Windows uses backslashes `\` instead of forward slashes `/`:
```python
# In .env file, use forward slashes or double backslashes
DATA_DIR=./data          # Works
DATA_DIR=C:/data         # Works
DATA_DIR=C:\\data        # Works
DATA_DIR=C:\data         # May cause issues
```

### Long File Paths
If you get errors about file paths being too long:
```powershell
# Enable long paths (requires admin)
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

Or move project closer to root:
```powershell
cd C:\translation
```

### Environment Variables
Set temporary environment variables:
```powershell
# PowerShell
$env:END_CHAPTER=1348
python main.py crawl

# CMD
set END_CHAPTER=1348
python main.py crawl
```

---

## Troubleshooting

### Error: "pip is not recognized"
```powershell
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Error: "python is not recognized"
Python not in PATH. Fix:
1. Find Python installation: `C:\Users\YourName\AppData\Local\Programs\Python\Python313`
2. Add to PATH:
   - Windows Search → "Environment Variables"
   - Edit "Path" variable
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python313`
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python313\Scripts`

### Error: "Access Denied"
Run PowerShell/CMD as Administrator, or install packages for current user:
```powershell
pip install --user -r requirements.txt
```

### Error: "SSL Certificate Verification Failed"
```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Module installed but still "No module named X"
```powershell
# Check which Python is running
python -c "import sys; print(sys.executable)"

# Check where modules are installed
pip show loguru

# If they don't match, use virtual environment (Solution 1)
```

---

## Quick Verification Script

Create `test_setup.py`:
```python
import sys
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
print()

modules = [
    'loguru', 'requests', 'bs4', 'openai', 
    'anthropic', 'jieba', 'pydantic', 'tqdm'
]

print("Checking modules:")
for module in modules:
    try:
        __import__(module)
        print(f"✓ {module}")
    except ImportError:
        print(f"✗ {module} - NOT INSTALLED")
```

Run it:
```powershell
python test_setup.py
```

---

## Recommended: Use Virtual Environment

**Always use virtual environment to avoid conflicts:**

1. Create once:
   ```powershell
   python -m venv .venv
   ```

2. Activate every time you work on the project:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install packages:
   ```powershell
   pip install -r requirements.txt
   ```

4. When done:
   ```powershell
   deactivate
   ```

---

## Summary for Your Issue

Since you already ran `pip install -r requirements.txt` but get "No module named loguru":

**Quick Fix:**
```powershell
# Navigate to project
cd path\to\translation

# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Now run
python main.py status
```

This will create an isolated Python environment and ensure all packages are installed correctly.
