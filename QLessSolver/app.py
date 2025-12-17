from flask import Flask
import os

#import pyodbc

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
        <a href="/scrabble" style="margin-right:15px;">Scrabble</a>
        <a href="/Top10Words" style="margin-right:15px;">Top 10 Words</a>
        <a href="/12letterwords" style="margin-right:15px;">12-Letter Words</a>
        <a href="/hello">Hello</a>
    </div>
    <hr>
    """

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>QLess Solver</title>
        <style>
            body {
                font-family: Calibri, sans-serif;
                background-color: #f5f7fa;
                margin: 0;
                padding: 0;
            }

            .container {
                max-width: 900px;
                margin: auto;
                padding: 40px;
            }

            h1 {
                text-align: center;
                margin-bottom: 10px;
            }

            .subtitle {
                text-align: center;
                color: #555;
                margin-bottom: 40px;
                font-size: 18px;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 25px;
            }

            .card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
            }

            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 24px rgba(0,0,0,0.15);
            }

            .card h2 {
                margin-top: 0;
            }

            .card p {
                color: #555;
            }

            .card a {
                display: inline-block;
                margin-top: 15px;
                padding: 10px 16px;
                background-color: #0066cc;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;
            }

            .card a:hover {
                background-color: #004c99;
            }

            footer {
                text-align: center;
                margin-top: 50px;
                color: #888;
                font-size: 14px;
            }
        </style>
    </head>
    <body>

        <div class="container">
            <h1>QLess Scrabble Solver</h1>
            <div class="subtitle">
                Dice-based Scrabble word exploration and analysis
            </div>

            <div class="grid">

                <div class="card">
                    <h2>Scrabble Solver</h2>
                    <p>
                        Roll the dice and instantly see all Scrabble words
                        that can be made from the rack.
                    </p>
                    <a href="/scrabble">Open Solver</a>
                </div>

                <div class="card">
                    <h2>Top 10 Words</h2>
                    <p>
                        View sample words from the dictionary,
                        including definitions and parts of speech.
                    </p>
                    <a href="/Top10Words">View Words</a>
                </div>

                <div class="card">
                    <h2>12-Letter Words</h2>
                    <p>
                        Find all 12-letter words that can be formed
                        from the dice in any order.
                    </p>
                    <a href="/12letterwords">Find 12-Letter Words</a>
                </div>

                <div class="card">
                    <h2>Hello</h2>
                    <p>
                        Simple test route to confirm Flask is running.
                    </p>
                    <a href="/hello">Say Hello</a>
                </div>

            </div>

            <footer>
                QLess Solver • Flask and SQL Server • Built for Scrabble analysis
            </footer>
        </div>

    </body>
    </html>
    """

@app.route('/hello')
def hello():
   # Render the page
   return nav_links() + f"Hello Python!"

dice = [
    "iinnoy", "dgglrr", "bllmmy", "fgkppv", "aeiouu", 
    "bknsxz", "dfllrw", "hhpttw", "hhnnrr", "ccmstt", 
    "bccdjt", "aaeeoo"
]

def RollDice():
    import random
    result = "".join([random.choice(die) for die in dice])
    return result

import csv

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

#############################################
from collections import Counter

def word_mask(word):
    mask = 0
    for ch in set(word.upper()):
        if 'A' <= ch <= 'Z':
            mask |= 1 << (ord(ch) - 65)
    return mask

WORD_MASKS = [(w["word"], word_mask(w["word"])) for w in NWL23words]

def can_build_with_counts(rack, word):
    rc = Counter(rack)
    wc = Counter(word)
    return all(wc[c] <= rc[c] for c in wc)

def scrabble_solve_bitmask(rack):
    rack = rack.upper()
    rack_mask = word_mask(rack)
    results = []

    for word, wmask in WORD_MASKS:
        if (wmask & rack_mask) == wmask:
            if can_build_with_counts(rack, word):
                results.append(word)

    return results

@app.route('/scrabble')
def scrabble_route():
    rack = RollDice()

    if not rack.isalpha():
        return "<h3>Please provide rack letters using ?rack=ABCDEFG</h3>"

    results = scrabble_solve_bitmask(rack)

    html = """
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
    """ + nav_links() + f"""
    <h2>Scrabble Words for Rack: """ + rack + """</h2>
    <table>
        <tr><th>Word</th><th>Length</th></tr>
    """

    for w in sorted(results, key=lambda x: (-len(x), x)):
        html += f"<tr><td>{w}</td><td>{len(w)}</td></tr>"

    html += "</table></body></html>"
    return html

#####################################
@app.route('/12letterwords')
def TwelveLetterWords():

    # ----------- Word Feasibility Checker -----------
    def can_form_word_any_order(word, dice):
        word = word.lower()

        # Build adjacency list: letter index -> dice indices
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

    # def can_form_word(word):
    #     word = word.lower()
    #     used = [False] * len(dice)

    #     for letter in word:
    #         found = False
    #         for i, die in enumerate(dice):
    #             if not used[i] and letter in die:
    #                 used[i] = True
    #                 found = True
    #                 break
    #         if not found:
    #             return False
    #     return True

    # Load only 12-letter words
    candidates = [w for w in NWL23words if w["length"] == 12]

    # Filter words possible with dice
    possible = [w for w in candidates if can_form_word_any_order(w["word"], dice)]

    # ----------- HTML OUTPUT -----------
    html = """
    <html>
    <head>
        <style>
            body {
                font-family: Calibri, sans-serif;
                padding: 20px;
            }
            table {
                border-collapse: collapse;
                width: 20%;
                font-size: 18px;
            }
            th, td {
                border: 1px solid #555;
                padding: 8px 12px;
                text-align: left;
            }
            th {
                background-color: #ddd;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #e6f3ff;
            }
        </style>
    </head>
    <body>
    """ + nav_links() + f"""
        <h2>12-Letter Words Possible From Dice</h2>"""

    html += f"<p>Total Words Found: {len(possible)}</p>"

    html += """
        <table>
            <tr>
                <th>Word</th>
                <th>Length</th>
            </tr>
    """

    for w in sorted(possible, key=lambda x: x["word"]):
        html += f"<tr><td>{w['word']}</td><td>{w['length']}</td></tr>"

    html += "</table></body></html>"
    # -----------------------------------

    return html

if __name__ == '__main__':
    #app.run('localhost', 4449)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
