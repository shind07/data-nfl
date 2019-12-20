from datetime import datetime
import logging

from . import (
    games,
    play_by_play
)

logging.basicConfig(level=logging.INFO, format='{%(filename)s:%(lineno)d} %(levelname)s - %(message)s')


def main():
    start_time = datetime.now()
    logging.info(f"Starting pipeline at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    games.run()
    play_by_play.run()

    logging.info(f"Pipeline finished in {datetime.now() - start_time}")


if __name__ == '__main__':
    main()
