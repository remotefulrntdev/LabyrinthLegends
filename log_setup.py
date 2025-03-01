import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",handlers=[logging.FileHandler("../debug.log",encoding="utf-8"),logging.StreamHandler()],encoding="utf-8")
