import logging
import sys

# Log dosyası
log_filename = "llm_agent_service.log"

# Log yapılandırması
logging.basicConfig(
    level=logging.INFO,  # Genel log seviyesi
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),  # Logları dosyaya yaz
        logging.StreamHandler(sys.stdout)  # Logları terminale yaz
    ]
)
