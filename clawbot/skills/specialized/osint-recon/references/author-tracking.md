# reconnaissance guidance

## reconnaissance guidance

```
reconnaissance guidance → reconnaissance guidance(reconnaissance guidance/reconnaissance guidance) → reconnaissance guidance → reconnaissance guidance
```

## Step 1: reconnaissance guidance

### HTML Meta reconnaissance guidance
```python
import re

def extract_author_from_meta(html):
    """reconnaissance guidance HTML meta reconnaissance guidance"""
    authors = []
    
    # <meta name="author" content="XXX">
    m = re.findall(r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)["\']', html)
    authors.extend(m)
    
    # <meta name="copyright" content="XXX">
    m = re.findall(r'<meta\s+name=["\']copyright["\']\s+content=["\']([^"\']+)["\']', html)
    authors.extend(m)
    
    # OG reconnaissance guidance
    m = re.findall(r'<meta\s+property=["\']article:author["\']\s+content=["\']([^"\']+)["\']', html)
    authors.extend(m)
    
    return list(set(authors))
```

### reconnaissance guidance
```python
def extract_social_links(html):
    """reconnaissance guidance"""
    links = re.findall(r'href=["\'](https ://[^"\']+)["\']', html)
    
    social = {}
    for link in links:
        if 'github.com' in link:
            social['github'] = link
        elif 'bilibili.com' in link:
            social['bilibili'] = link
        elif 'weibo.com' in link or 'weibo.cn' in link:
            social['weibo'] = link
        elif 'zhihu.com' in link:
            social['zhihu'] = link
        elif 'twitter.com' in link or 'x.com' in link:
            social['twitter'] = link
        elif 'linkedin.com' in link:
            social['linkedin'] = link
        elif 'youtube.com' in link:
            social['youtube'] = link
        elif 'facebook.com' in link:
            social['facebook'] = link
    
    return social
```

## Step 2: GitHub reconnaissance guidance

### reconnaissance guidance API
```python
import requests

def get_github_profile(username):
    """reconnaissance guidance GitHub reconnaissance guidance"""
    r = requests.get(f"https://api.github.com/users/{username}")
    if r.status_code != 200:
        return None
    
    data = r.json()
    return {
        'name': data.get('name'),
        'bio': data.get('bio'),
        'email': data.get('email'),
        'blog': data.get('blog'),
        'location': data.get('location'),
        'company': data.get('company'),
        'public_repos': data.get('public_repos'),
        'followers': data.get('followers'),
        'following': data.get('following'),
        'created_at': data.get('created_at'),
        'avatar_url': data.get('avatar_url'),
    }

def get_github_repos(username):
    """reconnaissance guidance（reconnaissance guidance）"""
    r = requests.get(f"https://api.github.com/users/{username}/repos per_page=100")
    if r.status_code != 200:
        return []
    
    repos = r.json()
    languages = {}
    for repo in repos:
        lang = repo.get('language')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    
    return {
        'top_languages': sorted(languages.items(), key=lambda x: -x[1])[:5],
        'repo_count': len(repos),
        'starred_total': sum(r.get('stargazers_count', 0) for r in repos),
    }
```

### reconnaissance guidance GitHub reconnaissance guidance
```python
def get_github_commit_email(username, repo):
    """reconnaissance guidance GitHub reconnaissance guidance"""
    r = requests.get(f"https://api.github.com/repos/{username}/{repo}/commits per_page=10")
    if r.status_code != 200:
        return []
    
    emails = set()
    for commit in r.json():
        author = commit.get('commit', {}).get('author', {})
        if author.get('email'):
            emails.add(author['email'])
    
    return list(emails)
```

## Step 3: reconnaissance guidance

### reconnaissance guidance
```python
# reconnaissance guidance
PLATFORMS = {
    'GitHub': 'https://github.com/{username}',
    'Breconnaissance guidance': 'https://space.bilibili.com/search keyword={username}',
    'reconnaissance guidance': 'https://www.zhihu.com/search type=content&q={username}',
    'CSDN': 'https://blog.csdn.net/{username}',
    'reconnaissance guidance': 'https://juejin.cn/user/{username}',
    'Twitter': 'https://twitter.com/{username}',
    'LinkedIn': 'https://www.linkedin.com/in/{username}',
}

async def cross_platform_search(username, fetch_tool):
    """reconnaissance guidance"""
    results = {}
    for platform, url_template in PLATFORMS.items():
        url = url_template.format(username=username)
        try:
            resp = await fetch_tool(url=url)
            if resp.get('status') == 200:
                results[platform] = f"✅ reconnaissance guidance ({url})"
            else:
                results[platform] = f"❌ reconnaissance guidance"
        except:
            results[platform] = f"⚠️ reconnaissance guidance"
    return results
```

## Step 4: reconnaissance guidance

```markdown
## reconnaissance guidance：{reconnaissance guidance}

### reconnaissance guidance
- **reconnaissance guidance**：xxx
- **reconnaissance guidance**：xxx（reconnaissance guidance）
- **reconnaissance guidance**：xxx
- **reconnaissance guidance**：xxx
- **reconnaissance guidance/reconnaissance guidance**：xxx

### reconnaissance guidance
- **reconnaissance guidance**：Python / JavaScript / ...
- **reconnaissance guidance**：...
- **reconnaissance guidance**：N reconnaissance guidance，M reconnaissance guidance
- **reconnaissance guidance**：...

### reconnaissance guidance
- GitHub: xxx
- Breconnaissance guidance: xxx
- reconnaissance guidance: xxx
- ...

### reconnaissance guidance
- reconnaissance guidance ID：xxx
- reconnaissance guidance：xxx
- reconnaissance guidance：xxx
```
