from newspaper import Article

def get_text_from_url(url):
    article = Article(url, language="en")
    article.download()
    article.parse()
    return article.title + "\n" + article.text
