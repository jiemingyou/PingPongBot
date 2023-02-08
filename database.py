import uuid
from datetime import datetime, timezone
from supabase import create_client, Client
import Keys


class Database:

    def __init__(self, url, key):
        self.url: str = url
        self.key: str = key
        self.supabase: Client = create_client(url, key)

    def get_players(self):
        users = self.supabase.table('users').select("*").execute()
        return {x['id']: x['name'] for x in users.data}

    def get_player_stats(self):
        stats = self.supabase.table('users').select("*").execute()
        return stats.data

    def insert_player(self, name):
        data = {
            "id": uuid.uuid4().int & (1<<32)-1,
            "name": name,
            "wins": 0,
            "loses": 0,
            "elo": 1500
        }
        player = self.supabase.table("users").insert(data).execute()
        return player.data
    
    def insert_match(self, p1, p2, s1, s2, winner):
        data = {
            "id": uuid.uuid4().int & (1<<32)-1,
            "player1": p1,
            "player2": p2,
            "score1": s1,
            "score2": s2,
            "winner": winner
        }
        match = self.supabase.table("matches").insert(data).execute()
        return match.data
    
if __name__ == "__main__":
    db = Database(Keys.DB_URL, Keys.DB_KEY)
    #db.insert_player("Zechen 123")
    print(db.get_players())


