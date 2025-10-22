import sys
import re
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except Exception as e:
    requests = None
    BeautifulSoup = None


def fetch_url(url, timeout=15):
    if requests:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=timeout)
        r.raise_for_status()
        return r.text
    else:
        # fallback to urllib
        from urllib.request import Request, urlopen
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=timeout) as r:
            return r.read().decode(errors='ignore')


def parse_robots(robots_txt):
    # Very simple robots.txt parser for User-agent: *
    lines = robots_txt.splitlines()
    user_agent = None
    disallows = []
    allows = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(':', 1)
        if len(parts) != 2:
            continue
        key, value = parts[0].strip().lower(), parts[1].strip()
        if key == 'user-agent':
            user_agent = value
        elif key == 'disallow' and (user_agent == '*' or user_agent is None):
            disallows.append(value)
        elif key == 'allow' and (user_agent == '*' or user_agent is None):
            allows.append(value)
    return disallows, allows


def is_path_allowed(path, disallows, allows):
    # Basic matching: longest allow/disallow wins doesn't implemented fully, but we check simple cases
    # If any allow matches prefix, allow. If any disallow is '/', disallow all.
    if '/' in disallows:
        return False
    for a in allows:
        if a and path.startswith(a):
            return True
    for d in disallows:
        if d and path.startswith(d):
            return False
    return True


def extract_info(html, base_url):
    soup = BeautifulSoup(html, 'html.parser') if BeautifulSoup else None
    if not soup:
        # crude regex fallback
        title_m = re.search(r'<title>(.*?)</title>', html, re.I|re.S)
        title = title_m.group(1).strip() if title_m else ''
        desc_m = re.search(r'<meta\s+name="description"\s+content="(.*?)"', html, re.I|re.S)
        desc = desc_m.group(1).strip() if desc_m else ''
        h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.I|re.S)
        imgs = re.findall(r'<img\s', html, re.I)
        links = re.findall(r'href=["\'](.*?)["\']', html, re.I)
        return {'title': title, 'description': desc, 'h1': h1s, 'num_images': len(imgs), 'links': links, 'text_snippet': re.sub('<[^<]+?>', '', html)[:300]}
    title = soup.title.string.strip() if soup.title and soup.title.string else ''
    desc = ''
    d = soup.find('meta', attrs={'name':'description'})
    if d and d.get('content'):
        desc = d.get('content').strip()
    h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
    imgs = soup.find_all('img')
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        full = urljoin(base_url, href)
        links.append(full)
    # visible text snippet
    texts = soup.get_text(separator=' ', strip=True)
    snippet = texts[:400]
    return {'title': title, 'description': desc, 'h1': h1s, 'num_images': len(imgs), 'links': links, 'text_snippet': snippet}


def crawl_site(start_url, max_pages=8):
    parsed = urlparse(start_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = urljoin(base, '/robots.txt')
    result = {'robots_url': robots_url, 'robots_ok': None, 'pages': []}
    try:
        rtxt = fetch_url(robots_url)
        disallows, allows = parse_robots(rtxt)
        result['robots_ok'] = is_path_allowed(parsed.path or '/', disallows, allows)
        result['robots_raw'] = rtxt[:2000]
    except Exception as e:
        result['robots_ok'] = True
        result['robots_error'] = str(e)
        disallows = []
        allows = []
    if not result['robots_ok']:
        return result
    # crawl BFS
    visited = set()
    to_visit = [start_url]
    while to_visit and len(result['pages']) < max_pages:
        url = to_visit.pop(0)
        u_parsed = urlparse(url)
        if u_parsed.netloc != parsed.netloc:
            continue
        if url in visited:
            continue
        visited.add(url)
        try:
            html = fetch_url(url)
            info = extract_info(html, base)
            info['url'] = url
            result['pages'].append(info)
            # enqueue internal links
            for link in info['links']:
                p = urlparse(link)
                if p.netloc == parsed.netloc and link not in visited and link not in to_visit:
                    to_visit.append(link)
        except Exception as e:
            result['pages'].append({'url': url, 'error': str(e)})
    return result


if __name__ == '__main__':
    start = 'https://www.infomedia.com.au'
    res = crawl_site(start, max_pages=6)
    import json
    print(json.dumps(res, indent=2))
