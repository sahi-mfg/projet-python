import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
# import time
# import seaborn as sns 

def parse_date(timesince_div):
    """Convertit '2 jours' en date ISO8601"""
    if not timesince_div:
        return "N/A"
    
    number_tag = timesince_div.find("span", class_="time")
    unit_tags = timesince_div.find_all("span")
    
    number = int(number_tag.text.strip()) if number_tag else 0
    unit = unit_tags[1].text.strip() if len(unit_tags) > 1 else ""
    
    now = datetime.now()
    if "jour" in unit:
        date = now - timedelta(days=number)
    elif "heure" in unit:
        date = now - timedelta(hours=number)
    elif "minute" in unit:
        date = now - timedelta(minutes=number)
    else:
        return "N/A"
    
    return date.isoformat()

def parse_location(location_tag):
    """
    Coinafrique CI : format observé
      - "Abidjan, Côte d'Ivoire"  → quartier absent, ville = Abidjan
      - "Angré, Abidjan"          → quartier = Angré, ville = Abidjan
    On veut toujours retourner la vraie ville (commune/ville connue).
    Le code postal est mis à N/A car la CI n'a pas de codes postaux numériques.
    """
    if not location_tag:
        return "N/A", "N/A"
    
    text = location_tag.text.strip().replace("location_on", "").strip()
    parts = [p.strip() for p in text.split(",")]
    
    KNOWN_CITIES = {
        "Abidjan", "Bouaké", "Daloa", "Korhogo", "Yamoussoukro",
        "San-Pédro", "Man", "Divo", "Gagnoa", "Abengourou"
    }
    
    city = "N/A"
    for part in parts:
        if part in KNOWN_CITIES:
            city = part
            break
    
    # Si aucune ville connue trouvée, prendre la dernière partie
    # (souvent le pays "Côte d'Ivoire" → on prend l'avant-dernière)
    if city == "N/A" and len(parts) >= 2:
        city = parts[-2]  # ex: "Angré, Abidjan" → Abidjan
    
    return city, "N/A"  # Pas de code postal numérique en CI

def get_ps5_prices():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0;Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.74 Safari/537.36 Edg/79.0.309.43"
    }
    
    url = "https://ci.coinafrique.com/search?category=&keyword=ps5"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Erreur HTTP : {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    ads = []
    
    listings = soup.find_all("div", class_="ad__card")
    
    for listing in listings:
        # --- TITRE ---
        title_tag = listing.find("p", class_="ad__card-description")
        title = title_tag.text.strip() if title_tag else "N/A"
        
        # --- PRIX ---
        price_tag = listing.find("p", class_="ad__card-price")
        if price_tag:
            price_text = price_tag.text.strip()
            price_text = price_text.replace("CFA", "").replace("\xa0", "").replace(" ", "").strip()
            try:
                price = float(price_text)
            except ValueError:
                price = 0
        else:
            price = 0
        
        # --- DATE ---
        date_div = listing.find("div", class_="ad__card-timesince")
        date = parse_date(date_div)
        
        # --- LOCALISATION ---
        location_tag = listing.find("p", class_="ad__card-location")
        city, postal_code = parse_location(location_tag)
        
        if title == "N/A" and price == 0:
            continue
        
        ads.append({
            "title": title,
            "price": price,
            "date": date,
            "city": city,
            "postal_code": postal_code
        })
    
    df = pd.DataFrame(ads, columns=["title", "price", "date", "city", "postal_code"])
    print(f"{len(df)} annonces récupérées.")
    print(df.head(20))
    
    return df

df = get_ps5_prices()
print(df.shape)

# Exercice 2
# Export en pickle
# df.to_pickle("ps5-dataframe.pickle")
# boucle qui lance la fonction toutes les 5 minutes
# for _ in time.sleep(300):
#     get_ps5_prices()



# Exercice 3 (dans un notebook)

# df = pd.read_pickle("ps5-dataframe.pickle")
# df["day"] = df["date"].dt.day

# # seaborn
# sns.boxplot(data=df, x="day", y="price")