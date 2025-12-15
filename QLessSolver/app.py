# from flask import Flask
# import pyodbc

# # Create an instance of the Flask class that is the WSGI application.
# # The first argument is the name of the application module or package,
# # typically __name__ when using a single module.
# app = Flask(__name__)

# # Flask route decorators map / and /hello to the hello function.
# # To add other resources, create functions that generate the page contents
# # and add decorators to define the appropriate resource locators for them.

# @app.route('/hello')
# def hello():
#    # Render the page
#    return "Hello Python!"

# @app.route('/')
# @app.route('/QLessSolver')
# def QLessSolver():

#     conn = pyodbc.connect(
#         "Driver={ODBC Driver 18 for SQL Server};"
#         "Server=localhost;"   # <- replace with your SSMS server name
#         "Database=English Words;"
#         "Trusted_Connection=yes;"
#         "Encrypt=no;"
#     )

#     cursor = conn.cursor()
#     cursor.execute("SELECT TOP 10 * FROM [tblCSW24 - 280k]")
#     rows = cursor.fetchall()
    
#     # Start HTML with Calibri font
#     html = """
#     <html>
#     <head>
#     <style>
#         body { font-family: Calibri, sans-serif; }
#         table { border-collapse: collapse; width: 100%; }
#         th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
#         th { background-color: #f2f2f2; }
#     </style>
#     </head>
#     <body>
#     <h2>Top 10 Words</h2>
#     <table>
#         <tr>
#             <th>Word</th>
#             <th>Definition</th>
#             <th>Part of Speech</th>
#             <th>Other Columns</th>
#         </tr>
#     """

#     # Populate table rows
#     for row in rows:
#         word = str(row[0])
#         definition = str(row[1]) if row[1] else ""
#         pos = str(row[2]) if row[2] else ""
#         other = " | ".join(str(col) for col in row[3:])  # any extra columns
#         html += f"<tr><td>{word}</td><td>{definition}</td><td>{pos}</td><td>{other}</td></tr>"

#     html += "</table>"

#     # Add Dice section
#     dice = [
#         "iinnoy", "dgglrr", "bllmmy", "fgkppv", "aeiouu", 
#         "bknsxz", "dfllrw", "hhpttw", "hhnnrr", "ccmstt", 
#         "bccdjt", "aaeeoo"
#     ]
#     html += "<h2>Dice</h2><table><tr>" + "".join(f"<td>{d}</td>" for d in dice) + "</tr></table>"
#     html += "<h2>Roll Dice Result</h2>" + " ".join(RollDice())

#     html += "</body></html>"

#     return html

# def RollDice():
#     import random
#     dice = [
#         "iinnoy", "dgglrr", "bllmmy", "fgkppv", "aeiouu", 
#         "bknsxz", "dfllrw", "hhpttw", "hhnnrr", "ccmstt", 
#         "bccdjt", "aaeeoo"
#     ]
#     result = [random.choice(die) for die in dice]
#     return result

# if __name__ == '__main__':
#    # Run the app server on localhost:4449
#    app.run('localhost', 4449)

#############################################
from flask import Flask, request
import pyodbc
from collections import Counter

app = Flask(__name__)

def load_words():
    conn = pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost;"
        "Database=English Words;"
        "Trusted_Connection=yes;"
        "Encrypt=no;"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT Word FROM [tblCSW24 - 280k]")
    return [row[0].upper() for row in cursor.fetchall()]

WORDS = load_words()

def word_mask(word):
    mask = 0
    for ch in set(word):
        mask |= 1 << (ord(ch) - 65)
    return mask

WORD_MASKS = [(w, word_mask(w)) for w in WORDS]

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

def RollDice():
    import random
    dice = [
        "iinnoy", "dgglrr", "bllmmy", "fgkppv", "aeiouu", 
        "bknsxz", "dfllrw", "hhpttw", "hhnnrr", "ccmstt", 
        "bccdjt", "aaeeoo"
    ]
    result = "".join([random.choice(die) for die in dice])
    return result

@app.route('/')
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
    <h2>Scrabble Words for Rack: """ + rack + """</h2>
    <table>
        <tr><th>Word</th><th>Legnth</th></tr>
    """

    for w in sorted(results, key=lambda x: (-len(x), x)):
        html += f"<tr><td>{w}</td><td>{len(w)}</td></tr>"

    html += "</table></body></html>"
    return html

#####################################
@app.route('/12letterwords')
def QLessSolver():

    dice = [
        "iinnoy", 
        "dfllrw", 
        "dgglrr", 
        "bllmmy", 
        "fgkppv", 
        "aeiouu",
        "bknsxz", 
        "hhpttw", 
        "hhnnrr", 
        "ccmstt",
        "bccdjt", 
        "aaeeoo"
    ]

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

    # Connect to SQL Server
    conn = pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=localhost;"
        "Database=English Words;"
        "Trusted_Connection=yes;"
        "Encrypt=no;"
    )
    cursor = conn.cursor()

    # Load only 12-letter words
    cursor.execute("SELECT Word FROM [tblCSW24 - 280k] WHERE LEN(Word) = 12")
    candidates = [row[0] for row in cursor.fetchall()]

    # Filter words possible with dice
    possible = [w for w in candidates if can_form_word_any_order(w, dice)]

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
        <h2>12-Letter Words Possible From Dice</h2>"""

    html += f"<p>Total Words Found: {len(possible)}</p>"

    html += """
        <table>
            <tr>
                <th>Word</th>
                <th>Length</th>
            </tr>
    """

    for w in sorted(possible):
        html += f"<tr><td>{w}</td><td>{len(w)}</td></tr>"

    html += "</table></body></html>"
    # -----------------------------------

    return html

if __name__ == '__main__':
    app.run('localhost', 4449)
