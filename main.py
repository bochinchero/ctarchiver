import utils.core as core
import json
from bs4 import BeautifulSoup

path = '../ctarchivedata/'
# Opening JSON file
f = open(path+'allPosts.json')

# returns JSON object as
# a dictionary
data = json.load(f)

post = data[0]
content = core.postParser(post,path)
