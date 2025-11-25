<!DOCTYPE html>
<html lang="pt-br">
<head>
    <link rel="stylesheet" href="css/cabecalho.css">
    <link rel="stylesheet" href="css/reset.css">
    <link rel="stylesheet" href="css/sobre.css">
    <link rel="stylesheet" href="css/footer.css">
    <link rel="stylesheet" href="css/popup.css">
    

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rubik&display=swap" rel="stylesheet">

    <link rel="icon" href="img/download.png" type="image/png">

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sobre</title>
</head>
<body>

<!--=== Topo ===-->
<header>

    <div id="h-logo">
        <img id="logo" src="img/senai.png"> <!-- Logo -->
    </div>
    
    <!--=== Menu ===-->
    <nav>
        <ul>
            <button class="menu" onclick=location.href="index.php">Home</button> <!-- Contato (Footer); Galeria; Funcionalidades; Breve descrição do projeto -->

                <!-- Dropdown -->
                <div class="dropdown">
                    <button class="menu">Sobre</button>
                    <div class="dropdown-content">
                        <a href="sobre.php">Projeto</a>
                        <a href="etapas.php">Etapas</a>
                        <a href="materiais.php">Materiais</a>
                    </div>
                </div>

            <button class="menu" onclick=location.href="equipe.php">Equipe</button>
            <button class="menu" onclick=location.href="codigo.php">Código</button>
        </ul>
    </nav>

    <div id="ht-logo">
        <img id="t-logo" src="img/tramonlogo.png"> <!-- Logo -->
    </div>

</header>

<div id="content">
    <div class="container" onclick="abrirPopup('Sobre o Projeto', 'Este projeto vem sendo realizado durante as aulas de Fundamentos da Eletrônica Aplicada e Programação em C para Arduino, no curso Técnico em desenvolvimento de sistemas do SENAI. O projeto tem como objetivo aplicar os conhecimentos adquiridos em aula, bem como o resultado de pesquisas externas realizadas pela equipe. O sensor RFID terá a responsabilidade de detectar o fluxo de itens ou ferramentas ao saírem pela porta da maquete onde o sistema está instalado. Quando isso ocorrer, um alarme sonoro (buzzer) será acionado automaticamente. O objetivo do projeto é de, após sua conclusão, apresentar nossa ideia para o SENAI com o intuito de aplicá-la na instituição de Farroupilha a fim de garantir e permitir maior controle e segurança na movimentação de itens dentro do ambiente SENAI, evitando perdas. Além disso, sua aplicação prática proporciona à equipe, uma oportunidade de aprofundar nossos conhecimentos e aprendizados sobre trabalho em equipe, podendo abrir novas oportunidades acadêmicas e profissionais no futuro.')">
        <div id="sobre">
            <div id="titulo-sobre">
                <h1 id="desc-titulo">Sobre o Projeto</h1>
            </div>

            <!--=== Container ===-->
            <div id="content-sobre">
                <p class="desc">Este projeto vem sendo realizado durante as aulas de Fundamentos da Eletrônica Aplicada e Programação em C para Arduino, no curso Técnico em desenvolvimento de sistemas do SENAI. O projeto tem como objetivo aplicar os conhecimentos adquiridos em aula, bem como o resultado de pesquisas externas realizadas pela equipe. O sensor RFID terá a responsabilidade de detectar o fluxo de itens ou ferramentas ao saírem pela porta da maquete onde o sistema está instalado. Quando isso ocorrer, um alarme sonoro (buzzer) será acionado automaticamente.</p>
                <p class="desc">O objetivo do projeto é de, após sua conclusão, apresentar nossa ideia para o SENAI com o intuito de aplicá-la na instituição de Farroupilha a fim de garantir e permitir maior controle e segurança na movimentação de itens dentro do ambiente SENAI, evitando perdas. </p>
                <p class="desc">Além disso, sua aplicação prática proporciona à equipe, uma oportunidade de aprofundar nossos conhecimentos e aprendizados sobre trabalho em equipe, podendo abrir novas oportunidades acadêmicas e profissionais no futuro.</p>
            </div>
        </div>
    </div>
</div>

    <!-- === POPUP 1 === -->
    <div id="popup" class="popup-overlay" onclick="fecharPopup()">
        <div class="popup-content" onclick="event.stopPropagation()">
            <h2>Sobre o Projeto</h2>
            <p></p>
        <button onclick="fecharPopup()">Fechar</button>
        </div>
    </div>

    <!-- === POPUP 2 === -->
    <div id="popup2" class="popup2-overlay" onclick="fecharPopup()">
        <div class="popup2-content" onclick="event.stopPropagation()">
            <h2>Sobre o Projeto</h2>
            <p></p>
        <button onclick="fecharPopup2()">Fechar</button>
        </div>
    </div>

    <!-- === SCRIPTS === -->
    <!--=== Script 1 ===-->
    <script>
        function abrirPopup(titulo, texto) {
            const popup = document.getElementById('popup');
            const popupTitulo = popup.querySelector('h2');
            const popupTexto = popup.querySelector('p');

            popupTitulo.innerText = titulo;
            popupTexto.innerText = texto;

            popup.classList.add('ativo');
        }

    //Script 2 (fechar popup)

        function fecharPopup() {
            const popup = document.getElementById('popup');
            popup.classList.remove('ativo');
        }

    //Script 3 (abrir popup2)

        function abrirpoplist(titulo, texto, lista) {
            const popup = document.getElementById('popup2');
            const popupTitulo = popup.querySelector('h2');
            const popupTexto = popup.querySelector('p');

            popupTitulo.innerText = titulo;
            popupTexto.innerText = texto;
            popupTexto.innerText = lista.join('\n');

            // Transformar lista em texto com quebras de linha
            const listaFormatada = lista.join('\n');

            // Coloca o texto principal + duas quebras de linha + a lista formatada
            popupTexto.innerText = texto + '\n\n' + listaFormatada;

            popup.classList.add('ativo');
        }

    //Script 3 (fechar popup2)
        function fecharPopup2() {
            const popup = document.getElementById('popup2');
            popup.classList.remove('ativo');
        }

    //Script 4 (abrir popup com lista)
        // Esta função recebe um título, um texto e uma lista de itens, e exibe-os em um popup.
        function abrirPopuplist(titulo, texto, lista) {
            const popup = document.getElementById('popup');
            const popupTitulo = popup.querySelector('h2');
            const popupTexto = popup.querySelector('p');

            popupTitulo.innerText = titulo;
            popupTexto.innerText = texto;
            popupTexto.innerText = lista.join('\n');

            // Transformar lista em texto com quebras de linha
            const listaFormatada = lista.join('\n');

            // Coloca o texto principal + duas quebras de linha + a lista formatada
            popupTexto.innerText = texto + '\n\n' + listaFormatada;

            popup.classList.add('ativo');
        }

    </script>


    
</body>
<!--====== Rodapé ======-->
<footer>
    <div id="footer-contact">
        <p>&copy; 2025 SENAI. Todos os direitos reservados.</p>
        <h3>Fale Conosco</h3>
        <p>Email: contato404.exe@gmail.com</p>
    </div>
</footer>
</html>