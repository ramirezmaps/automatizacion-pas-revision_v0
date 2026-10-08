"""
Módulo para la configuración centralizada de logs con marca de tiempo.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(log_dir: Optional[Path] = None, log_level: int = logging.INFO) -> Path:
    """
    Configura el sistema de logging para guardar un archivo con fecha y hora por ejecución.
    """
    if log_dir is None:
        log_dir = Path("logs")
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"audit_log_{timestamp}.log"
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpiar handlers previos si los hay
    root_logger.handlers.clear()
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Sistema de logging iniciado. Archivo de log: {log_file}")
    return log_file
