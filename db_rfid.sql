-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 11/11/2025 às 17:18
-- Versão do servidor: 10.4.28-MariaDB
-- Versão do PHP: 8.2.4

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

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_categorias`
--

CREATE TABLE `tb_categorias` (
  `id_categoria` int(11) NOT NULL,
  `nome_categoria` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_ferramentas`
--

CREATE TABLE `tb_ferramentas` (
  `id_ferramentas` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `descricao` text DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `status` enum('disponível','emprestada','manutenção') DEFAULT 'disponível'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_movimentacoes`
--

CREATE TABLE `tb_movimentacoes` (
  `id_mov` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_ferramentas` int(11) NOT NULL,
  `data_retirada` datetime DEFAULT current_timestamp(),
  `data_devolucao` datetime NOT NULL,
  `observacao` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_rfid_tags`
--

CREATE TABLE `tb_rfid_tags` (
  `id_tag` int(11) NOT NULL,
  `codigo_tag` varchar(100) NOT NULL,
  `id_ferramenta` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_usuario`
--

CREATE TABLE `tb_usuario` (
  `id_usuario` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `cargo` varchar(100) DEFAULT NULL,
  `matricula` varchar(50) DEFAULT NULL,
  `senha` varchar(255) DEFAULT NULL,
  `data_cadastro` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `tb_categorias`
--
ALTER TABLE `tb_categorias`
  ADD PRIMARY KEY (`id_categoria`);

--
-- Índices de tabela `tb_ferramentas`
--
ALTER TABLE `tb_ferramentas`
  ADD PRIMARY KEY (`id_ferramentas`),
  ADD KEY `id_categoria` (`id_categoria`);

--
-- Índices de tabela `tb_movimentacoes`
--
ALTER TABLE `tb_movimentacoes`
  ADD PRIMARY KEY (`id_mov`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_ferramentas` (`id_ferramentas`);

--
-- Índices de tabela `tb_rfid_tags`
--
ALTER TABLE `tb_rfid_tags`
  ADD PRIMARY KEY (`id_tag`),
  ADD UNIQUE KEY `codigo_tag` (`codigo_tag`),
  ADD KEY `id_ferramenta` (`id_ferramenta`);

--
-- Índices de tabela `tb_usuario`
--
ALTER TABLE `tb_usuario`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `matricula` (`matricula`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `tb_categorias`
--
ALTER TABLE `tb_categorias`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `tb_ferramentas`
--
ALTER TABLE `tb_ferramentas`
  MODIFY `id_ferramentas` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `tb_movimentacoes`
--
ALTER TABLE `tb_movimentacoes`
  MODIFY `id_mov` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `tb_rfid_tags`
--
ALTER TABLE `tb_rfid_tags`
  MODIFY `id_tag` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `tb_usuario`
--
ALTER TABLE `tb_usuario`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restrições para tabelas despejadas
--

--
-- Restrições para tabelas `tb_ferramentas`
--
ALTER TABLE `tb_ferramentas`
  ADD CONSTRAINT `tb_ferramentas_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `tb_categorias` (`id_categoria`);

--
-- Restrições para tabelas `tb_movimentacoes`
--
ALTER TABLE `tb_movimentacoes`
  ADD CONSTRAINT `tb_movimentacoes_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `tb_usuario` (`id_usuario`),
  ADD CONSTRAINT `tb_movimentacoes_ibfk_2` FOREIGN KEY (`id_ferramentas`) REFERENCES `tb_ferramentas` (`id_ferramentas`);

--
-- Restrições para tabelas `tb_rfid_tags`
--
ALTER TABLE `tb_rfid_tags`
  ADD CONSTRAINT `tb_rfid_tags_ibfk_1` FOREIGN KEY (`id_ferramenta`) REFERENCES `tb_ferramentas` (`id_ferramentas`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
