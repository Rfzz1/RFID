-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geraÃ§Ã£o: 13/11/2025 Ã s 18:07
-- VersÃ£o do servidor: 10.4.28-MariaDB
-- VersÃ£o do PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `db_rfid`
--
CREATE DATABASE IF NOT EXISTS `db_rfid` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `db_rfid`;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_admin`
--

DROP TABLE IF EXISTS `tb_admin`;
CREATE TABLE IF NOT EXISTS `tb_admin` (
  `id_admin` int(11) NOT NULL AUTO_INCREMENT,
  `usuario` varchar(50) DEFAULT NULL,
  `senha` varchar(255) DEFAULT NULL,
  `nome` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_admin`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `tb_admin`
--

INSERT INTO `tb_admin` (`id_admin`, `usuario`, `senha`, `nome`) VALUES
(1, 'admin', 'Y90R$Lpi!', NULL);

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_categorias`
--

DROP TABLE IF EXISTS `tb_categorias`;
CREATE TABLE IF NOT EXISTS `tb_categorias` (
  `id_categoria` int(11) NOT NULL AUTO_INCREMENT,
  `nome_categoria` varchar(100) NOT NULL,
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_ferramentas`
--

DROP TABLE IF EXISTS `tb_ferramentas`;
CREATE TABLE IF NOT EXISTS `tb_ferramentas` (
  `id_ferramentas` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` text DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `status` enum('disponÃ­vel','emprestada','manutenÃ§Ã£o') DEFAULT 'disponÃ­vel',
  PRIMARY KEY (`id_ferramentas`),
  KEY `id_categoria` (`id_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_movimentacoes`
--

DROP TABLE IF EXISTS `tb_movimentacoes`;
CREATE TABLE IF NOT EXISTS `tb_movimentacoes` (
  `id_mov` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `id_ferramentas` int(11) NOT NULL,
  `data_retirada` datetime DEFAULT current_timestamp(),
  `data_devolucao` datetime NOT NULL,
  `observacao` text DEFAULT NULL,
  PRIMARY KEY (`id_mov`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_ferramentas` (`id_ferramentas`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_rfid_tags`
--

DROP TABLE IF EXISTS `tb_rfid_tags`;
CREATE TABLE IF NOT EXISTS `tb_rfid_tags` (
  `id_tag` int(11) NOT NULL AUTO_INCREMENT,
  `codigo_tag` varchar(100) NOT NULL,
  `id_ferramenta` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_tag`),
  UNIQUE KEY `codigo_tag` (`codigo_tag`),
  KEY `id_ferramenta` (`id_ferramenta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_usuario`
--

DROP TABLE IF EXISTS `tb_usuario`;
CREATE TABLE IF NOT EXISTS `tb_usuario` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `usuario` varchar(70) NOT NULL,
  `email` varchar(255) NOT NULL,
  `cpf` varchar(25) NOT NULL,
  `telefone` varchar(30) NOT NULL,
  `cargo` varchar(100) DEFAULT NULL,
  `matricula` varchar(50) DEFAULT NULL,
  `senha` varchar(255) DEFAULT NULL,
  `data_cadastro` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('em atividade','desligado','','') NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `matricula` (`matricula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RestriÃ§Ãµes para tabelas despejadas
--

--
-- RestriÃ§Ãµes para tabelas `tb_ferramentas`
--
ALTER TABLE `tb_ferramentas`
  ADD CONSTRAINT `tb_ferramentas_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `tb_categorias` (`id_categoria`);

--
-- RestriÃ§Ãµes para tabelas `tb_movimentacoes`
--
ALTER TABLE `tb_movimentacoes`
  ADD CONSTRAINT `tb_movimentacoes_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `tb_usuario` (`id_usuario`),
  ADD CONSTRAINT `tb_movimentacoes_ibfk_2` FOREIGN KEY (`id_ferramentas`) REFERENCES `tb_ferramentas` (`id_ferramentas`);

--
-- RestriÃ§Ãµes para tabelas `tb_rfid_tags`
--
ALTER TABLE `tb_rfid_tags`
  ADD CONSTRAINT `tb_rfid_tags_ibfk_1` FOREIGN KEY (`id_ferramenta`) REFERENCES `tb_ferramentas` (`id_ferramentas`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
