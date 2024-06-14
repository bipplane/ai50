import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    dict1 = {}
    if page in corpus:
        for i in corpus:
            dict1[i] = (1-damping_factor)/len(corpus)
            if i in corpus[page]:
                dict1[i] += damping_factor/len(corpus[page])
    else:
        for i in corpus:
            dict1[i] = 1/len(corpus)
    return dict1


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    dict1 = {}
    for i in corpus:
        dict1[i] = 0
    page = random.choice(list(corpus.keys()))
    for _ in range(n):
        chosen = transition_model(corpus, page, damping_factor)
        page = random.choices(
            list(chosen.keys()), weights=chosen.values(), k=1)[0]
        dict1[page] += 1

    for page in dict1:
        dict1[page] /= n
    return dict1


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    dict1, dict2 = {}, {}
    for i in corpus:
        dict1[i] = 1/len(corpus)
        dict2[i] = 0
    while True:
        for i in corpus:
            dict2[i] = (1-damping_factor)/len(corpus)
            for p in corpus:
                if i in corpus[p]:
                    dict2[i] += damping_factor * dict1[p] / len(corpus[p])
                if not corpus[p]:
                    dict2[i] += damping_factor * dict1[p] / len(corpus)
        if all(abs(dict2[i] - dict1[i]) <= 0.000001 for i in dict1):
            break
        dict1 = dict2
    total = sum(dict2.values())
    for i in dict2:
        dict2[i] /= total
    return dict2


if __name__ == "__main__":
    main()
