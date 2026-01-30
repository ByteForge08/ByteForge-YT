import os
import re
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

def limpar_url(url):
    """Remove parâmetros de playlist para evitar travamentos"""
    if "list=" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
    return url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info', methods=['POST'])
def get_info():
    data = request.json
    raw_url = data.get('url')
    video_url = limpar_url(raw_url)
    
    if not video_url:
        return jsonify({'error': 'URL inválida'}), 400

    ydl_opts = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'noplaylist': True,
    'extract_flat': False, # Força a extração completa
    'socket_timeout': 30,  # Dá mais tempo para o servidor responder
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            url_video = info.get('url') or info.get('formats')[-1].get('url')

            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('vcodec') == 'none']
            
            if audio_formats:
                
                url_audio = audio_formats[-1].get('url')
            else:
                
                url_audio = url_video

            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'url_video': url_video,
                'url_audio': url_audio,
                'duration': info.get('duration_string')
            })
            
    except Exception as e:
        print(f"[DEBUG] ERRO: {str(e)}")
        return jsonify({'error': 'Erro ao analisar vídeo.'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

