<!DOCTYPE html>
<html lang="pt-br">
<head>
    <link rel="stylesheet" href="css/cabecalho.css">
    <link rel="stylesheet" href="css/reset.css">
    <link rel="stylesheet" href="css/sobre.css">
    <link rel="stylesheet" href="css/footer.css">
    <link rel="stylesheet" href="css/popup.css">
    <link rel="stylesheet" href="css/teste.css">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rubik&display=swap" rel="stylesheet">

    <link rel="icon" href="img/download.png" type="image/png">

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Materiais</title>
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
    <!--=== Container ===-->
    <div class="container">
        <div id="sobre">
            <div id="titulo-sobre">
                <h1 id="desc-titulo">Materiais e Componentes Utilizados</h1>
            </div>

            <!--=== Container ===-->
            <div id="content-sobre" onclick="abrirPopuplist('Materiais e Componentes Utilizados', 'Para o Desenvolvimento do sistema de controle de estoque via RFID , foram utilizados os seguintes componentes eletrônicos e materiais auxiliares:', ['Arduino UNO (X2) - Microcontrolador responsável por processar os sinais do sensor RFID e ativar o buzzer.', 'Leitor RFID RC522 (X2) - Módulo que realiza a leitura das tags RFID utilizadas nos itens do estoque.', 'Etiquetas RFID (2-5) - Utilizadas para identificar individualmente cada item ou ferramenta.', 'Buzzer ativo (X2) - Componente sonoro que é acionado sempre que um item não autorizado sai da sala.', 'Jumpers (15+) - Conectores utilizados para interligar o componentes no protoboard.', 'Resistores (X2) - Utilizados conforme a necessidade para controle de corrente nos circuitos.', 'Fonte de alimentação 12V (X2) - Utilizada para fornecer energia ao Arduino e demais componentes', 'Notebook/Computador - Usado para programar o Arduino, aplicativo e desenvolvimento Web.'])">
                <p class="desc">Para o Desenvolvimento do sistema de controle de estoque via RFID , foram utilizados os seguintes componentes eletrônicos e materiais auxiliares:</p>
                <ul>
                    <p class="desclist">Arduino UNO (X2) - Microcontrolador responsável por processar os sinais do sensor RFID e ativar o buzzer.</p>
                    <p class="desclist">Leitor RFID RC522 (X2) - Módulo que realiza a leitura das tags RFID utilizadas nos itens do estoque.</p>
                    <p class="desclist">Etiquetas RFID (2-5) - Utilizadas para identificar individualmente cada item ou ferramenta.</p>
                    <p class="desclist">Buzzer ativo (X2) - Componente sonoro que é acionado sempre que um item não autorizado sai da sala.</p>
                    <p class="desclist">Jumpers (15+) - Conectores utilizados para interligar o componentes no protoboard.</p>
                    <p class="desclist">Resistores (X2) - Utilizados conforme a necessidade para controle de corrente nos circuitos.</p>
                    <p class="desclist">Fonte de alimentação 12V (X2) - Utilizada para fornecer energia ao Arduino e demais componentes</p>
                    <p class="desclist">Notebook/Computador - Usado para programar o Arduino, aplicativo e desenvolvimento Web.</p>
                </ul>
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