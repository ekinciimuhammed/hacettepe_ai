from flask import Flask, render_template, request, jsonify, send_from_directory
from pipeline.rag_engine import generate_answer_enhanced
import os
from config import DOCS_DIR

app = Flask(__name__, static_folder="web/static", template_folder="web/templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/documents/<path:filename>")
def serve_document(filename):
    """Serve PDF files from the documents directory."""
    return send_from_directory(DOCS_DIR, filename)

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Endpoint that receives JSON { "message": "..." } 
    Returns JSON { "answer": "...", "sources": [...], "intent": "..." }
    """
    data = request.json
    user_input = data.get("message", "")
    
    if not user_input:
        return jsonify({"answer": "Bir mesaj yazmalısınız."})
    
    try:
        # Use the enhanced function that returns a dict
        result = generate_answer_enhanced(user_input)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"answer": "Bir teknik hata oluştu."}), 500

if __name__ == "__main__":
    print("🚀 Hacettepe AI Server Başlatılıyor (Port 5000)...")
    app.run(host="0.0.0.0", port=2704, debug=True)
