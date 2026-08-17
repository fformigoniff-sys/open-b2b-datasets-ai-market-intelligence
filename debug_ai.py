import os
import json
import requests

print("--- AVVIO TEST ISOLATO NICCHIA 4 (AI GENERATION) ---")

gemini_key = os.getenv('GEMINI_API_KEY')
groq_key = os.getenv('GROQ_API_KEY')

print(f"Verifica Chiavi -> GEMINI_KEY presente: {bool(gemini_key)} | GROQ_KEY presente: {bool(groq_key)}")

prompt = """Genera 3 coppie di domande e risposte B2B per fine-tuning.
Restituisci SOLO un array JSON valido con questa struttura esatta:
[{"instruction": "Domanda tecnica", "input": "", "output": "Risposta tecnica"}]"""

generated_data = None

# TEST 1: Google Gemini Flash
if gemini_key:
    print("\n[TEST GEMINI] Invio richiesta a Google Gemini API...")
    url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url_gemini, json=payload, timeout=15)
        print(f"[TEST GEMINI] HTTP Status Code: {res.status_code}")
        print(f"[TEST GEMINI] Risposta Server:\n{res.text[:400]}")
        if res.status_code == 200:
            raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
            generated_data = json.loads(clean_json)
            print("[TEST GEMINI] ✅ Parsing JSON completato con successo!")
    except Exception as e:
        print(f"[TEST GEMINI] ❌ Errore: {e}")

# TEST 2: Groq Llama 3 (Se Gemini fallisce o non produce dati)
if not generated_data and groq_key:
    print("\n[TEST GROQ] Invio richiesta a Groq API (Fallback)...")
    url_groq = "https://api.groq.com/openai/v1/chat/completions"
    headers = {'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'}
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    try:
        res = requests.post(url_groq, headers=headers, json=payload, timeout=15)
        print(f"[TEST GROQ] HTTP Status Code: {res.status_code}")
        print(f"[TEST GROQ] Risposta Server:\n{res.text[:400]}")
        if res.status_code == 200:
            content = res.json()['choices'][0]['message']['content']
            clean_json = content.replace("```json", "").replace("```", "").strip()
            generated_data = json.loads(clean_json)
            print("[TEST GROQ] ✅ Parsing JSON completato con successo!")
    except Exception as e:
        print(f"[TEST GROQ] ❌ Errore: {e}")

# SCRITTURA FILE
if generated_data:
    try:
        with open('ai_finetuning_dataset.jsonl', 'w', encoding='utf-8') as f:
            for row in generated_data:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
        print("\n🎉 SUCCESSO: File 'ai_finetuning_dataset.jsonl' creato e scritto correttamente!")
    except Exception as e:
        print(f"\n❌ Errore scrittura su disco: {e}")
else:
    print("\n⚠️ FALLIMENTO: Nessun dato generato dai motori IA.")
