// ========= BLOCO DE PROTEÇÃO (evita erros de extensões) =========
(function () {
    const blockList = [
        "A listener indicated",
        "message channel closed",
        "asynchronous response"
    ];

    window.addEventListener("error", e => {
        if (blockList.some(b => (e.message || "").includes(b))) {
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    }, true);

    window.addEventListener("unhandledrejection", e => {
        if (blockList.some(b => (e.reason || "").toString().includes(b))) {
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    }, true);
})();

// ==================== SLIDER =======================
document.addEventListener("DOMContentLoaded", function () {
    console.log("slide.js: iniciado");

    const sliderWrapper = document.querySelector("#slider-wrapper");
    const slider = sliderWrapper ? sliderWrapper.querySelector(".slider") : null;
    let banners = slider ? Array.from(slider.querySelectorAll(".banner")) : [];

    if (!sliderWrapper || !slider) {
        console.error("slide.js: Estrutura do slider não encontrada.");
        return;
    }
    if (banners.length === 0) {
        console.error("slide.js: Nenhum .banner encontrado.");
        return;
    }

    console.log("slide.js: banners encontrados:", banners.length);

    // === Configuração da faixa deslizante ===
    slider.style.display = "flex";
    slider.style.width = `${banners.length * 100}%`;
    slider.style.transition = "transform 0.6s ease-in-out";
    slider.style.willChange = "transform";

    banners.forEach(b => {
        b.style.minWidth = "100%";
        b.style.boxSizing = "border-box";
    });

    // === Esperar imagens carregarem ===
    const imgs = slider.querySelectorAll("img");
    const imgPromises = Array.from(imgs).map(img => {
        if (img.complete && img.naturalHeight !== 0) return Promise.resolve();
        return new Promise(resolve => {
            img.addEventListener("load", resolve);
            img.addEventListener("error", () => resolve());
        });
    });

    let index = 0;

    const backgrounds = [
        "#0a6112",              // fundo 1 (verde)
        "#001d3d",              // fundo 2 (azul)
        "#2b2b2b",              // fundo 3 (preto)
        "#857d7d"               // fundo 4 (cinza)
    ];

    function applyButtonStyleForBackground(bg, bannerEl) {
    let buttons = bannerEl ? Array.from(bannerEl.querySelectorAll(".btn")) : [];

    if (buttons.length === 0) {
        buttons = Array.from(document.querySelectorAll(".btn"));
    }

    buttons.forEach(btn => {
        // reseta
        btn.style.removeProperty("--color");

        if (bg === "#001d3d") {           // azul
            btn.style.setProperty("--color", "#c9c7c8");
			btn.style.setProperty("--hover-text", "#001d3d");

        } else if (bg === "#2b2b2b") {    // preto
            btn.style.setProperty("--color", "#c9c7c8");
			btn.style.setProperty("--hover-text", "#2b2b2b");

        } else if (bg === "#0a6112") {    // verde
            btn.style.setProperty("--color", "#c9c7c8");
			btn.style.setProperty("--hover-text", "#0a6112");

        } else {
            // fundo claro → deixe padrão do CSS
            btn.style.removeProperty("--color");
			btn.style.setProperty("--hover-text", "#857d7d");
        }
    });
}


    function goTo(i) {
        index = ((i % banners.length) + banners.length) % banners.length;
        slider.style.transform = `translateX(${-index * 100}%)`;

        // === ALTERA O FUNDO AQUI ===
        const wrapper = document.querySelector("#slider-wrapper");
        wrapper.style.transition = "background 0.8s ease-in-out";

        let bg = backgrounds[index] || "";

        // se for imagem (string tipo url(...)) ou cor
        if (typeof bg === "string" && bg.startsWith("url")) {
            wrapper.style.backgroundImage = bg;
            wrapper.style.backgroundSize = "cover";
            wrapper.style.backgroundPosition = "center";
            wrapper.style.background = ""; // limpa cor
        } else {
            wrapper.style.background = bg;
            wrapper.style.backgroundImage = "";
        }

        // aplica estilos aos botões do banner atual (com proteção)
        try {
            const currentBanner = banners[index];
            applyButtonStyleForBackground(bg, currentBanner);
        } catch (err) {
            console.warn("slide.js: erro ao aplicar estilo do botão:", err);
        }
    }

    function next() { goTo(index + 1); }

    // === AutoPlay ===
    let autoplayId = null;

    function startAutoplay() {
        if (!autoplayId)
            autoplayId = setInterval(next, 5000);
    }
    function stopAutoplay() {
        clearInterval(autoplayId);
        autoplayId = null;
    }

    // inicia após imagens carregadas
    Promise.all(imgPromises).then(() => {
        goTo(0);
        setTimeout(startAutoplay, 250);
    }).catch(err => {
        console.error("slide.js: erro ao carregar imagens:", err);
        goTo(0);
        startAutoplay();
    });

    // pausa quando sair da aba
    window.addEventListener("visibilitychange", () => {
        document.hidden ? stopAutoplay() : startAutoplay();
    });

    window.__mySlider = { goTo, next, startAutoplay, stopAutoplay };
});
