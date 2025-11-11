# Windows Quick Start

## Problem: "No module named 'loguru'" Error

You installed Python 3.13 and ran `pip install -r requirements.txt`, but when you run `python main.py`, you get:
```
ModuleNotFoundError: No module named 'loguru'
```

## Quick Fix (3 Steps)

### Step 1: Open PowerShell in Project Folder
Right-click in the `translation` folder → "Open in Terminal" or "Open PowerShell here"

### Step 2: Run Setup Script
```powershell
.\setup_windows.ps1
```

If you get an error about execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_windows.ps1
```

### Step 3: Verify Installation
```powershell
python test_setup.py
```

You should see all modules marked with ✓.

---

## Manual Setup (If Script Doesn't Work)

### 1. Create Virtual Environment
```powershell
python -m venv .venv
```

### 2. Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the beginning of your prompt.

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Test Installation
```powershell
python test_setup.py
```

### 5. Run the Project
```powershell
python main.py status
```

---

## Why This Happens

Windows often has multiple Python installations. When you run:
- `pip install` → installs to one Python
- `python main.py` → uses a different Python

**Solution:** Use a virtual environment (`.venv`) to ensure `pip` and `python` use the same installation.

---

## Every Time You Work on This Project

**You must activate the virtual environment first:**

```powershell
# In PowerShell
.\.venv\Scripts\Activate.ps1

# OR in Command Prompt
.venv\Scripts\activate.bat
```

Then you can run:
```powershell
python main.py crawl
python main.py status
```

When you're done:
```powershell
deactivate
```

---

## Full Documentation

See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed troubleshooting and explanations.

---

## Need Help?

1. **Run the diagnostic script:**
   ```powershell
   python test_setup.py
   ```

2. **Check if you're in virtual environment:**
   - Your prompt should show `(.venv)` at the beginning
   - If not, run: `.\.venv\Scripts\Activate.ps1`

3. **Verify Python and pip match:**
   ```powershell
   python -c "import sys; print(sys.executable)"
   pip --version
   ```
   They should point to the same Python installation.

4. **Reinstall in virtual environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
