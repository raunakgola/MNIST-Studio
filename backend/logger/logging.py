# # logger/logging.py
# import logging

# # Configure comprehensive logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("mnist_api.log"),
#         logging.StreamHandler()
#     ]
# )

# logger = logging.getLogger(__name__)

import logging
import sys

# Configure logging to output to stdout/stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Output to stdout
    ]
)

logger = logging.getLogger(__name__)