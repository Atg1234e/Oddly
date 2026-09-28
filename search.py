from flask import Flask, request, jsonify, render_template_string
import sqlite3
from urllib.parse import quote
from difflib import SequenceMatcher

app = Flask(__name__)

DB = "recommendation.db"


# =========================
# DATABASE
# =========================

def init_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# =========================
# DEMO ITEM DATABASE
# =========================

items = [
    {
        "name": "Black Running Shoes",
        "category": "shoes",
        "keywords": "black running sports shoes sneakers",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"
    },
    {
        "name": "White Sneakers",
        "category": "shoes",
        "keywords": "white sneakers casual shoes",
        "image": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=500"
    },
    {
        "name": "Classic Watch",
        "category": "watch",
        "keywords": "black watch classic wrist watch men",
        "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=500"
    },
    {
        "name": "Smart Watch",
        "category": "watch",
        "keywords": "smartwatch fitness watch digital watch",
        "image": "https://images.unsplash.com/photo-1544117519-31a4b719223d?w=500"
    },
    {
        "name": "Gaming Laptop",
        "category": "laptop",
        "keywords": "gaming laptop computer powerful laptop",
        "image": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=500"
    },
    {
        "name": "MacBook Style Laptop",
        "category": "laptop",
        "keywords": "laptop programming coding computer macbook",
        "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500"
    },
    {
        "name": "Python Programming Book",
        "category": "book",
        "keywords": "python programming coding book software development",
        "image": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=500"
    },
    {
        "name": "Machine Learning Book",
        "category": "book",
        "keywords": "machine learning artificial intelligence ai programming book",
        "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500"
    },
    {
        "name": "Cybersecurity Book",
        "category": "book",
        "keywords": "cybersecurity hacking network security programming book",
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500"
    },
    {
        "name": "Black Hoodie",
        "category": "clothing",
        "keywords": "black hoodie sweatshirt winter clothes",
        "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500"
    },
    {
        "name": "Denim Jacket",
        "category": "clothing",
        "keywords": "denim jacket blue jacket fashion clothes",
        "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500"
    },
    {
        "name": "Wireless Headphones",
        "category": "electronics",
        "keywords": "wireless headphones bluetooth audio music",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
    }
]


# =========================
# RECOMMENDATION ENGINE
# =========================

def similarity(a, b):
    return SequenceMatcher(
        None,
        a.lower(),
        b.lower()
    ).ratio()


