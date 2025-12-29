import psycopg2
from psycopg2.extras import execute_batch
from collections import Counter
import time
import os

dice = [#xujkpbfydmah
        #abdfhjkmpuxy
    "iinnoy","dgglrr","bllmmy","fgkppv","aeiouu","bknsxz",
    "dfllrw","hhpttw","hhnnrr","ccmstt","bccdjt","aaeeoo"
]

BASES = [len(d) for d in dice]
TOTAL = 1
for b in BASES:
    TOTAL *= b 

def index_to_roll(idx):
    letters = []
    for die in reversed(dice):
        idx, r = divmod(idx, len(die))
        letters.append(die[r])
    return ''.join(reversed(letters))

BATCH_SIZE = 500
CHECKPOINT_EVERY = 10000

def get_conn():
    db_url = os.environ.get("DATABASE_URL")
    print("DB_URL:", db_url)

    if not db_url:
        # LOCAL DEV ONLY
        print("USING LOCAL POSTGRES")
        return psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="English Words",
            user="postgres",
            password="6284"
        )

    # RAILWAY / PROD
    print("USING RAILWAY DB")
    return psycopg2.connect(db_url, sslmode="require")

def load_progress(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT dice_index FROM roll_progress WHERE id = 1")
        row = cur.fetchone()

        if row is None:
            cur.execute(
                "INSERT INTO roll_progress (id, dice_index) VALUES (1, 0)"
            )
            conn.commit()
            return 0

        return row[0]

def save_progress(conn, idx):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE tblrollprogress
            SET dice_index = %s, updated_at = now()
            WHERE id = 1
        """, (idx,))
    conn.commit()

def worker():
    conn = get_conn()
    start_idx = load_progress(conn)
    counter = Counter()
    processed = 0

    for idx in range(start_idx, TOTAL):
        roll = index_to_roll(idx)
        alpha = ''.join(sorted(roll))
        counter[alpha] += 1
        processed += 1

        if processed % BATCH_SIZE == 0:
            batch = [(k, v, 0) for k, v in counter.items()]
            with conn.cursor() as cur:
                execute_batch(cur, """
                    INSERT INTO tblrolls (roll, frequency, solutions)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (roll)
                    DO UPDATE SET frequency = tblrolls.frequency + EXCLUDED.frequency
                """, batch)
            conn.commit()
            counter.clear()

        if idx % CHECKPOINT_EVERY == 0:
            save_progress(conn, idx)
            print(f"Checkpoint saved @ {idx:,}")

    # final flush
    if counter:
        batch = [(k, v, 0) for k, v in counter.items()]
        with conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO tblrolls (roll, frequency, solutions)
                VALUES (%s, %s, %s)
                ON CONFLICT (roll)
                DO UPDATE SET frequency = tblrolls.frequency + EXCLUDED.frequency
            """, batch)
        conn.commit()

    save_progress(conn, TOTAL)
    conn.close()
    print("DONE")

if __name__ == "__main__":
    worker()