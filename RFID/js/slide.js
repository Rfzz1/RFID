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
    {
        bg: "linear-gradient(135deg, #0a6112, #0f9d31)",
        theme: "#ffffff", // verde
		texto: "#000000"
    },
    {
        bg: "linear-gradient(135deg, #001d3d, #003566)",
        theme: "#ffffff", // azul
		texto: "#000000"
    },
    {
        bg: "linear-gradient(135deg, #2b2b2b, #1a1a1a)",
        theme: "#ffffff", // preto
		texto: "#000000"
    },
    {
        bg: "linear-gradient(135deg, #857d7d, #9b9494)",
        theme: "#000000", // cinza
		texto: "#ffffff"
    }
];


function applyButtonStyleForBackground(themeColor, textoColor, bannerEl) {
    let buttons = bannerEl ? Array.from(bannerEl.querySelectorAll(".btn")) : [];

    if (buttons.length === 0) {
        buttons = Array.from(document.querySelectorAll(".btn"));
    }

    buttons.forEach(btn => {
        // define cor do efeito/borda/glow
        if (themeColor) {
            btn.style.setProperty("--color", themeColor);
        } else {
            btn.style.removeProperty("--color");
        }

        // define cor do texto no hover (fallback branco caso não definido)
        if (textoColor) {
            btn.style.setProperty("--hover-text", textoColor);
        } else {
            btn.style.setProperty("--hover-text", "#ffffff");
        }
    });
}

function updateBackgroundSmoothly(index) {
    const { bg, theme, texto } = backgrounds[index];

    if (lastBgTimeout) clearTimeout(lastBgTimeout);

    lastBgTimeout = setTimeout(() => {
        // body suave
        document.body.style.transition = "background 0.8s ease";
        document.body.style.setProperty("background", bg);

const headerBg = document.querySelector("#header-bg");
const headerBgNext = document.querySelector("#header-bg-next");

if (headerBg && headerBgNext) {
  // prepara next com o gradiente (sem alterar opacidade ainda)
  headerBgNext.style.background = bg;
  headerBgNext.style.opacity = 0; // garante estado inicial

  // força repaint antes de animar (ajuda a evitar flicker em alguns browsers)
  // eslint-disable-next-line no-unused-expressions
  headerBgNext.offsetHeight;

  // crossfade: next aparece, current some
  headerBgNext.style.opacity = 1;
  headerBg.style.opacity = 0;

  // após o tempo da transição, copia o bg para a camada principal e restaura os estados
  setTimeout(() => {
    headerBg.style.background = bg;
    headerBg.style.opacity = 1;      // mantém principal visível
    headerBgNext.style.opacity = 0;  // prepara next para próxima troca
  }, 820); // pequeno buffer maior que 0.8s da transition
} else {
  // fallback: caso as camadas não existam, aplica direto no header (menos ideal)
  const header = document.querySelector("header");
  if (header) header.style.background = bg;
}

        document.body.style.backgroundAttachment = "fixed";


        // botões
        applyButtonStyleForBackground(theme, texto);

        lastBgTimeout = null;
    }, 300);
}



function goTo(i) {
    index = ((i % banners.length) + banners.length) % banners.length;
    slider.style.transform = `translateX(${-index * 100}%)`;

    const wrapper = document.querySelector("#slider-wrapper");
    wrapper.style.transition = "background 0.8s ease-in-out";

    // pega o bg/envio correto do array
    const bgObj = backgrounds[index];
	const bgValue = bgObj.bg;
	const themeColor = bgObj.theme;
	const textoColor = bgObj.texto;

	updateBackgroundSmoothly(index);



    // wrapper transparente
    wrapper.style.background = "transparent";



    // aplica estilo do botão
    try {
        const currentBanner = banners[index];
        applyButtonStyleForBackground(themeColor, textoColor, currentBanner);
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
	
// suas variáveis do slider
let currentIndex = 0;
let lastBgTimeout = null;


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
