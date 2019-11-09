import logging

from jobs import games

logging.basicConfig(level=logging.INFO, format='{%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

def main():

   games.run()

if __name__ == '__main__':
    main()