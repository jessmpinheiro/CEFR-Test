from flask import Flask, render_template, request, session
import time
import random
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Define the database path (temporary storage for Render)
DB_PATH = "/tmp/test_results.db"

# Predefined CEFR test questions (A1 to C2)
questions = {
    "A1": [
        {"question": "Choose the correct sentence:", 
         "options": ["He go to school.", "He goes to school.", "He going to school."], 
         "answer": "He goes to school."},
        {"question": "What is the plural of 'child'?", 
         "options": ["Childs", "Children", "Childes"], 
         "answer": "Children"},
        {"question": "Fill in the blank: 'I ____ a book.'", 
         "options": ["read", "reads", "reading"], 
         "answer": "read"}
    ],
    "A2": [
        {"question": "Which sentence is correct?", 
         "options": ["I have went to the store.", "I have gone to the store.", "I has gone to the store."], 
         "answer": "I have gone to the store."},
        {"question": "What is the past tense of 'run'?", 
         "options": ["Runned", "Ran", "Running"], 
         "answer": "Ran"},
        {"question": "Choose the correct verb: 'She ____ TV every night.'", 
         "options": ["watch", "watches", "watching"], 
         "answer": "watches"}
    ],
    "B1": [
        {"question": "Which is the correct sentence?", 
         "options": ["If I was rich, I buy a car.", "If I were rich, I would buy a car.", "If I were rich, I buy a car."], 
         "answer": "If I were rich, I would buy a car."},
        {"question": "What is the correct modal verb? 'You ___ see a doctor if you feel sick.'", 
         "options": ["should", "must", "can"], 
         "answer": "should"},
        {"question": "Choose the correct word: 'We need to ___ a decision soon.'", 
         "options": ["make", "do", "take"], 
         "answer": "make"}
    ],
    "B2": [
        {"question": "Choose the correct sentence:", 
         "options": ["She suggested that he goes to the doctor.", "She suggested that he go to the doctor.", "She suggested that he went to the doctor."], 
         "answer": "She suggested that he go to the doctor."},
        {"question": "Which is the correct phrasal verb? 'I need to ___ this issue before making a decision.'", 
         "options": ["go over", "go under", "go through"], 
         "answer": "go over"},
        {"question": "Choose the correct conjunction: 'He was tired, ___ he kept working.'", 
         "options": ["but", "so", "because"], 
         "answer": "but"}
    ],
    "C1": [
        {"question": "Choose the correct form: 'Had he known about the meeting, he ___ attended.'", 
         "options": ["will have", "would have", "had"], 
         "answer": "would have"},
        {"question": "What does 'ubiquitous' mean?", 
         "options": ["Rare", "Everywhere", "Unimportant"], 
         "answer": "Everywhere"},
        {"question": "Choose the correct sentence:", 
         "options": ["Despite of the rain, we continued.", "Despite the rain, we continued.", "Although of the rain, we continued."], 
         "answer": "Despite the rain, we continued."}
    ],
    "C2": [
        {"question": "Which sentence is the most grammatically complex?", 
         "options": ["Despite the rain, we continued our journey as planned.", 
                     "We kept going even though it was raining.", 
                     "We decided to continue, the rain notwithstanding."], 
         "answer": "We decided to continue, the rain notwithstanding."},
        {"question": "Which word fits best? 'His arguments were ___ and well-structured, leaving no room for doubt.'", 
         "options": ["coherent", "haphazard", "superficial"], 
         "answer": "coherent"},
        {"question": "What does 'ephemeral' mean?", 
         "options": ["Short-lived", "Eternal", "Irrelevant"], 
         "answer": "Short-lived"}
    ]
}

def init_db():
    """Creates the database table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER,
            level TEXT,
            duration REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def chat():
    if "start_time" not in session or "test_questions" not in session:
        session["start_time"] = time.time()
        session["score"] = 0
        session["question_index"] = 0

        # Select 10 random questions from different levels
        all_questions = []
        for level in questions.values():
            all_questions.extend(level)

        session["test_questions"] = random.sample(all_questions, 10)

    if request.method == "POST":
        user_answer = request.form.get("answer")
        question_index = session["question_index"]

        if user_answer == session["test_questions"][question_index]["answer"]:
            session["score"] += 1

        session["question_index"] += 1

        if session["question_index"] >= len(session["test_questions"]):
            return determine_level()

        return render_template("index.html", question=session["test_questions"][session["question_index"]])

    return render_template("index.html", question=session["test_questions"][0])

def determine_level():
    """Determines the user's CEFR level and saves the result in the database."""
    test_duration = round(time.time() - session["start_time"], 2)
    score = session["score"]

    if score >= 9:
        level = "C2"
    elif score >= 7:
        level = "C1"
    elif score >= 5:
        level = "B2"
    elif score >= 3:
        level = "B1"
    elif score >= 1:
        level = "A2"
    else:
        level = "A1"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO results (score, level, duration) VALUES (?, ?, ?)", 
                   (score, level, test_duration))
    conn.commit()
    conn.close()

    result_message = f"Your estimated English level is: {level}. You took {test_duration} seconds."
    session.clear()
    return render_template("result.html", message=result_message)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)
