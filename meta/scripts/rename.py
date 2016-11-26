import os
import sys
import re


if not len(sys.argv) == 4:
    print("Arguments needed:")
    print("1.  The project root.")
    print("2.  The source path.")
    print("2.  The destination path.")
    sys.exit()

PROJECT_ROOT = sys.argv[1]
SRC = sys.argv[2]
DST = sys.argv[3]
ALL_PAGES = []
REGEX =  re.compile(r"\[(.*?)\]\(" +  re.escape(SRC) + "\)")

if  PROJECT_ROOT[-1] == "/":
    print("project root must be path not ending with '/'")
    sys.exit() 

if not SRC[0] == '/':
    SRC = "/" + SRC

if not DST[0] == '/':
    DST = "/" + DST

if os.path.exists(PROJECT_ROOT + DST):
    print("Destination already exist.")
    sys.exit()

# HELPERS

def rel(path):
    """ If the string path starts with the string root, removes this part.
        Used for removing the commont root of file paths.
    """
    if path[:len(PROJECT_ROOT)] == PROJECT_ROOT:
        return path[len(PROJECT_ROOT):]



# Fills ALL_PAGES
for (dirpath, dirnames, filenames) in os.walk(PROJECT_ROOT):
    ALL_PAGES.extend(map(lambda f: dirpath + "/" + f, filenames))

ALL_PAGES = list(filter(lambda p: all(x not in p for x in [".git", "meta", "LICENSE.md", "map.svg"]), ALL_PAGES))


for page in ALL_PAGES:
    with open(page, 'r', encoding='utf-8') as f:
        content = f.read()       
        print("==================", page, "==========================")
        content = re.sub(REGEX,r"[\1](" + DST + ")",content)
        f.close()
        with open(page, 'w', encoding='utf-8') as f:
            f.write(content)


os.rename(PROJECT_ROOT + SRC, PROJECT_ROOT + DST)
    
