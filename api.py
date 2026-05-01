# Exercice 5

from flask import Flask, jsonify
from sqlalchemy.orm import sessionmaker
from schemas import Team, Message, Channel, Reply, engine

app = Flask(__name__)
Session = sessionmaker(bind=engine)
session = Session()

# --- ROUTES ---

@app.route('/teams', methods=['GET'])
def get_all_teams():
    """Récupère toutes les équipes."""
    teams = session.query(Team).all()
    return jsonify([{"team_id": t.team_id, "display_name": t.display_name} for t in teams])

@app.route('/channels', methods=['GET'])
def get_all_channels():
    """Récupère tous les canaux."""
    channels = session.query(Channel).all()
    return jsonify([{
        "channel_id": c.channel_id, 
        "display_name": c.display_name, 
        "team_id": c.team_id
    } for c in channels])

@app.route('/messages', methods=['GET'])
@app.route('/messages/<message_id>', methods=['GET'])
def get_messages_api(message_id=None):
    """Récupère un message spécifique ou tous les messages[cite: 1]."""
    if message_id:
        msg = session.query(Message).filter_by(message_id=message_id).first()
        if not msg:
            return jsonify({"error": "Message non trouvé"}), 404
        return jsonify({"message_id": msg.message_id, "content": msg.content, "channel_id": msg.channel_id})
    
    messages = session.query(Message).all()
    return jsonify([{"message_id": m.message_id, "content": m.content} for m in messages])

@app.route('/replies', methods=['GET'])
@app.route('/replies/<reply_id>', methods=['GET'])
def get_replies_api(reply_id=None):
    """Récupère une réponse spécifique ou toutes les réponses."""
    if reply_id:
        rep = session.query(Reply).filter_by(reply_id=reply_id).first()
        if not rep:
            return jsonify({"error": "Réponse non trouvée"}), 404
        return jsonify({"reply_id": rep.reply_id, "content": rep.content, "message_id": rep.message_id})
    
    replies = session.query(Reply).all()
    return jsonify([{"reply_id": r.reply_id, "content": r.content} for r in replies])

# --- GESTION DES ERREURS ---

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Ressource non trouvée"}), 404

if __name__ == '__main__':
    app.run(debug=True)