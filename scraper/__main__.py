from scraper import scrapper
import time
import json
import os


if __name__ == "__main__":

    tags = None
    with open(os.path.join(os.getcwd(), "hashtags.json")) as json_file:
        tags = json.load(json_file)

    tags = tags['Branchen']

    print(tags)

    st = time.time()
    scrapper(tags = tags)
    print(round((time.time() - st), 2))
    
    

