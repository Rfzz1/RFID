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
    <title>Etapas</title>
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
                <h1 id="desc-titulo">Etapas do Projeto</h1>
            </div>

            <!--=== Container ===-->
            <div id="content-sobre" onclick="abrirpoplist('Etapas do Projeto', 'Com base nos objetivos estabelecidos, nossa equipe, juntamente ao professor Marcelo Dipp estruturou o trabalho em etapas bem definidas, de modo a facilitar a execução e acompanhamento do progresso do projeto.', ['1. Ideia Inicial - Na disciplina de Fundamentos da Eletrônica Aplicada, o professor Marcelo Dipp nos propôs desenvolver um projeto envolvendo um circuito eletrônico. Decidimos então, por desenvolver um sistema de controle de estoque com RFID.', '2. Pesquisa - Após a definição da ideia, iniciamos uma pesquisa sobre os componentes necessários, como o módulo RFID, Arduino, buzzer e outros.', '3. Esquematização do Cartaz - O primeiro passo para o desenvolvimento do projeto foi criar um diagrama visual explicativo em formato de cartaz. Esse material teve como objetivo representar de maneira clara e didática o funcionamento do circuito elétrico, evidenciando a interação entre o Arduino, os módulos RFID, os buzzers e as fontes de alimentação.', '4. Documentação do Projeto - Essa etapa foi iniciada em paralelo com a elaboração do cartaz explicativo, registrando desde os conceitos iniciais até as decisões técnicas tomadas pela equipe.', '5. Montagem da maquete - Com o conceito e esquematização definidos, conseguimos montar a maquete com mais facilidade, permitindo assim, um maior entendimento sobre o circuito.', '6. Desenvolvimento do Site e do Código do Arduino - Com a documentação concluída e a maquete feita, começamos com o web desenvolvimento e o código para fazer o circuito funcionar. A escolha de cores e itens para o site, foi feita delicadamente para uma maior harmonia.', '7. Apresentação do projeto - A apresentação do projeto vem sendo realizada nos dias 20, 21 e 22 de Agosto.'])">
                <p class="desc">Com base nos objetivos estabelecidos, nossa equipe, juntamente ao professor Marcelo Dipp estruturou o trabalho em etapas bem definidas, de modo a facilitar a execução e acompanhamento do progresso do projeto.</p>
                <p class="desc">1. Ideia Inicial - Na disciplina de Fundamentos da Eletrônica Aplicada, o professor Marcelo Dipp nos propôs desenvolver um projeto envolvendo um circuito eletrônico. Decidimos então, por desenvolver um sistema de controle de estoque com RFID.</p>
                <p class="desc">2. Pesquisa - Após a definição da ideia, iniciamos uma pesquisa sobre os componentes necessários, como o módulo RFID, Arduino, buzzer e outros.</p>
                <p class="desc">3. Esquematização do Cartaz - O primeiro passo para o
                desenvolvimento do projeto foi criar um diagrama visual explicativo em formato de cartaz. Esse material teve como objetivo representar de maneira clara e didática o funcionamento
                do circuito elétrico, evidenciando a interação entre o Arduino, os módulos RFID, os
                buzzers e as fontes de alimentação.</p>
                <p class="desc">4. Documentação do Projeto - Essa etapa foi iniciada em paralelo com a elaboração do cartaz explicativo, registrando desde os conceitos iniciais até as decisões técnicas tomadas pela equipe.</p>
                <p class="desc">5. Montagem da maquete - Com o conceito e esquematização definidos, conseguimos montar a maquete com mais facilidade, permitindo assim, um maior entendimento sobre o circuito.</p>
                <p class="desc">6. Desenvolvimento do Site e do Código do Arduino - Com a documentação concluída e a maquete feita, começamos com o web desenvolvimento e o código para fazer o circuito funcionar. A escolha de cores e itens para o site, foi feita delicadamente para uma maior harmonia.</p>
                <p class="desc">7. Apresentação do projeto - A apresentação do projeto vem sendo realizada nos dias 20, 21 e 22 de Agosto.</p>
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