def get_recommendations(query):

    query = query.lower().strip()

    results = []

    for item in items:

        text = (
            item["name"] + " " +
            item["category"] + " " +
            item["keywords"]
        ).lower()

        score = similarity(query, text)

        # Word matching
        query_words = query.split()

        for word in query_words:
            if word in text:
                score += 0.20

        results.append({
            **item,
            "score": score
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:8]


# =========================
# HTML
# =========================

HTML = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>SmartRecommend</title>

<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {

    font-family: Arial, sans-serif;

    background:
    linear-gradient(
        135deg,
        #f5f7ff,
        #eef1ff
    );

    min-height: 100vh;

    color: #222;
}


/* HEADER */

header {

    background: white;

    padding: 22px 7%;

    display: flex;

    justify-content: space-between;

    align-items: center;

    box-shadow:
    0 2px 15px rgba(0,0,0,0.08);
}

.logo {

    font-size: 25px;

    font-weight: bold;

    color: #5b4bdb;
}

.logo span {
    color: #222;
}


/* HERO */

.hero {

    text-align: center;

    padding: 65px 20px 35px;
}

.hero h1 {

    font-size: 42px;

    margin-bottom: 15px;
}

.hero p {

    color: #666;

    font-size: 17px;

    margin-bottom: 30px;
}


/* SEARCH */

.search-box {

    max-width: 700px;

    margin: auto;

    display: flex;

    background: white;

    padding: 7px;

    border-radius: 50px;

    box-shadow:
    0 8px 30px rgba(0,0,0,0.10);
}

.search-box input {

    flex: 1;

    border: none;

    outline: none;

    padding: 15px 20px;

    font-size: 16px;

    border-radius: 50px;
}

.search-box button {

    border: none;

    background: #5b4bdb;

    color: white;

    padding: 0 30px;

    border-radius: 40px;

    font-size: 16px;

    cursor: pointer;
}

.search-box button:hover {

    background: #4637c2;
}


/* GOOGLE BUTTON */

.google-search {

    margin-top: 15px;

    display: inline-block;

    color: #555;

    text-decoration: none;

    font-size: 14px;
}

.google-search:hover {
    text-decoration: underline;
}


/* SECTION */

.section {

    max-width: 1200px;

    margin: 40px auto;

    padding: 0 20px;
}

.section-title {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 20px;
}

.section-title h2 {
    font-size: 25px;
}


/* CARDS */

.grid {

    display: grid;

    grid-template-columns:
    repeat(auto-fit, minmax(230px, 1fr));

    gap: 22px;
}

.card {

    background: white;

    border-radius: 18px;

    overflow: hidden;

    box-shadow:
    0 5px 20px rgba(0,0,0,0.08);

    transition: 0.25s;
}

.card:hover {

    transform:
    translateY(-6px);

    box-shadow:
    0 12px 30px rgba(0,0,0,0.14);
}

.card img {

    width: 100%;

    height: 210px;

    object-fit: cover;
}

.card-content {

    padding: 16px;
}

.card h3 {

    font-size: 18px;

    margin-bottom: 8px;
}

.category {

    color: #777;

    font-size: 13px;

    margin-bottom: 15px;
}

.card-buttons {

    display: flex;

    gap: 8px;
}

.view-btn {

    flex: 1;

    padding: 10px;

    border: none;

    border-radius: 8px;

    background: #5b4bdb;

    color: white;

    cursor: pointer;
}

.google-btn {

    padding: 10px;

    border: 1px solid #ddd;

    border-radius: 8px;

    background: white;

    cursor: pointer;
}


/* HISTORY */

.history {

    display: flex;

    flex-wrap: wrap;

    gap: 10px;
}

.history span {

    background: white;

    padding: 9px 15px;

    border-radius: 30px;

    box-shadow:
    0 2px 8px rgba(0,0,0,0.07);

    cursor: pointer;

    font-size: 14px;
}


/* EMPTY */

.empty {

    text-align: center;

    padding: 50px;

    color: #777;
}


/* FOOTER */

footer {

    text-align: center;

    padding: 35px;

    color: #777;

    margin-top: 50px;
}


@media(max-width:600px) {

    .hero h1 {
        font-size: 30px;
    }

    .search-box {
        flex-direction: column;
        border-radius: 15px;
    }

    .search-box button {
        padding: 14px;
    }

}

</style>

</head>


<body>


<header>

    <div class="logo">
        Smart<span>Recommend</span>
    </div>

</header>


<section class="hero">

    <h1>
        Discover What You Like
    </h1>

    <p>
        Search anything and get personalized recommendations.
    </p>


    <div class="search-box">

        <input
            id="searchInput"
            type="text"
            placeholder="Search something..."
            onkeydown="handleEnter(event)"
        >

        <button onclick="search()">
            Search
        </button>

    </div>


    <a
        id="googleLink"
        class="google-search"
        href="https://www.google.com/search?tbm=isch"
        target="_blank"
    >
        🔎 View image results on Google
    </a>

</section>



<section class="section">

    <div class="section-title">

        <h2 id="resultTitle">
            Recommended For You
        </h2>

    </div>


    <div
        id="results"
        class="grid"
    ></div>

</section>



<section class="section">

    <div class="section-title">

        <h2>
            Your Search History
        </h2>

    </div>


    <div
        id="history"
        class="history"
    ></div>

</section>



<footer>

    SmartRecommend © 2026

</footer>



<script>


// ===========================
// SEARCH
// ===========================

function search() {

    const input =
        document.getElementById(
            "searchInput"
        );

    const query =
        input.value.trim();


    if (!query) {

        alert(
            "Please enter something to search."
        );

        return;
    }


    fetch(
        "/search?q=" +
        encodeURIComponent(query)
    )

    .then(response =>
        response.json()
    )

    .then(data => {

        displayResults(
            data.results,
            query
        );

        updateGoogleLink(
            query
        );

        loadHistory();

    })

    .catch(error => {

        console.error(error);

        alert(
            "Something went wrong."
        );

    });

}



// ===========================
// ENTER KEY
// ===========================

function handleEnter(event) {

    if (event.key === "Enter") {

        search();

    }

}



// ===========================
// GOOGLE IMAGE LINK
// ===========================

function updateGoogleLink(query) {

    const link =
        document.getElementById(
            "googleLink"
        );

    link.href =
        "https://www.google.com/search?tbm=isch&q="
        +
        encodeURIComponent(query);

}



// ===========================
// DISPLAY RESULTS
// ===========================

function displayResults(
    results,
    query
) {

    const container =
        document.getElementById(
            "results"
        );

    const title =
        document.getElementById(
            "resultTitle"
        );


    title.innerText =
        "Recommended for: " +
        query;


    container.innerHTML = "";


    if (results.length === 0) {

        container.innerHTML =
            '<div class="empty">' +
            'No recommendations found.' +
            '</div>';

        return;
    }


    results.forEach(item => {

        const googleURL =
            "https://www.google.com/search?tbm=isch&q="
            +
            encodeURIComponent(
                item.name
            );


        const card =
            document.createElement(
                "div"
            );

        card.className = "card";


        card.innerHTML = `

            <img
                src="${item.image}"
                alt="${item.name}"
            >

            <div class="card-content">

                <h3>
                    ${item.name}
                </h3>

                <div class="category">
                    ${item.category}
                </div>

                <div class="card-buttons">

                    <button
                        class="view-btn"
                        onclick="viewItem('${item.name}')"
                    >
                        View
                    </button>

                    <button
                        class="google-btn"
                        onclick="openGoogle('${item.name}')"
                    >
                        🔎
                    </button>

                </div>

            </div>
        `;


        container.appendChild(
            card
        );

    });

}



// ===========================
// VIEW ITEM
// ===========================

function viewItem(name) {

    fetch(
        "/click",
        {

            method: "POST",

            headers: {
                "Content-Type":
                "application/json"
            },

            body: JSON.stringify({
                item: name
            })

        }
    );

    openGoogle(name);

}



// ===========================
// GOOGLE SEARCH
// ===========================

function openGoogle(query) {

    const url =
        "https://www.google.com/search?tbm=isch&q="
        +
        encodeURIComponent(query);

    window.open(
        url,
        "_blank"
    );

}



// ===========================
// HISTORY
// ===========================

function loadHistory() {

    fetch("/history")

    .then(response =>
        response.json()
    )

    .then(data => {

        const container =
            document.getElementById(
                "history"
            );


        container.innerHTML = "";


        if (
            data.history.length === 0
        ) {

            container.innerHTML =
                "<span>No searches yet</span>";

            return;
        }


        data.history.forEach(
            query => {

                const span =
                    document.createElement(
                        "span"
                    );

                span.innerText =
                    query;


                span.onclick =
                    function() {

                        document
                        .getElementById(
                            "searchInput"
                        )
                        .value = query;

                        search();

                    };


                container.appendChild(
                    span
                );

            }
        );

    });

}



// ===========================
// INITIAL LOAD
// ===========================

window.onload = function() {

    loadHistory();

    fetch("/recommendations")

    .then(response =>
        response.json()
    )

    .then(data => {

        displayResults(
            data.results,
            "You may like"
        );

    });

};


</script>


</body>

</html>
"""


# =========================
# ROUTES
# =========================

@app.route("/")
def home():

    return render_template_string(
        HTML
    )


@app.route("/search")
def search():

    query = request.args.get(
        "q",
        ""
    ).strip()


    if not query:

        return jsonify({
            "results": []
        })


    # Save search

    conn = sqlite3.connect(DB)

    conn.execute(
        "INSERT INTO searches(query) VALUES (?)",
        (query,)
    )

    conn.commit()

    conn.close()


    results = get_recommendations(
        query
    )


    return jsonify({
        "results": results
    })


@app.route("/click", methods=["POST"])
def click():

    data = request.get_json()

    item = data.get(
        "item",
        ""
    )


    conn = sqlite3.connect(DB)

    conn.execute(
        "INSERT INTO clicks(item) VALUES (?)",
        (item,)
    )

    conn.commit()

    conn.close()


    return jsonify({
        "success": True
    })


@app.route("/history")
def history():

    conn = sqlite3.connect(DB)

    rows = conn.execute("""
        SELECT query
        FROM searches
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    conn.close()


    history = [
        row[0]
        for row in rows
    ]


    return jsonify({
        "history": history
    })


@app.route("/recommendations")
def recommendations():

    conn = sqlite3.connect(DB)

    row = conn.execute("""
        SELECT query
        FROM searches
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    conn.close()


    if row:

        results = get_recommendations(
            row[0]
        )

    else:

        results = items[:8]


    return jsonify({
        "results": results
    })


# =========================
# RUN
# =========================

if __name__ == "__main__":

    init_db()

    print(
        "\nSmartRecommend running at:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    app.run(
        debug=True
    )
