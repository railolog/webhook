import xml.etree.ElementTree as ElementTree
import urllib.request

url = 'https://lenta.ru/rss'


def get_news(url='http://feeds.feedburner.com/RuWikinewsLatestNews?format=xml'):
    f = ElementTree.parse(urllib.request.urlopen(url))
    root = f.getroot()
    news_list = root[0][21]
    try:
        descr = news_list[5].text.split('</p>')[0].strip().strip('<p>').strip()
    except:
        news_list = root[0][22]
        descr = news_list[5].text.split('</p>')[0].strip().strip('<p>').strip()
    return (news_list[0].text, descr, news_list[1].text)


if __name__ == '__main__':
    print(get_news())
    input()
