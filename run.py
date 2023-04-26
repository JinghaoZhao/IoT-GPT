import hupper
import iotgpt
from dotenv import load_dotenv, find_dotenv

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    reloader = hupper.start_reloader('iotgpt.main')
    iotgpt.main()