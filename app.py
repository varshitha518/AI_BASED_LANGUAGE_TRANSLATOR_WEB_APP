from flask import Flask, render_template, request, redirect, url_for
from googletrans import Translator
from datetime import datetime
import uuid

app = Flask(__name__)
translator = Translator()
translation_history = []

@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = ""
    detected_lang = ""
    source_lang = "auto"  # Use auto detect as default source language

    if request.method == "POST":
        text_to_translate = request.form.get("text", "").strip()
        target_lang = request.form.get("target_language", "").strip()
        source_lang = request.form.get("source_language", "auto").strip()

        if text_to_translate and target_lang:
            # Detect the input language only if source_lang is auto
            if source_lang == "auto":
                detection = translator.detect(text_to_translate)
                detected_lang = detection.lang
                source_lang = detected_lang
            else:
                detected_lang = source_lang

            # Translate
            translated = translator.translate(text_to_translate, src=source_lang, dest=target_lang)
            translated_text = translated.text

            # Add translation history with a unique UUID and timestamp
            transaction = {
                "id": str(uuid.uuid4()),  # Unique ID
                "original_text": text_to_translate,
                "translated_text": translated_text,
                "detected_lang": detected_lang,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            translation_history.append(transaction)

    return render_template(
        "index.html",
        translated_text=translated_text,
        detected_lang=detected_lang,
        source_lang=source_lang,
        history=translation_history
    )

@app.route("/delete/<entry_id>", methods=["POST"])
def delete_entry(entry_id):
    global translation_history
    translation_history = [entry for entry in translation_history if entry["id"] != entry_id]
    return redirect(url_for("index"))

@app.route("/clear_history", methods=["POST"])
def clear_history():
    global translation_history
    translation_history.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
