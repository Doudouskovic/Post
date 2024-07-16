import requests
import openai
import json
from datetime import datetime

# Clés API et identifiants (remplacez par vos propres valeurs)
NEWS_API_KEY = 'YOUR_NEWS_API_KEY'
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
NOTION_TOKEN = 'YOUR_NOTION_API_TOKEN'
NOTION_DATABASE_ID = 'YOUR_NOTION_DATABASE_ID'

def collect_news(api_key, query, from_date, to_date):
    url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&to={to_date}&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data['articles']

def generate_article(topic, articles):
    article_content = "\n\n".join([article['description'] for article in articles if article['description']])
    prompt = f"Rédige un article sur le sujet suivant : {topic} en utilisant les informations suivantes : {article_content}"
    
    openai.api_key = OPENAI_API_KEY
    response = openai.Completion.create(
        engine="text-davinci-004",
        prompt=prompt,
        max_tokens=1024
    )
    
    return response.choices[0].text.strip()

def create_notion_article(token, database_id, title, content):
    url = 'https://api.notion.com/v1/pages'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Titre": {"title": [{"text": {"content": title}}]},
            "Date de publication": {"date": {"start": datetime.today().strftime('%Y-%m-%d')}},
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [{"type": "text", "text": {"content": content}}]
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.status_code, response.json()

if __name__ == "__main__":
    from_date = (datetime.today().strftime('%Y-%m-%d'))
    to_date = from_date
    topic = "économie personnelle"
    articles = collect_news(NEWS_API_KEY, topic, from_date, to_date)
    generated_article = generate_article(topic, articles)
    title = f"Article quotidien sur l'économie personnelle - {from_date}"
    
    status_code, response_data = create_notion_article(NOTION_TOKEN, NOTION_DATABASE_ID, title, generated_article)
    print(status_code, response_data)
