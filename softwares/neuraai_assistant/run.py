import os
import sys
import subprocess
import platform
import time

def show_splash():
    """Exibe uma tela de splash no terminal"""
    splash_text = """
    ███╗   ██╗███████╗██╗   ██╗██████╗  █████╗      █████╗ ██╗
    ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔══██╗    ██╔══██╗██║
    ██╔██╗ ██║█████╗  ██║   ██║██████╔╝███████║    ███████║██║
    ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██╔══██║    ██╔══██║██║
    ██║ ╚████║███████╗╚██████╔╝██║  ██║██║  ██║    ██║  ██║██║
    ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝
                                                            
    Assistente Inteligente Futurista
    Iniciando...
    """
    print(splash_text)
    time.sleep(1)  # Exibir splash por 1 segundo

def create_directories():
    """Cria diretórios necessários para o aplicativo"""
    directories = ["histórico", "cache", "tmp"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Diretório '{directory}' criado.")

def is_frozen():
    """Verifica se estamos executando como um executável PyInstaller"""
    return getattr(sys, 'frozen', False)

def get_application_path():
    """Obtém o diretório raiz da aplicação"""
    if is_frozen():
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def check_basic_requirements():
    """Verifica requisitos básicos para execução"""
    try:
        import tkinter
        print("Tkinter disponível.")
        return True
    except ImportError:
        show_error_message("Tkinter não está instalado. Este componente é necessário para executar o aplicativo.")
        return False

def show_error_message(message):
    """Exibe uma mensagem de erro"""
    print(f"ERRO: {message}")
    try:
        if platform.system() == "Windows":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, "Erro - Neura AI", 0)
        else:
            input("\nErro encontrado. Pressione Enter para fechar...")
    except:
        input("\nErro encontrado. Pressione Enter para fechar...")

def launch_app():
    """Inicia o aplicativo principal"""
    print("Iniciando aplicativo...")
    
    # Definir diretório de trabalho
    os.chdir(get_application_path())
    
    try:
        # Importar o módulo app e iniciar a interface gráfica
        import app
        
        # Verificar se existe a função main
        if hasattr(app, 'main'):
            app.main()
        # Verificar se existe a classe FuturisticChatBot
        elif hasattr(app, 'FuturisticChatBot'):
            import tkinter as tk
            root = tk.Tk()
            chat_app = app.FuturisticChatBot(root)
            root.mainloop()
        else:
            show_error_message("Não foi possível iniciar o aplicativo. Estrutura de código não reconhecida.")
    
    except ImportError as e:
        show_error_message(f"Não foi possível importar o módulo principal: {str(e)}")
    except Exception as e:
        show_error_message(f"Erro ao iniciar o aplicativo: {str(e)}")

def main():
    """Função principal"""
    # Exibir splash
    show_splash()
    
    # Verificar requisitos básicos
    if not check_basic_requirements():
        return
    
    # Criar diretórios necessários
    create_directories()
    
    # Iniciar o aplicativo
    launch_app()

if __name__ == "__main__":
    main()