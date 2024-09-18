import os
import logging

def init_logging(level):
    """Generate a log file.
    """
    if os.path.exists("HEMCO_CMAQ.log"):
        os.remove("HEMCO_CMAQ.log")
    
    logging.basicConfig(
        level=level,
        # format="%(asctime)s | %(levelname)s > %(message)s",
        # datefmt="%Y-%m-%d %H:%M:%S",
        # filename="HEMCO_CMAQ.log",
    )
    
    # logging.debug("DEBUG")
    # logging.info("INFO")
    # logging.warning("WARNING")
    # logging.error("ERROR")
    # logging.critical("CRITICAL")