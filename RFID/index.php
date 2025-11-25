<!doctype html>
<html lang="pt-br">

<!--====== Head ======-->
<head>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rubik&display=swap" rel="stylesheet">
	<link href="https://fonts.googleapis.com/css2?family=Inconsolata:wght@200..900&display=swap" rel="stylesheet">
	<link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap" rel="stylesheet">

    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <meta charset="utf-8">
    
    <link rel="stylesheet" href="css/index.css">
    <link rel="stylesheet" href="css/cabecalho.css">
    <link rel="stylesheet" href="css/reset.css">
    <link rel="stylesheet" href="css/footer.css">
	<link rel="stylesheet" href="css/botoes.css">

    <link rel="icon" href="img/download.png" type="image/png">
    
    <title>Projeto RFID</title>
</head>

<!--====== Main ======-->
<body>
<!--=== Topo ===-->
<?php include 'cabecalho.php' ?>

<div id="banner">
	<div class="rfidtext">
		<p class="descant">ANTENA BÁSICA</p>
		<h1 class="text">ANTENA</h1>
		<h1 class="text">13.56 MHZ</h1>
		<button class="btn" onclick=location.href="js.php">Explore Mais</button>
	</div>
	<img id="rfidimg" src="img/rfid.png">
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