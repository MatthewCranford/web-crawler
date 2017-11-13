def crawl_web(seed):
    tocrawl = [seed]
    crawled = []
    index = {}
    graph = {}
    while tocrawl:
        page =  tocrawl.pop()
        if page not in crawled:
            content = get_page(page)
            add_page_to_index(index, page, content)
            outlinks = get_all_links(content)
            graph[page] = outlinks
            union(tocrawl, outlinks)
            crawled.append(page)
    return index, graph

def get_page(url):
    if url in cache:
        return cache[url]
    else:
        return None

def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

def get_all_links(page):
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links

def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

def add_page_to_index(index, url, content):
    words = content.split()
    for word in words:
        add_to_index(index, word, url)

def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None

def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10 # number of times we want to iterate

    ranks = {} # holds initial rank of each page in corpus
    npages = len(graph) # number of pages in corpus

    # give each page in our corpus the same initial rank.
    # the initial rank is the probability that someone would pick
    # this page at random as the very first page they browse
    # (NOT link to from another page).
    for page in graph:
        ranks[page] = 1.0 / npages

    for i in range(0, numloops): #update newranks based on ranks
        newranks = {} # create a dictionary to store our new rank calculations

        # for each page in our corpus...
        for page in graph:

            # calculate the probability that someone stops following links,
            # and instead starts over and randomly picks this SPECIFIC page
            newrank = (1 - d) / npages

            # loop through all the pages in our corpus...
            for node in graph:

                # and find all the pages that link to this SPECIFIC page
                if page in graph[node]:

                    # add the new rank calculated above to
                    # the probability that someone follows a link (d) multiplied by the rank of
                    # the page that links to this SPECIFIC page (rank[nodes]) divided by
                    # the number of links on the page that links to this SPECIFIC page (len(graph[nodes])
                    newrank = newrank + d * (ranks[node] / len(graph[node]))
                    newrank += d * (ranks[node] / len(graph[node]))

            # store the new rank of the SPECIFIC page
            newranks[page] = newrank

        # store the newranks we just calculated so they can be used in the next iteration
        ranks = newranks

    return ranks
