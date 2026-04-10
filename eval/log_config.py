import logging
import os
from datetime import datetime

# 确保logs目录存在
os.makedirs("chess_guide/logs", exist_ok=True)

# 日志配置
def setup_logger():
    logger = logging.getLogger("chess_guide")
    logger.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 文件处理器（按日期命名）
    log_file = f"chess_guide/logs/chess_guide_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    
    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 初始化日志器
logger = setup_logger()
