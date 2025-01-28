# context_processors.py
import requests

def get_news(request):
    url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey=1dc725c4b44746cbba9103a3d479147f'
    response = requests.get(url)

    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get('articles', [])
    else:
        articles = []

    return {'articles': articles}
