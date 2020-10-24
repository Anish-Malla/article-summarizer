from newspaper import Article

def get_text_from_url(url):
    """
    Parses the information in the given url and returns the text from it

    Parameters:
        url (string) : URL to an article

    Returns:
        string : Text from article
    """
    article = Article(url, language="en")
    article.download()
    article.parse()
    return article.title + "\n" + article.text
