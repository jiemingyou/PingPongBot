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
        users = self.supabase.table("users").select("*").execute()
        return {x["id"]: x["name"] for x in users.data}

    def get_player_stats(self):
        stats = self.supabase.table("users").select("*").execute()
        return stats.data

    def insert_player(self, name):
        data = {
            "id": uuid.uuid4().int & (1 << 32) - 1,
            "name": name,
            "wins": 0,
            "loses": 0,
            "elo": 1500,
        }
        player = self.supabase.table("users").insert(data).execute()
        return player.data

    def leaderboard(self):
        lb = (
            self.supabase.table("users")
            .select("name", "elo", "wins", "loses")
            .order("elo", desc=True)
            .execute()
        )
        return lb.data

    def insert_match(self, p1, p2, s1, s2):
        data = {
            "id": uuid.uuid4().int & (1 << 32) - 1,
            "winner": p1,
            "loser": p2,
            "winner_score": s1,
            "loser_score": s2,
        }
        match = self.supabase.table("matches").insert(data).execute()
        return match.data

    def match_history(self):
        history = (
            self.supabase.table("matches")
            .select("created_at, winner, loser, winner_score, loser_score")
            .execute()
        )
        return history.data

    def get_player_info(self, userid):
        elo = (
            self.supabase.table("users")
            .select("wins", "loses", "elo")
            .eq("id", userid)
            .execute()
        )
        return elo.data[0]

    def update_elo(self, elo, userid):
        self.supabase.table("users").update({"elo": elo}).eq("id", userid).execute()

    def update_wins(self, wins, userid):
        self.supabase.table("users").update({"wins": wins}).eq("id", userid).execute()

    def update_loses(self, loses, userid):
        self.supabase.table("users").update({"loses": loses}).eq("id", userid).execute()


if __name__ == "__main__":
    db = Database(Keys.DB_URL, Keys.DB_KEY)
    # db.insert_player("Zechen 123")
    print(db.leaderboard())
