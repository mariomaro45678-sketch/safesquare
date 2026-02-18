import sys
print(f"Python version: {sys.version}")
print(f"Executable: {sys.executable}")

try:
    from playwright.async_api import async_playwright
    print("SUCCESS: playwright.async_api imported")
except ImportError as e:
    print(f"FAILURE: playwright.async_api failed: {e}")
except Exception as e:
    print(f"FAILURE: playwright.async_api other error: {e}")

try:
    from playwright_stealth import stealth_async
    print("SUCCESS: playwright_stealth imported")
except ImportError as e:
    print(f"FAILURE: playwright_stealth failed: {e}")
except Exception as e:
    print(f"FAILURE: playwright_stealth other error: {e}")
