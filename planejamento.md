# 📘 Planejamento Geral — Projeto Controle de Estoque RFID

## 🧭 Visão Geral do Projeto
O **Controle de Estoque via RFID** tem como objetivo automatizar e centralizar o gerenciamento de ferramentas e materiais, permitindo a detecção de movimentações em tempo real, registro histórico e controle de permissões de acesso.  
O projeto nasceu no curso Técnico em Desenvolvimento de Sistemas do SENAI e visa evoluir para um **produto comercial escalável**, com integração entre hardware RFID, software desktop, app mobile e painel web.

---

## 👥 Equipe Principal
- **Rafael Bressan Fiorio** — Programador, Desenvolvedor Web/Desktop/Mobile, Documentador, Líder do Projeto, Montador do Circuito, Pesquisador
- **Thiago Mattei Sartor** — Programador, Desenvolvedor Mobile/Desktop, Montador de Circuito e Pesquisador  
- **Gustavo Feyh Zibetti** — Responsável pelo Banco de dados e sua integração, Pesquisador, Montador de Circuito

---

## 🧱 FASE 1 — Integração e Robustez do Sistema

### 🎯 Objetivos
- Unificar hardware, software e banco de dados em um único ecossistema.  
- Garantir comunicação estável e confiável entre RFID e banco de dados.  
- Criar base sólida para expansão futura (Java + SQL).

### 🔧 Etapas Técnicas
1. **Integração Python ↔ Banco MySQL**
   - Identificação e cadastro de tags
   - Leitura das tags UHF e gravação automática das movimentações.
   - Registro com data, hora, local

2. **Associação de Tags RFID às Ferramentas**
   - Interface para vincular tags a ferramentas cadastradas.
   - Sincronização automática no banco.

3. **Controle de Usuários e Permissões**
   - Tabela com autenticação segura e níveis de acesso (Admin e Funcionário).
   **Administrador**
	- Cadastra e gerencia Funcionários
	- Acesso a relatórios
	- Acesso a tabela de associação de ferramentas
	- Acesso a log de movimentações

4. **Monitoramento Local**
   - Interface em Python (CustomTkinter) para visualização de leituras em tempo real.
   - Logs de movimentação por sala (Ferramentas / Tornos).

---

## ☁️ FASE 2 — Desenvolvimento do Sistema Java

### 🎯 Objetivos
Transformar o controle de estoque em um **software desktop profissional**, conectado ao banco central e preparado para integração com aplicativos móveis e web.

### 🧩 Estrutura do Sistema Java (Desktop)
- **Tecnologias:** JavaFX, JDBC, MySQL, iTextPDF, SceneBuilder
- **Arquitetura:** MVC (Model–View–Controller)

### 🖥️ Módulos Principais
1. **Login e Controle de Acesso**
2. **Dashboard com gráficos e alertas**
3. **Cadastro de Ferramentas e Categorias**
4. **Associação de Tags RFID**
5. **Histórico e Movimentações**
6. **Cadastro de Usuários**
7. **Relatórios (PDF e CSV)**
8. **Configurações do Sistema**

### 💡 Funcionalidades Avançadas
- Sincronização automática com leitor RFID.
- Alerta de movimentação não autorizada.
- Exportação de relatórios e backup automático.
- Interface responsiva com modo escuro.

### 🔗 Comunicação com RFID
- O script Python continuará responsável pela leitura serial.
- O software Java consultará o banco MySQL para atualizar o status em tempo real.

---

## 📱 FASE 3 — Aplicativo Mobile Android

### 🎯 Objetivo
Permitir acesso rápido às informações do estoque, notificações de movimentação e relatórios diretamente no celular.

### 🧩 Estrutura do App
- **Linguagem:** Java/Kotlin (Android Studio)
- **Banco:** API REST conectada ao mesmo MySQL
- **Funcionalidades:**
  - Login e autenticação
  - Visualização de ferramentas e status
  - Notificações push para movimentações
  - Consulta de histórico e relatórios
  - QR Code para identificar ferramentas rapidamente

---

## 🌐 FASE 4 — Site da Empresa

### 🎯 Objetivos
- Mostrar profissionalismo e viabilizar a venda do produto.

### 🧩 Estrutura do Site
- **Seções:**
  - Página inicial (apresentação do produto)
  - Demonstração do painel RFID em tempo real
  - Login e acesso ao painel online
  - Contato e suporte técnico

### 💼 Site Institucional da Empresa
**Domínio sugerido:** `rfidcontrole.com.br`  
**Páginas:**
1. Início — apresentação da empresa e missão
2. Produto — descrição do sistema e diferenciais
3. Equipe — perfil dos fundadores e funções
4. Contato — formulário e canais de suporte
5. Blog — publicações sobre tecnologia e RFID

---

## 💼 FASE 5 — Produto Comercial e Escalabilidade

### 🎯 Objetivo
Transformar o projeto em um **produto vendável e escalável** para escolas, indústrias e oficinas.

### 💰 Modelos de Negócio
| **Licença Local (Desktop)** | Instalação única com suporte técnico. |
| **Personalizado para Indústria** | Adaptação sob demanda com integração ERP. |

### 📦 Pacote Comercial
- Kit de instalação (leitor RFID, etiquetas, software)
- Manual técnico e de uso
- Treinamento básico remoto
- Suporte via e-mail e WhatsApp

---

## 🚀 FASE 6 — Futuras Expansões

### 💡 Ideias
- Inventário automático via múltiplos leitores.
- Reconhecimento facial + RFID para autenticação dupla.
- Painel de controle com IA para detectar padrões de uso.
- Módulo de manutenção preventiva (alertas de desgaste).
- Integração com assistentes virtuais (voz).

---

## 🧠 Considerações Finais
Este planejamento consolida o **Controle de Estoque RFID** como um projeto com potencial real de mercado.  
Com base sólida em hardware, software e integração de sistemas, o grupo poderá transformar a ideia inicial da mostra científica em um **produto tecnológico completo e vendável**.

**Próximo passo:** iniciar a fase de integração entre o Python (RFID) e o banco de dados para que o Java possa se conectar em tempo real.
