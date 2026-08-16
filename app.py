import os
import subprocess
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEED-X AI | Voice & Action Engine</title>
    <style>
        body { background: #0B0F19; color: #FFF; font-family: system-ui, sans-serif; text-align: center; padding: 30px 15px; }
        .card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(12px); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 16px; padding: 25px; max-width: 480px; margin: 0 auto; box-shadow: 0 0 25px rgba(0, 240, 255, 0.15); }
        input, button { width: 100%; padding: 14px; margin-top: 12px; border-radius: 8px; border: none; font-size: 16px; box-sizing: border-box; }
        input { background: #161F33; color: #FFF; border: 1px solid #00F0FF; outline: none; }
        .btn-main { background: linear-gradient(90deg, #00F0FF, #7000FF); color: #FFF; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-voice { background: rgba(0, 240, 255, 0.15); border: 1px solid #00F0FF; color: #00F0FF; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-main:hover, .btn-voice:hover { opacity: 0.9; transform: scale(1.01); }
        #result { margin-top: 20px; text-align: right; background: #111827; border: 1px solid rgba(255,255,255,0.1); padding: 18px; border-radius: 10px; display: none; line-height: 1.7; }
        .tag { display: inline-block; background: rgba(0, 240, 255, 0.2); color: #00F0FF; padding: 2px 8px; border-radius: 4px; font-size: 13px; margin-right: 5px; }
        .voice-controls { display: flex; gap: 10px; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🌎 NEED-X AI</h2>
        <p>ما المشكلة أو الاحتياج الذي تريد حله الآن؟</p>
        
        <input type="text" id="userNeed" placeholder="اكتب أو تحدث باحتياجك (عربي/EN/FR)..." />
        
        <div class="voice-controls">
            <button class="btn-voice" onclick="startVoiceInput()">🎙️ إدخال صوتي</button>
            <button class="btn-voice" onclick="toggleSpeech()" id="speakBtn">🔊 قراءة النتيجة</button>
        </div>

        <button class="btn-main" onclick="processNeed()">تحليل وتنفيذ الطلب 🚀</button>
        <div id="result"></div>
    </div>

    <script>
        let lastSpeechText = "";

        // 1. Voice Input (Speech Recognition)
        function startVoiceInput() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                alert("خاصية التعرف على الصوت غير مدعومة في متصفحك.");
                return;
            }
            const recognition = new SpeechRecognition();
            recognition.lang = 'ar-SA'; // Default language recognition
            recognition.interimResults = false;

            document.getElementById('userNeed').placeholder = "🎧 جاري الاستماع إليك...";
            recognition.start();

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('userNeed').value = transcript;
                processNeed();
            };

            recognition.onerror = () => {
                document.getElementById('userNeed').placeholder = "لم يتم التقاط الصوت، حاول مجدداً.";
            };
        }

        // 2. Text Processing & Action Engine
        async function processNeed() {
            const need = document.getElementById('userNeed').value;
            if(!need) return alert('يرجى كتابة أو نطق احتياجك أولاً');
            
            const resDiv = document.getElementById('result');
            resDiv.style.display = 'block';
            resDiv.innerHTML = '⏳ جاري تحليل الاحتياج وبناء مسار التنفيذ الذكي...';
            
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
                    <p><b>التصنيف:</b> <span class="tag">${data.category}</span></p>
                    <p><b>النطاق:</b> ${data.scope}</p>
                    <p><b>الخطة التنفيذية:</b> ${data.action}</p>
                    <p><b>النتيجة المتوقعة:</b> ${data.result}</p>
                `;

                // Prepare robot text for voice response
                lastSpeechText = `${data.speech_response}`;
                speakText(lastSpeechText, data.lang);

            } catch(e) {
                resDiv.innerHTML = '❌ حدث خطأ أثناء الاتصال بالمحرك.';
            }
        }

        // 3. Multilingual Text-to-Speech Engine
        function speakText(text, lang) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel(); // Stop active speech
                const utterance = new SpeechSynthesisUtterance(text);
                
                if (lang === 'ar') utterance.lang = 'ar-SA';
                else if (lang === 'fr') utterance.lang = 'fr-FR';
                else utterance.lang = 'en-US';

                utterance.pitch = 1.0;
                utterance.rate = 0.95; // Natural robot pace
                window.speechSynthesis.speak(utterance);
            }
        }

        function toggleSpeech() {
            if (lastSpeechText) {
                speakText(lastSpeechText);
            } else {
                alert("لا توجد نتيجة حالية لقراءتها.");
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
    text = data.get('need', '').lower()
    
    # Language Detector (Basic pattern match for Trilingual support)
    lang = 'ar'
    if any(char in text for char in 'abcdefghijklmnopqrstuvwxyz'):
        if any(f_word in text for f_word in ['de', 'la', 'pièce', 'voiture', 'besoin', 'chercher', 'maison']):
            lang = 'fr'
            category = "Automobile et Pièces / Ingénierie"
            scope = "Local et Importation"
            action = "Vérification des pièces requises et sélection des fournisseurs."
            result = "Obtention de 3 devis en quelques minutes."
            speech = f"Besoin analysé: {data.get('need')}. Plan d'action configuré."
        else:
            lang = 'en'
            category = "Software & Tech Solutions"
            scope = "Global / Digital"
            action = "Architecture setup, code repository and instant deployment plan."
            result = "Live MVP server ready for testing."
            speech = f"Need analyzed: {data.get('need')}. Execution workflow generated."
    else:
        # Arabic Engine
        if any(k in text for k in ['سيارة', 'سيارات', 'قطع', 'غيار', 'مرسيدس']):
            category = "محركات وقطع غيار / Automotive"
            scope = "محلي + استيراد دولي"
            action = "فحص متطلبات القطعة المطلوب استبدالها وترشيح الموردين المعتمدين."
            result = "توفير 3 عروض أسعار خلال دقائق."
            speech = f"تم تحليل الاحتياج: {data.get('need')}. جاري الربط مع الموردين."
        else:
            category = "طلب خدمات وحلول مخصصة"
            scope = "محلي / دولي"
            action = "تحليل الألفاظ وبناء مسار الربط المباشر بين الطالب والمنفذ."
            result = "تحديد أفضل خيارات التنفيذ المتاحة."
            speech = f"تم تسجيل طلبك: {data.get('need')}. الخطة التنفيذية جاهزة."

    return jsonify({
        "status": "success",
        "need": data.get('need', ''),
        "category": category,
        "scope": scope,
        "action": action,
        "result": result,
        "speech_response": speech,
        "lang": lang
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
