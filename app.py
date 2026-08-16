import os
import subprocess
from flask import Flask, render_template_string, request, jsonify

# Force kill old processes running on port 7000
try:
    subprocess.run(["fuser", "-k", "7000/tcp"], check=False)
except Exception:
    pass

app = Flask(__name__)

# Main UI Concept
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEED-X AI | Action Engine</title>
    <style>
        body { background: #0B0F19; color: #FFF; font-family: system-ui, sans-serif; text-align: center; padding: 40px 20px; }
        .card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 16px; padding: 30px; max-width: 500px; margin: 0 auto; box-shadow: 0 0 20px rgba(0, 240, 255, 0.1); }
        input, button { width: 100%; padding: 14px; margin-top: 15px; border-radius: 8px; border: none; font-size: 16px; box-sizing: border-box; }
        input { background: #161F33; color: #FFF; border: 1px solid #00F0FF; }
        button { background: linear-gradient(90deg, #00F0FF, #7000FF); color: #FFF; font-weight: bold; cursor: pointer; }
        #result { margin-top: 20px; text-align: right; background: #111827; padding: 15px; border-radius: 8px; display: none; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🌎 NEED-X AI</h2>
        <p>ما المشكلة أو الاحتياج الذي تريد حله الآن؟</p>
        <input type="text" id="userNeed" placeholder="مثال: أحتاج قطعة غيار سيارة نادرة..." />
        <button onclick="processNeed()">تحليل وتنفيذ الطلب 🚀</button>
        <div id="result"></div>
    </div>

    <script>
        async function processNeed() {
            const need = document.getElementById('userNeed').value;
            if(!need) return alert('يرجى كتابة احتياجك أولاً');
            
            const resDiv = document.getElementById('result');
            resDiv.style.display = 'block';
            resDiv.innerHTML = '⏳ جاري تحليل الاحتياج وبناء مسار التنفيذ...';
            
            try {
                const response = await fetch('/api/process-need', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ need: need })
                });
                const data = await response.json();
                
                resDiv.innerHTML = `
                    <h4>✅ مسار التنفيذ المقترح (Workflow):</h4>
                    <p><b>الاحتياج:</b> ${data.need}</p>
                    <p><b>التصنيف:</b> ${data.category}</p>
                    <p><b>النطاق:</b> ${data.scope}</p>
                    <p><b>الخطوة التنفيذية:</b> ${data.action}</p>
                `;
            } catch(e) {
                resDiv.innerHTML = '❌ حدث خطأ أثناء الاتصال بالمحرك.';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

@app.route('/api/process-need', methods=['POST'])
def process_need():
    data = request.get_json() or {}
    user_need = data.get('need', '')
    
    return jsonify({
        "status": "success",
        "need": user_need,
        "category": "طلب خدمات / حلول ذكية",
        "scope": "محلي / دولي",
        "action": "تطابق تلقائي للطلب وجاري إيجاد المورد المناسب."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
