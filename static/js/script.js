async function buscarVideo() {
    const urlInput = document.getElementById('urlInput');
    const btn = document.getElementById('btnBuscar');
    const resultDiv = document.getElementById('result');
    const thumbImg = document.getElementById('thumb');
    const tituloDiv = document.getElementById('titulo');
    const linkMP4 = document.getElementById('downloadLink');
    const linkMP3 = document.getElementById('downloadMP3');
    
    if (!urlInput.value) {
        alert("Por favor, cole uma URL do YouTube.");
        return;
    }
    
    // Esconde o resultado anterior e inicia o loading
    resultDiv.style.display = 'none'; 
    btn.innerText = "Analisando...";
    btn.disabled = true;

    try {
        const response = await fetch('/get_info', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ url: urlInput.value })
        });
        
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);

        // --- ATUALIZAÇÃO DOS DADOS NO HTML ---
        
        // 1. Define a imagem de capa (Thumbnail)
        if (data.thumbnail) {
            thumbImg.src = data.thumbnail;
        }

        // 2. Define o título do vídeo
        if (data.title) {
            tituloDiv.innerText = data.title;
        }

        // 3. Configura os links de download
        linkMP4.href = data.url_video; // Link para o vídeo (MP4)
        linkMP3.href = data.url_audio; // Link para o áudio (MP3)

        // 4. Mostra o container de resultado com os dados novos
        resultDiv.style.display = 'block';

    } catch (err) {
        console.error("Erro na busca:", err);
        alert("Erro: " + err.message);
    } finally {
        btn.innerText = "Analisar Vídeo";
        btn.disabled = false;
    }
}