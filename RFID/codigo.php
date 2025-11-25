<!DOCTYPE html>
<html lang="pt-br">
<head>
    <link rel="stylesheet" href="css/cod.css">
    <link rel="stylesheet" href="css/cabecalho.css">
    <link rel="stylesheet" href="css/reset.css">
    <link rel="stylesheet" href="css/footer.css">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rubik&display=swap" rel="stylesheet">

    <link rel="icon" href="img/download.png" type="image/png">

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Código em C</title>
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

<div id="img">
    <img src="img/setup.jpg" alt="Código do Projeto" id="codigo-img">
    <img src="img/loop.jpg" alt="Código do Projeto" id="codigo-loop-img">
</div>

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