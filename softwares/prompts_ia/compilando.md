# Guia para Compilação do Neura AI com PyInstaller

Este guia explica como transformar o aplicativo Neura AI em um executável standalone usando PyInstaller.

## Requisitos Prévios

- Python 3.7 ou superior instalado
- Todas as dependências do projeto instaladas
- PyInstaller instalado (`pip install pyinstaller`)

## Estrutura de Arquivos Necessária

Antes de compilar, certifique-se de que os seguintes arquivos estão presentes no diretório do projeto:

```
neura_ai/
├── app.py                # Arquivo principal do aplicativo
├── run.py                # Script de inicialização
├── requirements.txt      # Lista de dependências
├── .gitignore            # Arquivos a serem ignorados
└── README.md             # Documentação
```

## Passos para Compilação

1. **Instale o PyInstaller** (se ainda não estiver instalado):

```bash
pip install pyinstaller
```

2. **Navegue até o diretório do projeto**:

```bash
cd caminho/para/neura_ai
```

3. **Execute o comando PyInstaller**:

**Para Windows:**
```bash
pyinstaller --onefile --windowed --icon=app_icon.ico --name="Neura AI" run.py
```

**Para macOS:**
```bash
pyinstaller --onefile --windowed --icon=app_icon.icns --name="Neura AI" run.py
```

**Para Linux:**
```bash
pyinstaller --onefile --name="Neura AI" run.py
```

4. **Parâmetros importantes**:
   - `--onefile`: Cria um único arquivo executável
   - `--windowed`: Evita que o console seja exibido (melhor para aplicações GUI)
   - `--icon`: Define um ícone para o executável (opcional)
   - `--name`: Define o nome do executável resultante

## Localização do Executável

Após a compilação bem-sucedida, o executável será encontrado em:

```
neura_ai/dist/Neura AI.exe     # Windows
neura_ai/dist/Neura AI.app     # macOS
neura_ai/dist/Neura AI         # Linux
```

## Solução de Problemas Comuns

### Erro de Módulos Ausentes

Se você receber erros sobre módulos ausentes, você pode especificar importações ocultas:

```bash
pyinstaller --onefile --windowed --hidden-import=PIL._tkinter_finder --name="Neura AI" run.py
```

### Arquivos Estáticos Ausentes

Se arquivos como imagens ou configurações estiverem ausentes no executável, use o parâmetro `--add-data`:

```bash
pyinstaller --onefile --windowed --add-data="app_icon.png:." --name="Neura AI" run.py
```

### Compatibilidade com Tkinter

Para garantir que o Tkinter seja corretamente empacotado:

```bash
pyinstaller --onefile --windowed --hidden-import=tkinter --hidden-import=tkinter.ttk --name="Neura AI" run.py
```

## Teste do Executável

Sempre teste o executável em um ambiente limpo para garantir que todas as dependências foram corretamente empacotadas.

## Distribuição

O executável gerado pode ser distribuído para usuários finais sem a necessidade de Python instalado em seus sistemas.

**Nota**: Dependendo do sistema operacional de destino, você pode precisar de ferramentas adicionais para criar instaladores adequados (como Inno Setup para Windows ou DMG Creator para macOS).