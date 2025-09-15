from flask import Flask, render_template_string, request
from datetime import datetime
import re

app = Flask(_name_)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Fasttech Cleaner</title>
  <style>
    :root {
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --gray: #f1f5f9;
      --border: #d1d5db;
      --text: #1f2937;
      --bg: #f8fafc;
    }
    [data-theme="dark"] {
      --primary: #3b82f6;
      --primary-dark: #1e40af;
      --gray: #1e293b;
      --border: #334155;
      --text: #f1f5f9;
      --bg: #0f172a;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      transition: background 0.3s ease, color 0.3s ease;
    }
    .container {
      max-width: 800px;
      margin: 30px auto;
      background: white;
      background: var(--gray);
      padding: 24px;
      border-radius: 18px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
    }
    h1 {
      text-align: center;
      font-size: 24px;
      margin-bottom: 16px;
    }
    label {
      font-size: 14px;
      font-weight: 500;
    }
    textarea {
      width: 100%;
      padding: 14px;
      font-family: monospace;
      font-size: 14px;
      border: 1px solid var(--border);
      border-radius: 12px;
      resize: vertical;
      min-height: 200px;
      transition: border 0.3s ease;
      background: white;
      color: var(--text);
    }
    [data-theme="dark"] textarea {
      background: #1e293b;
      color: #f1f5f9;
    }
    textarea:focus {
      outline: none;
      border: 2px solid var(--primary);
    }
    .card-count {
      margin-top: 8px;
      font-size: 13px;
    }
    button, .btn {
      display: inline-block;
      width: 100%;
      margin-top: 16px;
      padding: 14px 0;
      font-size: 16px;
      font-weight: 600;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      transition: background 0.3s ease;
      text-align: center;
      text-decoration: none;
    }
    button:hover, .btn:hover {
      background: var(--primary-dark);
    }
    .btn-group {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .result {
      margin-top: 28px;
    }
    .result h2 {
      font-size: 18px;
      margin-bottom: 10px;
    }
    .footer {
      margin-top: 30px;
      text-align: center;
      font-size: 13px;
    }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    .theme-toggle {
      background: none;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 6px 10px;
      font-size: 13px;
      cursor: pointer;
    }

    @media (max-width: 600px) {
      .container {
        border-radius: 0;
        margin: 0;
        min-height: 100vh;
      }
    }
  </style>
  <script>
    function updateCount() {
      const input = document.getElementById("input_cards").value.trim();
      const lines = input ? input.split("\\n").filter(l => l.trim() !== "") : [];
      document.getElementById("line_count").innerText = lines.length + " card(s)";
    }

    function toggleTheme() {
      const root = document.documentElement;
      const current = root.getAttribute("data-theme");
      const newTheme = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
    }

    function exportTxt() {
      const output = document.getElementById("output_cards").value;
      const blob = new Blob([output], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "cleaned_cards.txt";
      a.click();
      URL.revokeObjectURL(url);
    }

    window.onload = () => {
      const savedTheme = localStorage.getItem("theme");
      if (savedTheme) {
        document.documentElement.setAttribute("data-theme", savedTheme);
      }
      updateCount();
    };
  </script>
</head>
<body>
  <div class="container">
    <div class="topbar">
      <h1>💳 MrCrypto Cleaner</h1>
      <button class="theme-toggle" onclick="toggleTheme()">🌓 Theme</button>
    </div>

    <form method="POST">
      <label for="input_cards">Paste your raw card data (max 10,000 lines):</label>
      <textarea id="input_cards" name="input_cards" oninput="updateCount()">{{ input_text or '' }}</textarea>
      <div class="card-count" id="line_count">0 card(s)</div>
      <button type="submit">🧼 Clean Cards</button>
    </form>

    {% if cleaned_cards %}
    <div class="result">
      <h2>✅ Cleaned Cards ({{ cleaned_cards|length }})</h2>
      <textarea readonly id="output_cards">{{ cleaned_cards | join('\\n') }}</textarea>
      <a class="btn" onclick="exportTxt()">📄 Download .txt</a>
    </div>
    {% endif %}

    <div class="footer">
      &copy; {{ year }} Card Cleaner • Android Web Ready • Dark Mode + Download
    </div>
  </div>
</body>
</html>
"""

def clean_card_data(lines):
    cleaned = []
    for line in lines:
        parts = line.strip().split('|')
        if len(parts) >= 4:
            card_number = parts[0].strip()
            exp_month = parts[1].strip()
            exp_year = parts[2].strip()
            cvv_raw = parts[3].strip()

            # Extract only digits from CVV part
            cvv_match = re.match(r'^\d{3,4}', cvv_raw)
            if not cvv_match:
                continue  # skip invalid CVV
            cvv = cvv_match.group()

            cleaned_line = f"{card_number}|{exp_month}|{exp_year}|{cvv}"
            cleaned.append(cleaned_line)

            if len(cleaned) >= 10000:
                break
    return cleaned

@app.route("/", methods=["GET", "POST"])
def index():
    input_text = ""
    cleaned_cards = []

    if request.method == "POST":
        input_text = request.form.get("input_cards", "")
        lines = input_text.strip().splitlines()
        cleaned_cards = clean_card_data(lines)

    return render_template_string(HTML_TEMPLATE,
                                  input_text=input_text,
                                  cleaned_cards=cleaned_cards,
                                  year=datetime.now().year)

if _name_ == "_main_":
    app.run(debug=False)
