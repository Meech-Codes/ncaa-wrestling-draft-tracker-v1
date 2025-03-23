try:
    from ncaa_wrestling_tracker import config
    from ncaa_wrestling_tracker.utils.logging_utils import log_debug
    print("Imports successful!")
except ImportError as e:
    print(f"Import error: {e}")