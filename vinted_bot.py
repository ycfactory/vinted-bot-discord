import requests
import re
import os
from datetime import datetime

# Configuration
CONFIG = {
    "WEBHOOK_URL": os.getenv('DISCORD_WEBHOOK'),
    "VINTED_URL": "https://www.vinted.fr/catalog?search_text=ralph+lauren&order=newest_first",
    "MAX_ITEMS": 5,
    "TIMEOUT": 10
}

def fetch_items():
    """Récupère les articles depuis Vinted"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "fr-FR,fr;q=0.9"
        }
        
        response = requests.get(
            CONFIG["VINTED_URL"],
            headers=headers,
            timeout=CONFIG["TIMEOUT"]
        )
        response.raise_for_status()
        
        items = []
        pattern = r'"title":"(?P<title>.*?)".*?"price":"(?P<price>.*?)".*?"path":"(?P<path>.*?)"'
        
        for match in re.finditer(pattern, response.text):
            if len(items) >= CONFIG["MAX_ITEMS"]:
                break
                
            title = match.group('title').encode('latin1').decode('unicode-escape')
            items.append({
                "title": title,
                "price": f"{match.group('price')}€",
                "url": f"https://www.vinted.fr{match.group('path')}"
            })
            
        return items
        
    except Exception as e:
        print(f"Erreur lors du scraping: {str(e)}")
        return []

def send_to_discord(items):
    """Envoie les résultats à Discord"""
    if not items:
        print("Aucun article trouvé")
        return
    
    embeds = [{
        "title": f"{item['title']} - {item['price']}",
        "url": item['url'],
        "color": 65280,
        "footer": {"text": f"Scrapé le {datetime.now().strftime('%d/%m/%Y %H:%M')}"}
    } for item in items]
    
    try:
        response = requests.post(
            CONFIG["WEBHOOK_URL"],
            json={"embeds": embeds},
            timeout=CONFIG["TIMEOUT"]
        )
        response.raise_for_status()
        print(f"{len(items)} articles envoyés à Discord")
    except Exception as e:
        print(f"Erreur d'envoi à Discord: {str(e)}")

if __name__ == "__main__":
    items = fetch_items()
    send_to_discord(items)
