import os
import re
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

def limpar_url(url):
    """Remove parâmetros de playlist para evitar confusão no script"""
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

    # Configurações otimizadas para rodar em servidores (Render/Railway)
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'extract_flat': False,
        'socket_timeout': 30,
        'source_address': '0.0.0.0', # Força o uso do IPv4
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrai informações sem baixar o arquivo
            info = ydl.extract_info(video_url, download=False)
            
            # Tenta pegar a URL direta do vídeo
            url_video = info.get('url') or (info.get('formats')[-1].get('url') if info.get('formats') else None)

            # Filtra apenas formatos de áudio
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
        error_msg = str(e)
        print(f"[DEBUG] ERRO NO SERVIDOR: {error_msg}")
        
        # Tradução amigável para erros comuns de servidor
        if "403" in error_msg or "Sign in" in error_msg:
            return jsonify({'error': 'O YouTube bloqueou temporariamente o servidor. Tente novamente em instantes ou mude a região no Render.'}), 500
        
        return jsonify({'error': 'Não foi possível analisar este vídeo. Verifique a URL.'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
