import sqlite3
import json
import os
from app_config.settings import DB_PATH

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL") # Melhor concorrência
        cursor = conn.cursor()
        
        # Table for matches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id TEXT PRIMARY KEY,
                home_team TEXT,
                away_team TEXT,
                date TEXT,
                league TEXT,
                sport TEXT,
                home_prob REAL,
                draw_prob REAL,
                away_prob REAL,
                best_bet TEXT,
                value_detected BOOLEAN
            )
        ''')
        
        # Table for odds
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS odds (
                match_id TEXT,
                bookmaker TEXT,
                home_odds REAL,
                draw_odds REAL,
                away_odds REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches (id)
            )
        ''')
        
        # Table for bets/history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bet_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                selection TEXT,
                odds REAL,
                stake REAL,
                result TEXT, -- WIN, LOSS, PENDING
                profit REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Table for chat history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT, -- user, assistant
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table for user preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                user_id INTEGER,
                key TEXT,
                value TEXT,
                PRIMARY KEY (user_id, key)
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_chat_message(self, user_id, role, content):
        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (user_id, role, content)
            VALUES (?, ?, ?)
        ''', (user_id, role, content))
        conn.commit()
        conn.close()

    def get_chat_history(self, user_id, limit=10):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT role, content FROM chat_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        # Inverter para ordem cronológica
        history = [{"role": row['role'], "content": row['content']} for row in rows]
        return history[::-1]

    def save_match(self, match_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO matches 
            (id, home_team, away_team, date, league, sport, home_prob, draw_prob, away_prob, best_bet, value_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_data['id'], match_data['home_team'], match_data['away_team'],
            match_data['date'], match_data['league'], match_data['sport'],
            match_data.get('home_prob'), match_data.get('draw_prob'), match_data.get('away_prob'),
            match_data.get('best_bet'), match_data.get('value_detected', False)
        ))
        conn.commit()
        conn.close()

    def get_pending_bets(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bet_history WHERE result = 'PENDING'")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def save_bet(self, bet_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bet_history (match_id, selection, odds, stake, result)
            VALUES (?, ?, ?, ?, 'PENDING')
        ''', (bet_data['match_id'], bet_data['selection'], bet_data['odds'], bet_data['stake']))
        conn.commit()
        conn.close()

    def save_preference(self, user_id, key, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (user_id, key, value)
            VALUES (?, ?, ?)
        ''', (user_id, key, value))
        conn.commit()
        conn.close()

    def get_preference(self, user_id, key):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM preferences WHERE user_id = ? AND key = ?', (user_id, key))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
