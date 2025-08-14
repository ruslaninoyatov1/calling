import logging
from app.scheduler import check_and_make_calls

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_and_make_calls()