import re 
import requests


#Where the magic happens! 
WIKI_URL = "https://cookieclicker.wiki.gg/wiki/"

SQ_PATTERN = r'\[\[(.*?)\]\]'
CB_PATTERN = r'{([^{}]+)\}\}'
p = re.compile(r'<.*?>')
# Example "[[Hello]]"
# Example "{{Grandma}}"


def check_for_tags(msg):
    # There is a better way of doing this.
    square_re = re.search(SQ_PATTERN, msg)
    if square_re: 
        return square_re.string
    curvy_re = re.search(CB_PATTERN, msg)
    if curvy_re: 
        return curvy_re.string
    return False 

def strip_tags(msg):
    for ch in ['[',']','{','}']:
        if ch in msg:
            msg = msg.replace(ch,'')
    return msg
    
def strip_html(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def link_to_url(msg: str) -> str:
    """makes a Link to a URL"""
    m = [w.title() for w in msg.split(" ")]
    link = "_".join(m)
    return f"{WIKI_URL}{link}"
    
def link_to_search(msg: str) -> str:
    search_term = "+".join(msg.split(" "))
    return f"https://cookieclicker.wiki.gg/index.php?search={search_term}"

def check_site_validity(link):
    request = requests.get(link)
    
    print(request.history) # This can show a 302 Redirect
    
    if request.status_code != requests.codes.ok: # check for 200
        print(f'Error with {link}: {request.status_code}')
    if request.status_code == 502: # Cloudflare is down
        return 'Cloudflare'
        
    if ("There is currently no text in this page." in request.text):
        return 0
    else:
        return 1

def find_search_exists(soup):
    # a['href] = link to page, a['title] = Title of page
    # Thanks wiki.gg! 
    search_exists = soup.find('p',attrs={'class':'mw-search-exists'})
    if search_exists:
        return search_exists.find('a') 
    
def find_did_you_mean(soup):
    did_you_mean = soup.find('a',attrs={'id':'mw-search-DYM-rewritten'}) # IF error, or no page, there's None
    if did_you_mean:
        return did_you_mean.find('em').text

def get_search_results(soup):
    results = []
    search_results = soup.find("body").find("ul", attrs={'class':'mw-search-results'}) 
    n = 0 ## Means it only returns the first 5. 
    for result in search_results:
        if n == 5:
            return results 
        else: 
            n += 1

        link = result.find('a', href=True)
        href = link['href']
        result_dict = {'name': strip_html(str(link['title'])),
                       'description':'',
                       'url':f'{WIKI_URL}{href}'}


        search_text = result.find('div',attrs={'class':'searchresult'}) # Matching Text
        search_text = strip_html(str(search_text))
        
        #cursed slicing
        result_dict['description'] = search_text[:97] + '...'

        # Not necessary, but may come in useful some day :> 
        result_dict['data'] = strip_html(str(result.find('div',attrs={'class':'mw-search-result-data'}))) #Data about the page
        results.append(result_dict)
        
