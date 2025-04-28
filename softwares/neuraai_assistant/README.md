# Documentação do Sistema Neura AI: Assistente Inteligente com Interface Futurista

## Índice
- [Introdução](#introdução)
- [Requisitos do Sistema](#requisitos-do-sistema)
- [Instalação](#instalação)
- [Interface de Usuário](#interface-de-usuário)
- [Menu Principal](#menu-principal)
- [Como Utilizar o Sistema](#como-utilizar-o-sistema)
- [Solução de Problemas](#solução-de-problemas)
- [Atalhos de Teclado](#atalhos-de-teclado)
- [Recursos Adicionais](#recursos-adicionais)
- [Considerações Finais](#considerações-finais)

## Introdução

Neura AI é um sistema desktop avançado desenvolvido em Python com Tkinter que integra a API do Dify para criar uma interface de chatbot inteligente, moderna e de fácil utilização. Esta documentação fornece instruções detalhadas sobre como instalar, configurar e utilizar todas as funcionalidades do sistema.

## Requisitos do Sistema

- Python 3.7 ou superior
- Conexão com internet
- Bibliotecas Python:
  - requests
  - Pillow (PIL)
  - tkinter
  - python-dotenv
  - reportlab (opcional, para exportação de PDF)

## Instalação

1. **Preparação do ambiente:**
   ```
   mkdir neura_ai
   cd neura_ai
   ```

2. **Instalação das dependências:**
   ```
   pip install -r requirements.txt
   ```

3. **Execução do aplicativo:**
   ```
   python app.py
   ```

## Interface de Usuário

A interface do Neura AI é dividida em várias seções principais:

### Barra Superior
- **Título**: Exibe o nome "NEURA AI" no canto superior esquerdo
- **Indicador de Status**: Mostra o status de conexão com a API ("Conectado" ou "Desconectado")
- **Botões de Controle**:
  - **Nova Conversa**: Inicia uma nova sessão de chat
  - **Configurações** (⚙️): Abre o menu de configurações
  - **Ajuda** (?): Acessa a documentação e ajuda

### Barra de Ferramentas
- **Salvar** (💾): Salva a conversa atual em arquivo de texto
- **Exportar** (📤): Exporta a conversa como PDF
- **Limpar** (🗑️): Limpa a janela de chat atual
- **Voz** (🔇/🔊): Ativa/desativa recursos de voz (experimental)
- **Tema** (🌓): Alterna entre modos claro e escuro
- **API Info**: Exibe informações sobre a conexão com a API

### Área de Chat
- Exibe todas as mensagens trocadas entre o usuário e o assistente
- As mensagens são formatadas por cores:
  - **Usuário**: Azul
  - **Assistente**: Verde
  - **Sistema**: Cinza
  - **Erro**: Vermelho

### Área de Entrada
- Campo de texto para digitar suas mensagens
- Botão de envio (➤): Envia a mensagem para a API

### Barra de Status
- Exibe o estado atual do aplicativo
- Mostra o contador de palavras da mensagem sendo digitada
- Exibe créditos e informações adicionais

## Menu Principal

O Neura AI possui um menu completo com várias funcionalidades:

### Menu Arquivo
- **Nova Conversa** (Ctrl+N): Inicia uma nova sessão de chat
- **Salvar Conversa** (Ctrl+S): Salva o histórico atual
- **Exportar como PDF**: Gera um arquivo PDF da conversa
- **Sair** (Alt+F4): Fecha o aplicativo

### Menu Editar
- **Copiar** (Ctrl+C): Copia texto selecionado
- **Colar** (Ctrl+V): Cola texto no campo de entrada
- **Limpar Chat**: Apaga todas as mensagens da tela

### Menu Visualizar
- **Alternar Modo Escuro**: Troca entre temas claro e escuro
- **Aumentar/Diminuir Fonte**: Ajusta o tamanho do texto
- **Histórico de Conversas**: Exibe conversas salvas anteriormente

### Menu Ferramentas
- **Configurações**: Permite personalizar o aplicativo
- **Estatísticas da Conversa**: Mostra métricas sobre o uso
- **Verificar API**: Testa a conexão com o servidor Dify

### Menu Ajuda
- **Documentação**: Exibe esta documentação
- **Sobre**: Informações sobre o aplicativo
- **Verificar Atualizações**: Busca por novas versões

## Como Utilizar o Sistema

### Iniciando uma Conversa

1. Ao abrir o aplicativo, você verá uma mensagem de boas-vindas do assistente
2. Digite sua mensagem na caixa de texto na parte inferior
3. Pressione Enter ou clique no botão de envio (➤) para enviar
4. O assistente processará sua mensagem e enviará uma resposta
5. Use Shift+Enter se desejar criar uma nova linha sem enviar a mensagem

### Gerenciando Conversas

- **Iniciar Nova Conversa**: Clique no botão "Nova Conversa" ou use Ctrl+N
- **Salvar Conversa**: Clique no botão 💾 ou use Ctrl+S para salvar como arquivo de texto
- **Exportar como PDF**: Clique no botão 📤 para criar um documento PDF formatado
- **Limpar Chat**: Clique no botão 🗑️ para limpar a tela (mantém o contexto da conversa)

### Configurações do Sistema

Para personalizar o Neura AI:

1. Clique no botão ⚙️ ou acesse Menu > Ferramentas > Configurações
2. A janela de configurações possui três abas:
   - **API**: Configure sua chave API e URL do Dify
   - **Interface**: Ajuste o modo escuro e tamanho da fonte
   - **Avançado**: Defina o timeout da API e outras opções

### Modos de Visualização

- **Modo Claro/Escuro**: Alterne entre temas clicando no botão 🌓
- **Tamanho da Fonte**: Ajuste usando Menu > Visualizar > Aumentar/Diminuir Fonte

### Recursos Avançados

- **Estatísticas**: Acesse Menu > Ferramentas > Estatísticas para ver métricas da conversa atual
- **Histórico**: Gerencie conversas salvas através de Menu > Visualizar > Histórico de Conversas
- **Exportação**: Salve suas conversas em diferentes formatos para referência futura

## Solução de Problemas

### Erro 404 na API

**Problema**: Mensagem "Erro na comunicação com a API. Código: 404"  
**Solução**:
1. Verifique as configurações da API em Menu > Ferramentas > Configurações > aba API
2. Certifique-se de que a URL esteja correta: `https://api.dify.ai/v1/chat-messages`
3. Verifique sua conexão com a internet

### Erro 401 (Não Autorizado)

**Problema**: Mensagem de erro de autenticação  
**Solução**:
1. Verifique se a chave API está correta nas configurações
2. Confirme se sua chave API é válida no painel do Dify
3. Gere uma nova chave API se necessário

### Aplicativo Não Responde

**Problema**: Interface congelada ou lenta  
**Solução**:
1. Reinicie o aplicativo
2. Verifique sua conexão com a internet
3. Limpe o cache em Configurações > Avançado > Limpar Cache

## Atalhos de Teclado

| Atalho | Função |
|--------|--------|
| Ctrl+N | Nova conversa |
| Ctrl+S | Salvar conversa |
| Ctrl+C | Copiar texto selecionado |
| Ctrl+V | Colar texto |
| F1 | Abrir ajuda |
| F5 | Verificar conexão com a API |
| Enter | Enviar mensagem |
| Shift+Enter | Inserir quebra de linha |

## Recursos Adicionais

### Exportação de Histórico

O Neura AI permite exportar conversas em diferentes formatos:

- **Texto (.txt)**: Formato básico, preserva todo o conteúdo da conversa
- **PDF (.pdf)**: Documento formatado com estilos por tipo de mensagem
- **CSV (.csv)**: Formato tabulado para análise em planilhas (via estatísticas)

### Personalização

O sistema pode ser personalizado de várias formas:

- **Temas**: Alternância entre modos claro e escuro
- **Fontes**: Ajuste do tamanho do texto para melhor visualização
- **API**: Configuração personalizada da conexão com o Dify
- **Interface**: Ajustes visuais para preferências pessoais

## Considerações Finais

O Neura AI foi projetado para oferecer uma experiência de usuário intuitiva e moderna para interação com assistentes de IA. Esta documentação cobre as funcionalidades principais, mas o sistema continua em desenvolvimento, com novos recursos sendo adicionados regularmente.

Para obter suporte adicional, utilize o recurso de ajuda interno do aplicativo acessando o botão de ajuda (?) ou pressionando F1.