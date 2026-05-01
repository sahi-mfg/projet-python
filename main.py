import os
import requests
from dotenv import load_dotenv

from schemas import Team, Message, Channel, Reply, session

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BASE_URL = "https://graph.microsoft.com/beta"
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}



def check_response(response):
    """Vérifie si le token est encore valide."""
    if response.status_code == 401:
        print("--- ATTENTION : Votre token a expiré ! ---")
        print("Allez sur : https://developer.microsoft.com/en-us/graph/graph-explorer")
        print("Copiez le nouveau token et mettez à jour la variable ACCESS_TOKEN.")
        return False
    return True

# Exercice 1
def member_of():
    """Retourne le display_name et l'id de toutes les équipes de l'utilisateur."""
    url = f"{BASE_URL}/me/memberof"
    response = requests.get(url, headers=HEADERS)

    if not check_response(response):
        return {}
    
    if response.status_code == 200:
        teams_data = response.json().get('value', [])
        teams = {t['displayName']: t['id'] for t in teams_data if 'groupTypes' in t}
        return teams
    else:
        print(f"Erreur : {response.status_code}")
        return {}
    

teams = member_of()
for name, id in teams.items():
    print(f'channel name: {name} - channel id: {id}')




# Exercice 2
def get_channels(team_id):
    """
    Retourne un dictionnaire {nom_du_canal: id_du_canal} 
    pour l'équipe passée en paramètre.
    """
    url = f"{BASE_URL}/teams/{team_id}/channels"
    response = requests.get(url, headers=HEADERS)

    if not check_response(response):
        return {} 
        
    
    channels = {}
    
    if response.status_code == 200:
        data = response.json().get('value', [])
        for c in data:
            channels[c['id']] = c['displayName']
    else:
        print(f"Erreur lors de la récupération des canaux : {response.status_code}")
        
    return channels

channels = get_channels("0a15ecbb-d5dc-49c8-a47f-fc5371492401")
for channel_id, channel_name in channels.items():
    print(channel_id, channel_name)


# Exercice 3
def get_messages(team_id, channel_id):
    """Retourne tous les messages et leurs réponses d'un canal."""
    url_messages = f"{BASE_URL}/teams/{team_id}/channels/{channel_id}/messages"
    res_msg = requests.get(url_messages, headers=HEADERS)
    if not check_response(res_msg) or res_msg.status_code != 200:
        return []
    
    all_data = []
    
    if res_msg.status_code == 200:
        messages = res_msg.json().get('value', [])
        
        for msg in messages:
            msg_id = msg['id']
            url_replies = f"{BASE_URL}/teams/{team_id}/channels/{channel_id}/messages/{msg_id}/replies"
            res_replies = requests.get(url_replies, headers=HEADERS)
            
            replies = res_replies.json().get('value', []) if res_replies.status_code == 200 else []
            
            all_data.append({
                "message": msg.get('body', {}).get('content', ''),
                "id": msg_id,
                "replies": [r.get('body', {}).get('content', '') for r in replies]
            })
            
    return all_data


# Exercice 4
def export_to_sql():
    """Récupère les données de l'API et les insère dans SQLite."""
    # 1. Récupérer les équipes
    teams_dict = member_of() 
    
    for name, t_id in teams_dict.items():
        new_team = Team(team_id=t_id, display_name=name)
        session.merge(new_team)
        
        # 2. Récupérer les canaux
        channels = get_channels(t_id) 
        for c_id, c_name in channels:
            new_channel = Channel(channel_id=c_id, display_name=c_name, team_id=t_id)
            session.merge(new_channel)
            
            # 3. Récupérer les messages et réponses
            messages_data = get_messages(t_id, c_id)
            for m in messages_data:
                new_msg = Message(message_id=m['id'], content=m['content'], channel_id=c_id)
                session.merge(new_msg)
                
               
                for r_id, r_content in m.get('replies_detailed', []):
                    new_reply = Reply(reply_id=r_id, content=r_content, message_id=m['id'])
                    session.merge(new_reply)
    
    session.commit()
    print("Exportation terminée avec succès dans teams_data.db")