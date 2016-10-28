import os
import sys
import re

PROJECT_ROOT = sys.argv[1]
LINK_REGEX = re.compile(r"\[(.*?)\]\((.*?)\)")
ALL_PAGES = []


# HELPERS


###############################################################################
# TAKEN FROM www.hetland.org/coding/python/levenshtein.py
###############################################################################

# This is a straightforward implementation of a well-known algorithm, and thus
# probably shouldn't be covered by copyright to begin with. But in case it is,
# the author (Magnus Lie Hetland) has, to the extent possible under law,
# dedicated all copyright and related and neighboring rights to this software
# to the public domain worldwide, by distributing it under the CC0 license,
# version 1.0. This software is distributed without any warranty. For more
# information, see <http://creativecommons.org/publicdomain/zero/1.0>
def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    a = a.lower()
    b = b.lower()
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]

###############################################################################
# END OF TAKEN FROM www.hetland.org/coding/python/levenshtein.py
###############################################################################




def rel(path):
    """ If the string path starts with the string root, removes this part.
        Used for removing the commont root of file paths.
    """
    if path[:len(PROJECT_ROOT)] == PROJECT_ROOT:
        return path[len(PROJECT_ROOT):]



def first_double_substring(pages, name, link):
    
    guesses0 = []
    pages_there = []
    for p in pages:
        if name.lower() in p.lower() and link.lower() in p.lower():
            guesses0.append((min(levenshtein(p,name), levenshtein(p,link), levenshtein(p,name + link)), rel(p)))
            pages_there += p

    guesses1 = [] 
    for p in pages:
        if name.lower() in p.lower() and not (p in pages_there):
            guesses1.append((min(levenshtein(p,name), levenshtein(p,link), levenshtein(p,name + link)), rel(p)))
   
    guesses0 = sorted(guesses0, key = lambda x:x[0])
    guesses1 = sorted(guesses1, key = lambda x:x[0])
    return guesses0 + guesses1

def fills(pages, text, match):
    """ Given a link match, corresponding to the content of text, try to find the corresponding page and fill the link correctly.
        Returns a tuple whose first component is the replaced part of text, and second component is the remaining part.
    """
    name, link = match.groups()
    
    if link in map(rel, pages):    
        best_guess = link
    else:
        guesses = first_double_substring(pages, name, link)
        if guesses:
            print("In the link  [{}]({}) , choose the following ".format(name, link))
            list(map(lambda x: print(x[0], " : " , x[1]), enumerate(guesses)))
            choice = input("By entering the index, or nothing to take the 0-th, or 'n' to keep as is : ")
            if choice == "n":
                best_guess = link
            elif choice == "":
                best_guess = guesses[0][1]
            else:
                best_guess = guesses[int(choice)][1]
            print("Choosen: ", best_guess)
        else:
            best_guess = link
    return (text[:match.start(2)] + best_guess, text[match.end(2):])
        

# Fills ALL_PAGES
for (dirpath, dirnames, filenames) in os.walk(PROJECT_ROOT):
    ALL_PAGES.extend(map(lambda f: dirpath + "/" + f, filenames))

ALL_PAGES = list(filter(lambda p: all(x not in p for x in [".git", "README.md", "meta", "LICENSE.md", "map.svg"]), ALL_PAGES))


for page in ALL_PAGES:
    with open(page, 'r') as f:
        before = ""
        after = f.read()       

        m = LINK_REGEX.search(after)
        while m:
            b, a = fills(ALL_PAGES, after, m)
            before = before + b
            after = a
            m = LINK_REGEX.search(after)
    
        f.close()
        with open(page, 'w') as f:
            f.write(before + after)

