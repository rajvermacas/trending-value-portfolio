import builtins
import logging
import os


def init_log(suffix):
    log_file_name = os.path.join(os.getenv("OUTPUT_DIR"), "logs", f"indicator_{suffix}.log")
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s')
    builtins.logging = logging
    
    builtins.logging.info(f"Initializing log for suffix={suffix} log_file_name={log_file_name}")