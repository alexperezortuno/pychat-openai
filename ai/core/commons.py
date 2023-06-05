import os

log_str: str = os.getenv("LOG_FORMAT", f"%(asctime)s | %(name)s | %(lineno)d | %(levelname)s | %(message)s")
log_lvl: str = os.getenv("LOG_LEVEL", "info")
