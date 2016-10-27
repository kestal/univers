import os
import sys
import re

project_root = sys.argv[0]
source = sys.argv[2]
target = sys.argv[3]

LINK_REGEX = re.compile(r"\[(.*?)\]\((.*?)\)")

ALL_PAGES = []
for (dirpath, dirnames, filenames) in os.walk(project_root):
    if not ".git" in dirpath and not "meta" in dirpath:
        ALL_PAGES.extend(map(lambda f: dirpath + "/" + f, filenames))

for page in ALL_PAGES:
    text = open(page).read()
    for r in LINK_REGEX.findall(text):
        print(r) 
