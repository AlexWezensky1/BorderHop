from flask import Flask, render_template
from flask import request
from collections import Counter
import os
import csv
import time
import psycopg2
from psycopg2.extras import execute_batch
#import pyodbc
print("IMPORT START")


# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)
# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

def nav_links():
    return """
    <div style="margin-bottom: 20px;">
        <a href="/" style="margin-right:15px;">Home</a>
        <a href="/anagrams" style="margin-right:15px;">Anagrams</a>
        <a href="/Top10Words" style="margin-right:15px;">Top 10 Words</a>
        <a href="/12letterwords" style="margin-right:15px;">12-Letter Words</a>
    </div>
    <hr>
    """

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

# conn = pyodbc.connect(
#     "DRIVER={ODBC Driver 18 for SQL Server};"
#     "SERVER=localhost;"
#     "DATABASE=English Words;"
#     "Trusted_Connection=yes;"
#     "TrustServerCertificate=yes;"
# )

# cursor = conn.cursor()
# cursor.fast_executemany = True

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>QLess Solver</title>
        <style>
            body {font-family: Calibri, sans-serif;background-color: #f5f7fa;margin: 0;padding: 0;}
            .container {max-width: 1500px;margin: auto;padding: 40px;}
            h1 {text-align: center;margin-bottom: 10px;}
            .subtitle {text-align: center;color: #555;margin-bottom: 40px;font-size: 18px;}
            .grid {display: grid;grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));gap: 25px;}
            .card {background: white;border-radius: 12px;padding: 25px;box-shadow: 0 6px 18px rgba(0,0,0,0.1);transition: transform 0.2s, box-shadow 0.2s;}
            .card:hover {transform: translateY(-5px);box-shadow: 0 10px 24px rgba(0,0,0,0.15);}
            .card h2 {margin-top: 0;}
            .card p {color: #555;}
            .card a {display: inline-block;margin-top: 15px;padding: 10px 16px;background-color: #0066cc;color: white;text-decoration: none;border-radius: 6px;font-weight: bold;}
            .card a:hover {background-color: #004c99;}
            footer {text-align: center;margin-top: 50px;color: #888;font-size: 14px;}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>QLess Project</h1>
            <div class="subtitle">
                To do: 
                <li>QLess solver - show all solutions for a specific roll</li>
                <li>Cache all 2 billion possible rolls and their solutions</li>
                <li>Rank solution by frequency of words</li>
                <li>Leaderboard - most rolls solved, quickest solve, most obscure solve</li>
                <li>Dictionary selector, explanation, and word list</li>
                <li>Option to play with a different number of dice</li>
            </div>

            <div class="grid">
                <a href="/anagrams"><div class="card">
                    <h2>Anagrams</h2><p>
                        Roll the dice and see all possible words that can be made.
                    </p>
                </div></a>
                <a href="/Top10Words"><div class="card">
                    <h2>First 10 Words</h2><p>
                        View the first 10 words alphabetically of the NWL word list.
                    </p>
                </div></a>
                <a href="/12letterwords"><div class="card">
                    <h2>12 Letter Words</h2><p>
                        View all the 12 letter words that can be formed from the dice in any order.
                    </p>
                </div></a>
            </div>
            <footer>
                Proudly built with no AI. Buy me a coffee! <a href="https://www.linkedin.com/in/alex-wezensky-8425b7b8/">LinkedIn</a>
            </footer>
        </div>
    </body>
    </html>
    """
                # <a href="/hello"><div class="card">
                #     <h2>Hello</h2><p>
                #         Simple test route.
                #     </p>
                # </div></a>

@app.route('/hello')
def hello():
   # Render the page
   return nav_links() + f"Hello Python!"

dice = [
    "iinnoy", "dgglrr", "bllmmy", "fgkppv", "aeiouu", 
    "bknsxz", "dfllrw", "hhpttw", "hhnnrr", "ccmstt", 
    "bccdjt", "aaeeoo"]

def RollDice():
    import random
    result = "".join([random.choice(die) for die in dice])
    return result

def load_NWL23words():
    NWL23words = []
    with open("tblNWL23 - 196k.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        #print(reader.fieldnames)
        for row in reader:
            word = row["word"].strip().upper()
            NWL23words.append({
                "word": word,
                "definition": row.get("definition", ""),
                "partofspeech": row.get("partofspeechandalternates", ""),
                "length": int(row.get("length", len(word))),
                "fulltext": row.get("fulltext", "")
            })
    return NWL23words

NWL23words = load_NWL23words()

def load_WFWords():
    WFWords = []
    with open("tblWFWords - 5k.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        #print(reader.fieldnames)
        for row in reader:
            word = row["word"].strip().upper()
            WFWords.append({
                "word": word,
                "rank": int(row.get("rank", "")),
                "freq": int(row.get("freq", "")),
                "#texts": int(row.get("#texts", "")),
                "%caps": float(row.get("%caps", ""))
            })
    return WFWords

WordFreq = load_WFWords()
WordFreq_Lookup = {w["word"]: w for w in WordFreq}

@app.route('/Top10Words')
def Top10Words():

    # cursor.execute("SELECT TOP 10 * FROM [tblCSW24 - 280k]")
    # rows = cursor.fetchall()
    
    # Start HTML with Calibri font
    html = """
    <html>
    <head>
    <style>
        body { font-family: Calibri, sans-serif; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
    </head>
    <body>
    """ + nav_links() + f"""
    <h2>Top 10 Words</h2>
    <table>
        <tr>
            <th>Word</th>
            <th>Definition</th>
            <th>Part of Speech</th>
            <th>Length</th>
            <th>Full Text</th>
        </tr>
    """

    # Populate table rows
    for w in NWL23words[:10]:
        html += f"""
        <tr>
            <td>{w['word']}</td>
            <td>{w['definition']}</td>
            <td>{w['partofspeech']}</td>
            <td>{w['length']}</td>
            <td>{w['fulltext']}</td>
        </tr>
        """

    html += "</table>"

    html += "<h2>Dice</h2><table><tr>" + "".join(f"<td>{d}</td>" for d in dice) + "</tr></table>"
    html += "<h2>Roll Dice Result</h2>" + RollDice()

    html += "</body></html>"

    return html

def word_mask(word):
    mask = 0
    for ch in set(word.upper()):
        if 'A' <= ch <= 'Z':
            mask |= 1 << (ord(ch) - 65)
    return mask

WORD_MASKS = [(w["word"], word_mask(w["word"])) for w in NWL23words]

print("IMPORT END")

def can_build_with_counts(rack, word):
    rc = Counter(rack)
    wc = Counter(word)
    return all(wc[c] <= rc[c] for c in wc)

def anagrams_solve_bitmask(rack):
    rack = rack.upper()
    rack_mask = word_mask(rack)
    results = []

    for word, wmask in WORD_MASKS:
        if (wmask & rack_mask) == wmask:
            if can_build_with_counts(rack, word):
                results.append(word)

    return results

@app.route("/anagrams", methods=["GET", "POST"])
def anagrams_route():
    randomrack = RollDice()
    rack = ""
    results = []

    html = nav_links() + f"""
    <h1>Enter your letters</h1>
    <h3>12 random letters to test: """ + randomrack + """</h3>
    <form method="POST" action="/anagrams" style="margin-bottom: 1rem;">
        <input
            type="text"
            name="letters"
            placeholder="Enter letters"
            required
            style="padding: 6px; font-size: 14px;"
        >
        <button
            type="submit"
            style="padding: 6px 12px; font-size: 14px;"
        >
            Submit
        </button>
    </form>"""

    if request.method == "POST":
        rack = request.form["letters"]
        results = anagrams_solve_bitmask(rack)

    html += """
    <html>
    <head>
    <style>
        body { font-family: Calibri, sans-serif; }
        table { border-collapse: collapse; width: 50%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
    </head>
    <body>
    <h2>Possible words for """ + rack + """</h2>
    Total Words Found: """ + str(len(results)) + """
    <table id="anagrams">
        <tr><th onclick="sortTable(0)">Word</th><th onclick="sortTable(1)">Length</th><th onclick="sortTable(2)">Rank out of the top 5000 words</th></tr>
    """

    for w in sorted(results, key=lambda x: (-len(x), x)):
        wf = WordFreq_Lookup.get(w)
        rank = wf["rank"] if wf else ""
        html += f"""<tr>
                <td>{w}</td>
                <td>{len(w)}</td>
                <td>{rank}</td>
            </tr>"""

    html += """</table>
<script>
function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("anagrams");
  switching = true;
  dir = "asc";

  while (switching) {
    switching = false;
    rows = table.rows;
    for (i = 1; i < (rows.length - 1); i++) {
      shouldSwitch = false;
      x = rows[i].getElementsByTagName("TD")[n].innerHTML;
      y = rows[i + 1].getElementsByTagName("TD")[n].innerHTML;

      // convert to numbers if both x and y are numeric
      let xNum = parseFloat(x);
      let yNum = parseFloat(y);

      if (!isNaN(xNum) && !isNaN(yNum)) {
        if (dir == "asc" && xNum > yNum) {
          shouldSwitch = true;
          break;
        } else if (dir == "desc" && xNum < yNum) {
          shouldSwitch = true;
          break;
        }
      } else {
        // fallback to string comparison
        if (dir == "asc" && x.toLowerCase() > y.toLowerCase()) {
          shouldSwitch = true;
          break;
        } else if (dir == "desc" && x.toLowerCase() < y.toLowerCase()) {
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      switchcount++;
    } else {
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
</script>
    </body></html>"""
    return html

def twelve_cache_function():
    def can_form_word_any_order(word, dice):
        word = word.lower()

        adj = []
        for ch in word:
            possible_dice = [i for i, d in enumerate(dice) if ch in d]
            if not possible_dice:
                return False
            adj.append(possible_dice)

        match = [-1] * len(dice)

        def dfs(i, seen):
            for d in adj[i]:
                if seen[d]:
                    continue
                seen[d] = True
                if match[d] == -1 or dfs(match[d], seen):
                    match[d] = i
                    return True
            return False

        for i in range(len(word)):
            seen = [False] * len(dice)
            if not dfs(i, seen):
                return False

        return True

    candidates = [w for w in NWL23words if w["length"] == 12]
    return [w for w in candidates if can_form_word_any_order(w["word"], dice)]

TwelveLetterCache = twelve_cache_function()

@app.route('/12letterwords')
def TwelveLetterWords():
    possible = TwelveLetterCache

    html = """
    <html>
    <head>
        <style>
            body {font-family: Calibri, sans-serif;padding: 20px;}
            table {border-collapse: collapse;width: 20%;font-size: 18px;}
            th, td {border: 1px solid #555;padding: 8px 12px;text-align: left;}
            th {background-color: #ddd;}
            tr:nth-child(even) {background-color: #f2f2f2;}
            tr:hover {background-color: #e6f3ff;}
        </style>
    </head>
    <body>
    """ + nav_links() + f"""<h2>12 letter words possible from dice with the NWL dictionary</h2>"""

    html += f"<p>Total Words Found: {len(possible)}</p>"
    html += """
        <table>
            <tr>
                <th>Word</th>
                <th>Length</th>
            </tr>"""

    for w in sorted(possible, key=lambda x: x["word"]):
        html += f"<tr><td>{w['word']}</td><td>{w['length']}</td></tr>"

    html += "</table></body></html>"
    return html

@app.route('/allrolls')
def allrolls():
    sql = """
    DROP TABLE "tblRolls";"""
    conn = get_conn()
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            execute_batch(cur, sql, batch, page_size=1000)
        conn.commit()
    finally:
        conn.close()
    batch.clear()

    batch = []
    alphaword = word = ""
    first = second = third = fourth = fifth = sixth = seventh = eighth = ninth = tenth = eleventh = twelfth = ""
    dict = {}
    count = 0
    first = dice[0]
    second = dice[1]
    third = dice[2]
    fourth = dice[3]
    fifth = dice[4]
    sixth = dice[5]
    seventh = dice[6]
    eighth = dice[7]
    ninth = dice[8]
    tenth = dice[9]
    eleventh = dice[10]
    twelfth = dice[11]
    start = time.time()
    counter1 = Counter()
 
    # for k, char1 in enumerate(first):
    #     for k, char2 in enumerate(second):
    #         for k, char3 in enumerate(third):
    #             for k, char4 in enumerate(fourth):
    #                 for k, char5 in enumerate(fifth):
    #                     for k, char6 in enumerate(sixth):
    #                         for k, char7 in enumerate(seventh):
    #                             for k, char8 in enumerate(eighth):
    #                                 for k, char9 in enumerate(ninth):
    #                                     for k, char10 in enumerate(tenth):
    #                                         for k, char11 in enumerate(eleventh):
    #                                             for k, char12 in enumerate(twelfth):
    #                                                 word = char1 + char2 + char3 + char4 + char5 + char6 + char7 + char8 + char9 + char10 + char11 + char12
    #                                                 print(word)
                                                    
    #                                                 alphaword = ''.join(sorted(word))
    #                                                 #dict[alphaword] = len(alphaword)
    #                                                 print(alphaword)
                                                    
    #                                                 #batch.append((alphaword,0,0))
    #                                                 counter1[alphaword] += 1
    #                                                 print(counter1)
                                                    
    #                                                 count += 1
    #                                                 batchsize = 10

    #                                                 #if len(batch) == batchsize:
    #                                                 # if sum(counter1.values()) >= batchsize:
    #                                                 #     batch = [(roll, freq, 0) for roll, freq in counter1.items()]
    #                                                 #     cursor.executemany(sql, result)
    #                                                 #     conn.commit()
    #                                                 #     batch.clear()
    #                                                 #     counter1.clear()
    #                                                 print(len(counter1))
    #                                                 if sum(counter1.values()) >= batchsize:       
    #                                                     batch = [(roll, freq, 0) for roll, freq in counter1.items()]
    #                                                     sql = """
    #                                                     DROP TABLE "tblRolls";"""
    #                                                     conn = get_conn()
    #                                                     conn.autocommit = True
    #                                                     try:
    #                                                         with conn.cursor() as cur:
    #                                                             execute_batch(cur, sql, batch, page_size=1000)
    #                                                         conn.commit()
    #                                                     finally:
    #                                                         conn.close()
    #                                                     batch.clear()
       
    #                                                 if count == batchsize:
    #                                                     end = time.time()
    #                                                     return f"""Words checked: """+str(count)+""". Time elapsed: """+str((end-start))
    #print("Words checked: " + str(count))
    #print("Unique words: " + str(len(dict)))
    #print(dict.keys())
    return counter1

if __name__ == '__main__':
    #app.run('localhost', 4449)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
