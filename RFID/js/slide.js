document.addEventListener("DOMContentLoaded", function () {
    console.log("slide.js carregado");
    const slider = document.querySelector(".slider");
    const banners = Array.from(document.querySelectorAll(".banner"));
    if (!slider) {
        console.error("ERRO: .slider não encontrado. Verifique HTML (falta <div class='slider'>).");
        return;
    }
    if (banners.length === 0) {
        console.error("ERRO: nenhum .banner encontrado. Verifique HTML.");
        return;
    }

    // Forçar estilo base
    banners.forEach(b => { b.style.minWidth = "100%"; b.style.boxSizing = "border-box"; });
    slider.style.display = "flex";
    slider.style.width = (banners.length * 100) + "%";

    // espera imagens (resolve também em erro de carregamento)
    const imgs = slider.querySelectorAll("img");
    const imgPromises = Array.from(imgs).map(img => {
        if (img.complete && img.naturalHeight !== 0) return Promise.resolve();
        return new Promise(res => { img.addEventListener("load", res); img.addEventListener("error", res); });
    });

    let index = 0;
    function goTo(i) {
        index = (i + banners.length) % banners.length;
        slider.style.transform = `translateX(${-index * 100}%)`;
        console.log("slide ->", index);
    }
    function next(){ goTo(index+1); }
    function startAutoplay(){ return setInterval(next, 5000); }

    Promise.all(imgPromises).then(() => {
        console.log("Imagens tratadas. iniciando...");
        // forçar repaint
        slider.getBoundingClientRect();
        goTo(0);
        // delay pequeno antes de iniciar o autoplay
        setTimeout(() => { window.__slideInterval = startAutoplay(); }, 200);
    });

    // exposição para debug no console
    window.__debugSlider = { slider, banners, goTo, next };
});
