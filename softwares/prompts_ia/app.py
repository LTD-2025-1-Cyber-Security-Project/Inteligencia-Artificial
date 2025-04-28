import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog, Menu
import requests
import threading
import json
import os
import re
import time
import datetime
import webbrowser
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import io
import base64
import platform
import random
import sys

class NeoMorphicButton(tk.Canvas):
    """Classe personalizada para criar botões com estilo neomórfico"""
    def __init__(self, parent, width, height, text="", command=None, radius=10, color="#f0f0f0", **kwargs):
        super().__init__(parent, width=width, height=height, bg=color, highlightthickness=0, **kwargs)
        self.color = color
        self.radius = radius
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.state = "normal"
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw()
    
    def draw(self):
        self.delete("all")
        
        if self.state == "normal":
            # Sombra externa escura (parte inferior direita)
            self.create_rectangle(
                self.radius, self.radius,
                self.width - self.radius, self.height - self.radius,
                fill=self.color, outline="", tags="shadow"
            )
            
            # Borda arredondada
            self.create_rounded_rectangle(
                0, 0, self.width, self.height, 
                self.radius, fill=self.color, outline="#e0e0e0"
            )
            
            # Sombra clara (parte superior esquerda)
            self.create_line(
                self.radius, self.radius, 
                self.width - self.radius, self.radius,
                fill="#ffffff", width=1
            )
            self.create_line(
                self.radius, self.radius,
                self.radius, self.height - self.radius,
                fill="#ffffff", width=1
            )
            
            # Sombra escura (parte inferior direita)
            self.create_line(
                self.width - self.radius, self.radius,
                self.width - self.radius, self.height - self.radius,
                fill="#d0d0d0", width=1
            )
            self.create_line(
                self.radius, self.height - self.radius,
                self.width - self.radius, self.height - self.radius,
                fill="#d0d0d0", width=1
            )
        elif self.state == "hover":
            # Efeito hover - sombra mais suave
            self.create_rounded_rectangle(
                0, 0, self.width, self.height, 
                self.radius, fill=self.color, outline="#e8e8e8"
            )
        else:  # pressed
            # Efeito pressionado - invertendo sombras
            self.create_rounded_rectangle(
                0, 0, self.width, self.height, 
                self.radius, fill=self.color, outline="#d0d0d0"
            )
            
            # Sombra interna
            self.create_line(
                self.radius, self.radius,
                self.width - self.radius, self.radius,
                fill="#d0d0d0", width=1
            )
            self.create_line(
                self.radius, self.radius,
                self.radius, self.height - self.radius,
                fill="#d0d0d0", width=1
            )
        
        # Texto centralizado
        text_color = "#555555" if self.state != "pressed" else "#333333"
        x_offset = 1 if self.state == "pressed" else 0
        y_offset = 1 if self.state == "pressed" else 0
        
        self.create_text(
            self.width // 2 + x_offset, 
            self.height // 2 + y_offset, 
            text=self.text, 
            fill=text_color,
            font=("Segoe UI", 10, "bold")
        )
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)
    
    def on_enter(self, event):
        if self.state != "pressed":
            self.state = "hover"
            self.draw()
    
    def on_leave(self, event):
        if self.state != "pressed":
            self.state = "normal"
            self.draw()
    
    def on_press(self, event):
        self.state = "pressed"
        self.draw()
    
    def on_release(self, event):
        self.state = "normal"
        self.draw()
        if self.command:
            self.command()


class CustomScrollbar(ttk.Scrollbar):
    """Classe para criar uma scrollbar personalizada"""
    def set(self, low, high):
        if float(low) <= 0.0 and float(high) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        ttk.Scrollbar.set(self, low, high)


class BlurredFrame(tk.Frame):
    """Frame com efeito de blur para destacar elementos"""
    def __init__(self, parent, blur_radius=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.blur_radius = blur_radius
        
        # Configurar cores e bordas
        bg_color = kwargs.get("bg", "#f5f5f5")
        self.configure(bg=bg_color)
        self.bind("<Configure>", self.update_appearance)
    
    def update_appearance(self, event=None):
        width, height = self.winfo_width(), self.winfo_height()
        if width > 1 and height > 1:  # Evitar dimensões inválidas
            # Criar uma imagem base
            base = Image.new("RGBA", (width, height), self["bg"])
            
            # Aplicar blur
            blurred = base.filter(ImageFilter.GaussianBlur(self.blur_radius))
            
            # Criar ImageTk
            self.img = ImageTk.PhotoImage(blurred)
            
            # Definir imagem de fundo usando canvas ou label
            if not hasattr(self, "bg_label"):
                self.bg_label = tk.Label(self, image=self.img, bg=self["bg"])
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                self.bg_label.configure(image=self.img)


class PulsingButton(tk.Canvas):
    """Botão com efeito pulsante para elementos interativos"""
    def __init__(self, parent, width, height, text="", command=None, color="#4a86e8", **kwargs):
        # Obter a cor de fundo do parent, se for um Frame ttk, use um valor padrão
        if isinstance(parent, ttk.Frame):
            bg_color = "#f0f0f0"  # Valor padrão para ttk.Frame
        else:
            try:
                bg_color = parent["bg"]
            except:
                bg_color = "#f0f0f0"  # Valor padrão se não conseguir acessar bg
        
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=bg_color, **kwargs)
        self.width = width
        self.height = height
        self.text = text
        self.command = command
        self.color = color
        self.pulsing = False
        self.pulse_amount = 0
        self.growing = True
        
        self.bind("<Enter>", self.start_pulse)
        self.bind("<Leave>", self.stop_pulse)
        self.bind("<Button-1>", self.on_click)
        
        self.draw()
    
    def draw(self):
        self.delete("all")
        
        # Determinar tamanho atual com base na pulsação
        w_offset = self.pulse_amount if self.pulsing else 0
        h_offset = self.pulse_amount if self.pulsing else 0
        
        # Criar botão oval
        self.create_oval(
            2, 2, 
            self.width - 2 - w_offset, 
            self.height - 2 - h_offset,
            fill=self.color, outline=""
        )
        
        # Adicionar texto
        self.create_text(
            (self.width - w_offset) // 2,
            (self.height - h_offset) // 2,
            text=self.text,
            fill="white",
            font=("Segoe UI", 11, "bold")
        )
    
    def start_pulse(self, event=None):
        self.pulsing = True
        self._pulse()
    
    def _pulse(self):
        if not self.pulsing:
            return
        
        if self.growing:
            self.pulse_amount += 0.2
            if self.pulse_amount >= 4:
                self.growing = False
        else:
            self.pulse_amount -= 0.2
            if self.pulse_amount <= 0:
                self.growing = True
        
        self.draw()
        self.after(50, self._pulse)
    
    def stop_pulse(self, event=None):
        self.pulsing = False
        self.pulse_amount = 0
        self.growing = True
        self.draw()
    
    def on_click(self, event=None):
        if self.command:
            self.command()


class FuturisticChatBot:
    def __init__(self, root):
        # Configuração da API do Dify
        self.API_KEY = "app-MUYoCNvT2EhVO88Hm9o3Oylm"
        self.API_URL = "https://api.dify.ai/v1/chat-messages"
        self.stream_API_URL = "https://api.dify.ai/v1/chat-messages:stream"
        self.conversation_id = None
        self.user_input = ""
        self.history = []
        self.api_request_in_progress = False
        self.api_reconnect_attempts = 0
        self.MAX_RECONNECT_ATTEMPTS = 3
        self.thinking_animation_id = None
        self.voice_active = False
        self.dark_mode = False

        # Sistema operacional
        self.os_name = platform.system()
        
        # Configuração da interface gráfica
        self.root = root
        self.root.title("Neura AI - Assistente Inteligente Futurista")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Variáveis do sistema
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto para conversar")
        self.connection_status = tk.StringVar()
        self.connection_status.set("Desconectado")
        self.word_count = tk.StringVar()
        self.word_count.set("0 palavras")
        
        # Configurar estilos
        self.configure_style()
        
        # Configurar o layout principal
        self.setup_layout()
                
        # Carregar configurações
        self.load_settings()
        
        # Iniciar nova conversa
        self.new_conversation()
        
        # Verificar conexão com a API
        self.check_api_connection()

    def configure_style(self):
        """Configura os estilos da interface gráfica com tema futurista"""
        # Cores principais
        self.colors = {
            "bg_primary": "#f8f9fa",
            "bg_secondary": "#f1f3f4",
            "bg_tertiary": "#e8eaed",
            "accent": "#4285f4",  # Azul Google
            "accent_dark": "#3367d6",
            "text_primary": "#202124",
            "text_secondary": "#5f6368",
            "success": "#34a853",  # Verde Google
            "warning": "#fbbc05",  # Amarelo Google
            "error": "#ea4335",    # Vermelho Google
            "border": "#dadce0",
            "highlight": "#e8f0fe",
            "user_msg_bg": "#e3f2fd",  # Azul claro para mensagens do usuário
            "bot_msg_bg": "#f1f8e9",   # Verde claro para mensagens do bot
            "system_msg_bg": "#f5f5f5"  # Cinza claro para mensagens do sistema
        }
        
        # Configuração de cores
        self.root.configure(bg=self.colors["bg_primary"])
        
        # Configurar estilo ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilos para os widgets
        style.configure("TFrame", background=self.colors["bg_primary"])
        style.configure("Secondary.TFrame", background=self.colors["bg_secondary"])
        style.configure("TButton", font=('Segoe UI', 10), background=self.colors["accent"], foreground="white")
        style.configure("Secondary.TButton", font=('Segoe UI', 9), background=self.colors["bg_secondary"])
        style.configure("TLabel", font=('Segoe UI', 10), background=self.colors["bg_primary"], foreground=self.colors["text_primary"])
        style.configure("Header.TLabel", font=('Segoe UI', 14, 'bold'), background=self.colors["bg_primary"], foreground=self.colors["text_primary"])
        style.configure("Status.TLabel", font=('Segoe UI', 9), foreground=self.colors["text_secondary"], background=self.colors["bg_primary"])
        style.configure("Connected.TLabel", font=('Segoe UI', 9), foreground=self.colors["success"], background=self.colors["bg_primary"])
        style.configure("Disconnected.TLabel", font=('Segoe UI', 9), foreground=self.colors["error"], background=self.colors["bg_primary"])
        
        # Estilos para scrollbars
        style.configure("Custom.Vertical.TScrollbar", gripcount=0, background=self.colors["bg_tertiary"], darkcolor=self.colors["bg_tertiary"], 
                        lightcolor=self.colors["bg_tertiary"], troughcolor=self.colors["bg_primary"], bordercolor=self.colors["bg_primary"],
                        arrowcolor=self.colors["text_secondary"])

    def toggle_dark_mode(self):
        """Alterna entre modo claro e escuro"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Cores para modo escuro
            self.colors = {
                "bg_primary": "#202124",
                "bg_secondary": "#303134",
                "bg_tertiary": "#3c4043",
                "accent": "#8ab4f8",
                "accent_dark": "#669df6",
                "text_primary": "#e8eaed",
                "text_secondary": "#9aa0a6",
                "success": "#81c995",
                "warning": "#fdd663",
                "error": "#f28b82",
                "border": "#5f6368",
                "highlight": "#394457",
                "user_msg_bg": "#174ea6",  # Azul escuro para mensagens do usuário
                "bot_msg_bg": "#0d652d",   # Verde escuro para mensagens do bot
                "system_msg_bg": "#3c4043"  # Cinza escuro para mensagens do sistema
            }
        else:
            # Cores para modo claro
            self.colors = {
                "bg_primary": "#f8f9fa",
                "bg_secondary": "#f1f3f4",
                "bg_tertiary": "#e8eaed",
                "accent": "#4285f4",
                "accent_dark": "#3367d6",
                "text_primary": "#202124",
                "text_secondary": "#5f6368",
                "success": "#34a853",
                "warning": "#fbbc05",
                "error": "#ea4335",
                "border": "#dadce0",
                "highlight": "#e8f0fe",
                "user_msg_bg": "#e3f2fd",
                "bot_msg_bg": "#f1f8e9",
                "system_msg_bg": "#f5f5f5"
            }
        
        # Atualizar estilos
        self.update_styles()
        
        # Atualizar configurações
        self.save_settings({"dark_mode": self.dark_mode})

    def update_styles(self):
        """Atualiza os estilos conforme as cores atuais"""
        # Atualizar cor de fundo da janela principal
        self.root.configure(bg=self.colors["bg_primary"])
        
        # Atualizar estilo ttk
        style = ttk.Style()
        
        # Estilos para os widgets
        style.configure("TFrame", background=self.colors["bg_primary"])
        style.configure("Secondary.TFrame", background=self.colors["bg_secondary"])
        style.configure("TButton", background=self.colors["accent"], foreground="white")
        style.configure("Secondary.TButton", background=self.colors["bg_secondary"])
        style.configure("TLabel", background=self.colors["bg_primary"], foreground=self.colors["text_primary"])
        style.configure("Header.TLabel", background=self.colors["bg_primary"], foreground=self.colors["text_primary"])
        style.configure("Status.TLabel", foreground=self.colors["text_secondary"], background=self.colors["bg_primary"])
        style.configure("Connected.TLabel", foreground=self.colors["success"], background=self.colors["bg_primary"])
        style.configure("Disconnected.TLabel", foreground=self.colors["error"], background=self.colors["bg_primary"])
        
        # Atualizar fundo do frame principal
        self.main_frame.configure(style="TFrame")
        
        # Atualizar chat display
        self.chat_display.config(
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
        )
        
        # Reconfigurar tags de mensagem
        self.chat_display.tag_config('user', foreground=self.colors["accent"], background=self.colors["user_msg_bg"])
        self.chat_display.tag_config('bot', foreground=self.colors["text_primary"], background=self.colors["bot_msg_bg"])
        self.chat_display.tag_config('system', foreground=self.colors["text_secondary"], background=self.colors["system_msg_bg"])
        self.chat_display.tag_config('error', foreground=self.colors["error"], background=self.colors["system_msg_bg"])
        
        # Atualizar área de entrada do usuário
        self.user_input_box.config(
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["text_primary"]
        )
        
        # Atualizar barra de status
        self.status_frame.configure(style="TFrame")
        
        # Atualizar barra de ferramentas
        self.toolbar_frame.configure(style="TFrame")
        
        # Atualizar bordas de elementos
        for widget in [self.chat_display, self.user_input_box]:
            widget.config(highlightbackground=self.colors["border"])

    def setup_layout(self):
        """Configura o layout principal da aplicação com design futurista"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar menu
        self.setup_menu()
        
        # Frame superior - cabeçalho
        header_frame = ttk.Frame(self.main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo e título
        title_label = ttk.Label(header_frame, text="NEURA AI", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Status de conexão
        connection_indicator = ttk.Label(header_frame, textvariable=self.connection_status)
        connection_indicator.pack(side=tk.LEFT, padx=10)
        
        # Botões de controle
        control_frame = ttk.Frame(header_frame, style="TFrame")
        control_frame.pack(side=tk.RIGHT)
        
        # Botão de novo chat com estilo neomórfico
        new_chat_btn = NeoMorphicButton(
            control_frame, width=120, height=30, 
            text="Nova Conversa", command=self.new_conversation,
            color=self.colors["bg_secondary"]
        )
        new_chat_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão de configurações
        settings_btn = NeoMorphicButton(
            control_frame, width=30, height=30,
            text="⚙️", command=self.show_settings,
            color=self.colors["bg_secondary"]
        )
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão de ajuda
        help_btn = NeoMorphicButton(
            control_frame, width=30, height=30,
            text="?", command=self.show_help,
            color=self.colors["bg_secondary"]
        )
        help_btn.pack(side=tk.LEFT, padx=5)
        
        # Barra de ferramentas
        self.toolbar_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botões de ferramentas
        self.setup_toolbar()
        
        # Painel principal dividido
        panel_frame = ttk.Frame(self.main_frame, style="TFrame")
        panel_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de chat - área principal
        chat_frame = ttk.Frame(panel_frame, style="TFrame")
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Área de exibição das mensagens com estilo futurista
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, 
            font=('Segoe UI', 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            relief=tk.FLAT,
            padx=10, pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_display.config(state=tk.DISABLED)
        
        # Configurar tags para formatação de mensagens
        self.chat_display.tag_config('user', foreground=self.colors["accent"], background=self.colors["user_msg_bg"], 
                                    font=('Segoe UI', 10, 'bold'), lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_display.tag_config('bot', foreground=self.colors["text_primary"], background=self.colors["bot_msg_bg"],
                                    font=('Segoe UI', 10), lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_display.tag_config('system', foreground=self.colors["text_secondary"], background=self.colors["system_msg_bg"],
                                    font=('Segoe UI', 9, 'italic'), lmargin1=5, lmargin2=5)
        self.chat_display.tag_config('error', foreground=self.colors["error"], background=self.colors["system_msg_bg"],
                                    font=('Segoe UI', 9, 'bold'), lmargin1=5, lmargin2=5)
        self.chat_display.tag_config('thinking', foreground="#9e9e9e", background=self.colors["system_msg_bg"], 
                                    font=('Segoe UI', 9, 'italic'), lmargin1=5, lmargin2=5)
        
        # Frame de entrada do usuário com design moderno
        input_frame = ttk.Frame(self.main_frame, style="Secondary.TFrame")
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Área de entrada de texto com estilo melhorado
        self.user_input_box = scrolledtext.ScrolledText(
            input_frame, height=4, 
            font=('Segoe UI', 11),
            wrap=tk.WORD,
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["text_primary"],
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            relief=tk.FLAT,
            padx=10, pady=10
        )
        self.user_input_box.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 10))
        self.user_input_box.bind("<Return>", self.handle_return)
        self.user_input_box.bind("<Shift-Return>", lambda e: None)  # Permitir quebra de linha com Shift+Enter
        self.user_input_box.bind("<KeyRelease>", self.update_word_count)
        
        # Botão de envio animado
        send_button = PulsingButton(
            input_frame, width=50, height=50,
            text="➤", command=self.send_message,
            color=self.colors["accent"]
        )
        send_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Barra de status futurista
        status_frame = ttk.Frame(self.main_frame, style="TFrame")
        status_frame.pack(fill=tk.X)
        self.status_frame = status_frame
        
        # Status à esquerda
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        # Contador de palavras
        word_count_label = ttk.Label(status_frame, textvariable=self.word_count, style="Status.TLabel")
        word_count_label.pack(side=tk.LEFT, padx=15)
        
        # Créditos
        credits_label = ttk.Label(status_frame, text="Powered by Dify AI", style="Status.TLabel")
        credits_label.pack(side=tk.RIGHT)
        credits_label.bind("<Button-1>", lambda e: webbrowser.open("https://dify.ai"))

    def setup_menu(self):
        """Configura o menu principal"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Nova Conversa", command=self.new_conversation, accelerator="Ctrl+N")
        file_menu.add_command(label="Salvar Conversa", command=self.save_history, accelerator="Ctrl+S")
        file_menu.add_command(label="Exportar como PDF", command=self.export_as_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.destroy, accelerator="Alt+F4")
        
        # Menu Editar
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Copiar", command=self.copy_selected_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Colar", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_command(label="Limpar Chat", command=self.clear_chat)
        
        # Menu Visualizar
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizar", menu=view_menu)
        view_menu.add_command(label="Alternar Modo Escuro", command=self.toggle_dark_mode)
        view_menu.add_command(label="Aumentar Fonte", command=self.increase_font_size)
        view_menu.add_command(label="Diminuir Fonte", command=self.decrease_font_size)
        view_menu.add_separator()
        view_menu.add_command(label="Histórico de Conversas", command=self.show_history_window)
        
        # Menu Ferramentas
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Configurações", command=self.show_settings)
        tools_menu.add_command(label="Estatísticas da Conversa", command=self.show_conversation_stats)
        tools_menu.add_command(label="Verificar API", command=self.check_api_connection)
        
        # Menu Ajuda
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Documentação", command=self.show_help)
        help_menu.add_command(label="Sobre", command=self.show_about)
        help_menu.add_command(label="Verificar Atualizações", command=self.check_for_updates)
        
        # Registrar atalhos
        self.root.bind("<Control-n>", lambda e: self.new_conversation())
        self.root.bind("<Control-s>", lambda e: self.save_history())
        self.root.bind("<Control-c>", lambda e: self.copy_selected_text())
        self.root.bind("<Control-v>", lambda e: self.paste_text())
        self.root.bind("<F1>", lambda e: self.show_help())
        self.root.bind("<F5>", lambda e: self.check_api_connection())

    def setup_toolbar(self):
        """Configura a barra de ferramentas"""
        # Botões de ferramentas - usando frames normais para evitar problemas de bg
        tool_save = NeoMorphicButton(self.toolbar_frame, width=100, height=30, 
                                   text="💾 Salvar", command=self.save_history,
                                   color=self.colors["bg_secondary"])
        tool_save.pack(side=tk.LEFT, padx=5)
        
        tool_export = NeoMorphicButton(self.toolbar_frame, width=100, height=30, 
                                   text="📤 Exportar", command=self.export_as_pdf,
                                   color=self.colors["bg_secondary"])
        tool_export.pack(side=tk.LEFT, padx=5)
        
        tool_clear = NeoMorphicButton(self.toolbar_frame, width=100, height=30, 
                                   text="🗑️ Limpar", command=self.clear_chat,
                                   color=self.colors["bg_secondary"])
        tool_clear.pack(side=tk.LEFT, padx=5)
        
        # Separador
        separator_frame = tk.Frame(self.toolbar_frame, width=2, height=30, bg=self.colors["border"])
        separator_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Botão de ativar/desativar voz (futura implementação)
        self.voice_btn = NeoMorphicButton(self.toolbar_frame, width=100, height=30, 
                                       text="🔇 Voz", command=self.toggle_voice,
                                       color=self.colors["bg_secondary"])
        self.voice_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão de tema
        self.theme_btn = NeoMorphicButton(self.toolbar_frame, width=100, height=30, 
                                       text="🌓 Tema", command=self.toggle_dark_mode,
                                       color=self.colors["bg_secondary"])
        self.theme_btn.pack(side=tk.LEFT, padx=5)
        
        # Espaço flexível usando frame normal
        spacer = tk.Frame(self.toolbar_frame, bg=self.colors["bg_primary"])
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão de informações da API
        api_info = NeoMorphicButton(self.toolbar_frame, width=100, height=30, 
                                 text="API Info", command=self.show_api_info,
                                 color=self.colors["bg_secondary"])
        api_info.pack(side=tk.RIGHT, padx=5)

    def handle_return(self, event):
        """Gerencia o evento de pressionar Enter na caixa de entrada"""
        if not event.state & 0x1:  # Se Shift não estiver pressionado
            self.send_message()
            return 'break'  # Impede a inserção de nova linha
        return None  # Permite a inserção de nova linha com Shift+Enter

    def update_word_count(self, event=None):
        """Atualiza o contador de palavras na área de entrada"""
        text = self.user_input_box.get("1.0", tk.END).strip()
        words = len(re.findall(r'\b\w+\b', text))
        self.word_count.set(f"{words} palavra{'s' if words != 1 else ''}")

    def send_message(self):
        """Envia a mensagem do usuário para a API e exibe a resposta"""
        # Obter texto da entrada do usuário
        user_input = self.user_input_box.get("1.0", tk.END).strip()
        if not user_input:
            return
        
        # Cancelar qualquer animação de pensamento em andamento
        if self.thinking_animation_id:
            self.root.after_cancel(self.thinking_animation_id)
            self.thinking_animation_id = None
            self.chat_display.config(state=tk.NORMAL)
            try:
                self.chat_display.delete("thinking_tag_start", "thinking_tag_end")
            except tk.TclError:
                # Se as marcas não existirem, ignore
                pass
            self.chat_display.config(state=tk.DISABLED)
        
        # Limpar caixa de entrada
        self.user_input_box.delete("1.0", tk.END)
        self.update_word_count()
        
        # Exibir mensagem do usuário no chat
        self.append_message(f"Você: {user_input}", 'user')
        
        # Atualizar status
        self.status_var.set("Processando mensagem...")
        
        # Mostrar animação de "pensando"
        self.show_thinking_animation()
        
        # Verificar se já existe uma solicitação em andamento
        if self.api_request_in_progress:
            self.append_message("Sistema: Aguarde a resposta anterior ser concluída.", 'system')
            return
        
        # Iniciar thread para enviar mensagem à API (evita congelar a interface)
        self.api_request_in_progress = True
        threading.Thread(target=self.process_message, args=(user_input,), daemon=True).start()

    def show_thinking_animation(self):
        """Exibe uma animação de 'pensando' enquanto aguarda resposta"""
        thinking_text = "Assistente está pensando"
        dots = "."
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n{thinking_text}{dots}", ('thinking', 'thinking_tag'))
        
        # Criar marcas de texto
        self.chat_display.mark_set("thinking_tag_start", f"end-{len(thinking_text+dots)}c")
        self.chat_display.mark_gravity("thinking_tag_start", tk.LEFT)
        self.chat_display.mark_set("thinking_tag_end", "end")
        self.chat_display.mark_gravity("thinking_tag_end", tk.RIGHT)
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        def update_dots():
            nonlocal dots
            if len(dots) >= 3:
                dots = "."
            else:
                dots += "."
            
            self.chat_display.config(state=tk.NORMAL)
            try:
                self.chat_display.delete("thinking_tag_start", "thinking_tag_end")
                self.chat_display.insert("thinking_tag_start", f"{thinking_text}{dots}", 'thinking')
                self.chat_display.see(tk.END)
            except tk.TclError:
                # Se ocorrer um erro, é porque as marcas não existem mais
                pass
            self.chat_display.config(state=tk.DISABLED)
            
            self.thinking_animation_id = self.root.after(500, update_dots)
        
        self.thinking_animation_id = self.root.after(500, update_dots)

    def process_message(self, user_input):
        """Processa a mensagem do usuário e obtém resposta da API em uma thread separada"""
        try:
            headers = {
                "Authorization": f"Bearer {self.API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": {},
                "query": user_input,
                "response_mode": "blocking",  # Alterado para blocking em vez de streaming para simplificar
                "user": "user"
            }
            
            if self.conversation_id:
                payload["conversation_id"] = self.conversation_id
            
            # Enviar solicitação para a API do Dify
            response = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
            
            # Cancelar animação de pensamento
            if self.thinking_animation_id:
                self.root.after_cancel(self.thinking_animation_id)
                self.thinking_animation_id = None
                self.root.after(0, lambda: self.remove_thinking_animation())
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Salvar ID da conversa se for nova
                if not self.conversation_id and "conversation_id" in response_data:
                    self.conversation_id = response_data["conversation_id"]
                
                # Atualizar status de conexão
                self.root.after(0, lambda: self.connection_status.set("Conectado"))
                self.root.after(0, lambda: self.update_status_style("Connected"))
                
                # Exibir resposta do assistente
                if "answer" in response_data:
                    bot_message = response_data["answer"]
                    self.root.after(0, lambda: self.append_message(f"Assistente: {bot_message}", 'bot'))
                else:
                    self.root.after(0, lambda: self.append_message("Assistente: Não consegui gerar uma resposta adequada.", 'error'))
            else:
                error_msg = f"Erro na comunicação com a API. Código: {response.status_code}"
                
                # Se for erro 404, adicionar informação adicional
                if response.status_code == 404:
                    error_msg += " (Endpoint não encontrado. Verifique a URL da API.)"
                    # Sugerir URL alternativa
                    alternate_url = "https://api.dify.ai/v1/chat-messages"
                    if self.API_URL != alternate_url:
                        self.root.after(0, lambda: self.append_message(f"Sugestão: Tente usar a URL padrão da API Dify: {alternate_url}", 'system'))
                
                # Se for erro 401, adicionar informação adicional
                elif response.status_code == 401:
                    error_msg += " (Acesso não autorizado. Verifique sua chave API.)"
                
                self.root.after(0, lambda: self.append_message(error_msg, 'error'))
                
                # Atualizar status de conexão
                self.root.after(0, lambda: self.connection_status.set("Desconectado"))
                self.root.after(0, lambda: self.update_status_style("Disconnected"))
                
                # Se houver falha, tentar reconectar
                self.api_reconnect_attempts += 1
                if self.api_reconnect_attempts < self.MAX_RECONNECT_ATTEMPTS:
                    self.root.after(0, lambda: self.append_message(f"Sistema: Tentando reconectar... Tentativa {self.api_reconnect_attempts}/{self.MAX_RECONNECT_ATTEMPTS}", 'system'))
                    self.root.after(2000, self.check_api_connection)
        
        except requests.exceptions.RequestException as e:
            # Cancelar animação de pensamento
            if self.thinking_animation_id:
                self.root.after_cancel(self.thinking_animation_id)
                self.thinking_animation_id = None
                self.root.after(0, lambda: self.remove_thinking_animation())
            
            # error_msg = f"Erro de conexão: {str(e)}"
            # self.root.after(0, lambda: self.append_message(error_msg, 'error'))
            
            # Atualizar status de conexão
            self.root.after(0, lambda: self.connection_status.set("Desconectado"))
            self.root.after(0, lambda: self.update_status_style("Disconnected"))
            
            # Sugerir alterações de configuração
            suggestions = [
                "Verifique sua conexão com a internet.",
                "Certifique-se de que a URL da API está correta.",
                "Verifique se a chave API é válida."
            ]
            for suggestion in suggestions:
                self.root.after(0, lambda s=suggestion: self.append_message(f"Sugestão: {s}", 'system'))
        
        except Exception as e:
            # Cancelar animação de pensamento
            if self.thinking_animation_id:
                self.root.after_cancel(self.thinking_animation_id)
                self.thinking_animation_id = None
                self.root.after(0, lambda: self.remove_thinking_animation())
            
            error_msg = f"Erro ao processar mensagem: {str(e)}"
            self.root.after(0, lambda: self.append_message(error_msg, 'error'))
        
        finally:
            # Atualizar status
            self.root.after(0, lambda: self.status_var.set("Pronto para conversar"))
            self.api_request_in_progress = False

    def remove_thinking_animation(self):
        """Remove a animação de 'pensando' do chat"""
        self.chat_display.config(state=tk.NORMAL)
        try:
            self.chat_display.delete("thinking_tag_start", "thinking_tag_end")
        except tk.TclError:
            # Se as marcas não existirem, ignore
            pass
        self.chat_display.config(state=tk.DISABLED)

    def update_status_style(self, style):
        """Atualiza o estilo do indicador de status"""
        if style == "Connected":
            self.status_label.configure(style="Connected.TLabel")
        else:
            self.status_label.configure(style="Disconnected.TLabel")

    def append_message(self, message, tag):
        """Adiciona uma mensagem à área de chat com a formatação adequada"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Adicionar timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", 'system')
        
        # Verificar se é necessário adicionar separador
        if self.chat_display.index(tk.END) != "1.0":
            self.chat_display.insert(tk.END, "\n")
        
        # Adicionar mensagem com formatação especial
        self.chat_display.insert(tk.END, f"{message}\n", tag)
        
        # Adicionar espaço após a mensagem
        self.chat_display.insert(tk.END, "\n")
        
        # Auto-rolar para a mensagem mais recente
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Salvar na história local
        self.history.append({"time": timestamp, "message": message, "type": tag})

    def new_conversation(self):
        """Inicia uma nova conversa"""
        self.conversation_id = None
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Mensagem de boas-vindas futurista
        welcome = "Bem-vindo ao Neura AI! Sou seu assistente virtual projetado para ajudar em diversas tarefas. Como posso ajudar você hoje?"
        self.append_message(f"Assistente: {welcome}", 'bot')
        
        # Limpar histórico
        self.history = []
        
        # Atualizar status
        self.status_var.set("Nova conversa iniciada")
        
        # Resetar contador de tentativas de reconexão
        self.api_reconnect_attempts = 0

    def clear_chat(self):
        """Limpa o chat mantendo o ID da conversa"""
        if messagebox.askyesno("Limpar Chat", "Deseja limpar todas as mensagens do chat?\nO histórico da conversa na API será mantido."):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            # Mensagem informativa
            self.append_message("Sistema: Chat limpo. A conversa continua com o mesmo contexto na API.", 'system')

    def save_history(self):
        """Salva o histórico da conversa atual"""
        if not self.history:
            messagebox.showinfo("Informação", "Não há conversa para salvar.")
            return
        
        try:
            # Pedir o nome do arquivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
                initialdir="./histórico",
                title="Salvar Conversa"
            )
            
            if not file_path:  # Se o usuário cancelou
                return
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(f"Conversa: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                file.write("-" * 50 + "\n\n")
                
                for entry in self.history:
                    file.write(f"[{entry['time']}] {entry['message']}\n\n")
            
            messagebox.showinfo("Sucesso", f"Conversa salva em: {file_path}")
            
            # Atualizar status
            self.status_var.set(f"Conversa salva: {os.path.basename(file_path)}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar conversa: {str(e)}")

    def export_as_pdf(self):
        """Exporta o histórico da conversa como PDF"""
        if not self.history:
            messagebox.showinfo("Informação", "Não há conversa para exportar.")
            return
        
        try:
            # Verificar se o módulo reportlab está disponível
            try:
                import reportlab
                has_reportlab = True
            except ImportError:
                has_reportlab = False
            
            if not has_reportlab:
                if messagebox.askyesno("Módulo Necessário", 
                                       "É necessário instalar o módulo 'reportlab' para exportar como PDF. Deseja instalá-lo agora?"):
                    # Tentar instalar o reportlab usando pip
                    import subprocess
                    self.status_var.set("Instalando módulo reportlab...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
                    messagebox.showinfo("Sucesso", "Módulo instalado com sucesso. Tente exportar novamente.")
                return
            
            # Importações específicas para PDF
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            # Pedir o nome do arquivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
                initialdir="./histórico",
                title="Exportar como PDF"
            )
            
            if not file_path:  # Se o usuário cancelou
                return
            
            # Configurar documento PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Criar estilos customizados
            styles.add(ParagraphStyle(name='User',
                                      parent=styles['Normal'],
                                      textColor=colors.blue,
                                      fontSize=10,
                                      leftIndent=20))
            
            styles.add(ParagraphStyle(name='Bot',
                                      parent=styles['Normal'],
                                      textColor=colors.darkgreen,
                                      fontSize=10,
                                      leftIndent=20))
            
            styles.add(ParagraphStyle(name='System',
                                      parent=styles['Italic'],
                                      textColor=colors.gray,
                                      fontSize=9,
                                      leftIndent=10))
            
            styles.add(ParagraphStyle(name='Error',
                                      parent=styles['Normal'],
                                      textColor=colors.red,
                                      fontSize=9,
                                      leftIndent=10))
            
            # Conteúdo do documento
            content = []
            
            # Título
            title = Paragraph(f"Conversa: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Heading1'])
            content.append(title)
            content.append(Spacer(1, 12))
            
            # Adicionar mensagens
            for entry in self.history:
                # Determinar estilo baseado no tipo de mensagem
                if entry['type'] == 'user':
                    style = styles['User']
                elif entry['type'] == 'bot':
                    style = styles['Bot']
                elif entry['type'] == 'error':
                    style = styles['Error']
                else:
                    style = styles['System']
                
                # Adicionar timestamp e mensagem
                timestamp = Paragraph(f"[{entry['time']}]", styles['System'])
                content.append(timestamp)
                
                message = Paragraph(entry['message'], style)
                content.append(message)
                content.append(Spacer(1, 6))
            
            # Informação de rodapé
            footer = Paragraph("Gerado por Neura AI - Powered by Dify", styles['Italic'])
            content.append(Spacer(1, 20))
            content.append(footer)
            
            # Gerar PDF
            doc.build(content)
            
            messagebox.showinfo("Sucesso", f"Conversa exportada para: {file_path}")
            
            # Perguntar se deseja abrir o arquivo
            if messagebox.askyesno("Abrir Arquivo", "Deseja abrir o arquivo PDF agora?"):
                self.open_file(file_path)
            
            # Atualizar status
            self.status_var.set(f"Conversa exportada: {os.path.basename(file_path)}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar conversa: {str(e)}")

    def open_file(self, file_path):
        """Abre um arquivo com o aplicativo padrão do sistema"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {str(e)}")

    def copy_selected_text(self):
        """Copia o texto selecionado para a área de transferência"""
        try:
            # Tentar obter seleção do chat_display
            if self.chat_display.tag_ranges(tk.SEL):
                selected_text = self.chat_display.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.status_var.set("Texto copiado para a área de transferência")
            # Tentar obter seleção do user_input_box
            elif self.user_input_box.tag_ranges(tk.SEL):
                selected_text = self.user_input_box.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.status_var.set("Texto copiado para a área de transferência")
            else:
                self.status_var.set("Nenhum texto selecionado")
        except Exception as e:
            self.status_var.set(f"Erro ao copiar texto: {str(e)}")

    def paste_text(self):
        """Cola o texto da área de transferência"""
        try:
            text = self.root.clipboard_get()
            self.user_input_box.insert(tk.INSERT, text)
            self.update_word_count()
        except Exception as e:
            self.status_var.set(f"Erro ao colar texto: {str(e)}")

    def load_settings(self):
        """Carrega configurações do aplicativo"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as file:
                    settings = json.load(file)
                    
                    # Aplicar configurações
                    if "api_key" in settings and settings["api_key"]:
                        self.API_KEY = settings["api_key"]
                    
                    if "api_url" in settings and settings["api_url"]:
                        self.API_URL = settings["api_url"]
                    
                    if "dark_mode" in settings:
                        self.dark_mode = settings["dark_mode"]
                        if self.dark_mode:
                            self.toggle_dark_mode()
                    
                    if "voice_active" in settings:
                        self.voice_active = settings["voice_active"]
                        self.update_voice_button()
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            # Criar arquivo de configuração padrão
            self.save_settings({"api_key": self.API_KEY, "api_url": self.API_URL})

    def save_settings(self, settings_dict):
        """Salva configurações do aplicativo"""
        try:
            # Carregar configurações existentes
            existing_settings = {}
            if os.path.exists("config.json"):
                with open("config.json", "r") as file:
                    existing_settings = json.load(file)
            
            # Atualizar com novas configurações
            existing_settings.update(settings_dict)
            
            # Salvar configurações
            with open("config.json", "w") as file:
                json.dump(existing_settings, file, indent=4)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")

    def show_settings(self):
        """Exibe janela de configurações com estilo futurista"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações - Neura AI")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        settings_window.configure(bg=self.colors["bg_primary"])
        
        # Ícone da janela (se disponível)
        try:
            if hasattr(self.root, 'iconbitmap'):
                settings_window.iconbitmap(self.root.iconbitmap())
        except:
            pass
        
        # Frame principal com estilo neomórfico
        main_frame = ttk.Frame(settings_window, style="TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Configurações do Sistema", style="Header.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de API
        api_frame = ttk.Frame(notebook, style="TFrame", padding=10)
        notebook.add(api_frame, text="API")
        
        # Configuração da API
        ttk.Label(api_frame, text="Chave API:", style="TLabel").grid(row=0, column=0, sticky=tk.W, pady=10)
        api_key_entry = ttk.Entry(api_frame, width=40)
        api_key_entry.grid(row=0, column=1, sticky=tk.W, pady=10)
        api_key_entry.insert(0, self.API_KEY)
        
        ttk.Label(api_frame, text="URL da API:", style="TLabel").grid(row=1, column=0, sticky=tk.W, pady=10)
        api_url_entry = ttk.Entry(api_frame, width=40)
        api_url_entry.grid(row=1, column=1, sticky=tk.W, pady=10)
        api_url_entry.insert(0, self.API_URL)
        
        test_api_btn = ttk.Button(api_frame, text="Testar Conexão", 
                                command=lambda: self.test_api_connection(api_key_entry.get(), api_url_entry.get()))
        test_api_btn.grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Aba de Interface
        interface_frame = ttk.Frame(notebook, style="TFrame", padding=10)
        notebook.add(interface_frame, text="Interface")
        
        # Opção de tema escuro
        dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        dark_mode_check = ttk.Checkbutton(interface_frame, text="Modo Escuro", variable=dark_mode_var)
        dark_mode_check.grid(row=0, column=0, sticky=tk.W, pady=10)
        
        # Tamanho da fonte
        ttk.Label(interface_frame, text="Tamanho da Fonte:", style="TLabel").grid(row=1, column=0, sticky=tk.W, pady=10)
        font_size_var = tk.IntVar(value=10)  # Valor padrão
        font_size_scale = ttk.Scale(interface_frame, from_=8, to=16, orient=tk.HORIZONTAL, 
                                  variable=font_size_var, length=200)
        font_size_scale.grid(row=1, column=1, sticky=tk.W, pady=10)
        font_size_label = ttk.Label(interface_frame, textvariable=font_size_var, style="TLabel")
        font_size_label.grid(row=1, column=2, sticky=tk.W, pady=10)
        
        # Continuação do código a partir do último ponto

        # Aba de Avançado
        advanced_frame = ttk.Frame(notebook, style="TFrame", padding=10)
        notebook.add(advanced_frame, text="Avançado")
        
        # Opções avançadas
        ttk.Label(advanced_frame, text="Tempo limite da API (segundos):", style="TLabel").grid(row=0, column=0, sticky=tk.W, pady=10)
        timeout_var = tk.IntVar(value=30)
        timeout_spin = ttk.Spinbox(advanced_frame, from_=5, to=120, textvariable=timeout_var, width=5)
        timeout_spin.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # Opção para habilitar o envio por voz
        voice_var = tk.BooleanVar(value=self.voice_active)
        voice_check = ttk.Checkbutton(advanced_frame, text="Ativar recursos de voz (experimental)", variable=voice_var)
        voice_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Opção para limpar cache
        clear_cache_btn = ttk.Button(advanced_frame, text="Limpar Cache", 
                                   command=self.clear_cache)
        clear_cache_btn.grid(row=2, column=0, sticky=tk.W, pady=10)
        
        # Botões
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=10)
        
        save_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Salvar", 
            command=lambda: self.save_settings_and_close(
                settings_window, 
                api_key_entry.get(), 
                api_url_entry.get(),
                dark_mode_var.get(),
                font_size_var.get(),
                voice_var.get(),
                timeout_var.get()
            ),
            color=self.colors["bg_secondary"]
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Cancelar", 
            command=settings_window.destroy,
            color=self.colors["bg_secondary"]
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Centralizar janela
        settings_window.update_idletasks()
        width = settings_window.winfo_width()
        height = settings_window.winfo_height()
        x = (settings_window.winfo_screenwidth() // 2) - (width // 2)
        y = (settings_window.winfo_screenheight() // 2) - (height // 2)
        settings_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def save_settings_and_close(self, window, api_key, api_url, dark_mode, font_size, voice_active, timeout):
        """Salva configurações e fecha a janela de configurações"""
        settings = {
            "api_key": api_key,
            "api_url": api_url,
            "dark_mode": dark_mode,
            "font_size": font_size,
            "voice_active": voice_active,
            "timeout": timeout
        }
        
        # Atualizar variáveis
        self.API_KEY = api_key
        self.API_URL = api_url
        
        # Atualizar fonte
        current_font = self.chat_display.cget("font")
        if isinstance(current_font, str):
            font_family = current_font.split()[0]
        else:
            font_family = current_font[0]
        
        new_font = (font_family, font_size)
        self.chat_display.config(font=new_font)
        self.user_input_box.config(font=new_font)
        
        # Atualizar modo escuro se necessário
        if self.dark_mode != dark_mode:
            self.dark_mode = dark_mode
            self.toggle_dark_mode()
        
        # Atualizar voz
        self.voice_active = voice_active
        self.update_voice_button()
        
        # Salvar configurações
        self.save_settings(settings)
        window.destroy()
        messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        
        # Verificar a conexão com a API
        self.check_api_connection()

    def update_voice_button(self):
        """Atualiza o botão de voz conforme a configuração"""
        if self.voice_active:
            self.voice_btn.text = "🔊 Voz"
            self.voice_btn.draw()
        else:
            self.voice_btn.text = "🔇 Voz"
            self.voice_btn.draw()

    def toggle_voice(self):
        """Alterna entre modo de voz ativado/desativado"""
        self.voice_active = not self.voice_active
        self.update_voice_button()
        self.save_settings({"voice_active": self.voice_active})
        
        # Mensagem informativa
        if self.voice_active:
            self.append_message("Sistema: Modo de voz ativado. Esta funcionalidade é experimental.", 'system')
        else:
            self.append_message("Sistema: Modo de voz desativado.", 'system')

    def clear_cache(self):
        """Limpa os arquivos de cache do aplicativo"""
        try:
            # Lista de diretórios para verificar e limpar
            cache_dirs = ["./cache", "./tmp"]
            
            files_removed = 0
            for directory in cache_dirs:
                if os.path.exists(directory):
                    for file in os.listdir(directory):
                        file_path = os.path.join(directory, file)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                                files_removed += 1
                        except Exception as e:
                            print(f"Erro ao remover {file_path}: {e}")
            
            messagebox.showinfo("Cache Limpo", f"{files_removed} arquivos temporários foram removidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar cache: {str(e)}")

    def test_api_connection(self, api_key, api_url):
        """Testa a conexão com a API usando as configurações fornecidas"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Verificar se a URL termina com '/'
            if not api_url.endswith('/'):
                api_url += '/'
            
            # Montar URL de teste
            test_url = api_url
            if 'chat-messages' not in api_url:
                test_url = api_url + 'chat-messages'
            
            # Fazer uma solicitação HEAD para verificar se o endpoint existe
            response = requests.head(test_url, headers=headers, timeout=5)
            
            if response.status_code < 400:  # Códigos 2xx e 3xx são considerados sucesso
                messagebox.showinfo("Sucesso", "Conexão com a API estabelecida com sucesso!")
                return True
            else:
                # error_msg = f"Erro na conexão: Código HTTP {response.status_code}"
                # messagebox.showerror("Erro", error_msg)
                return False
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível se conectar à API: {str(e)}")
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao testar conexão: {str(e)}")
            return False

    def check_api_connection(self):
        """Verifica a conexão com a API atual"""
        self.status_var.set("Verificando conexão com a API...")
        threading.Thread(target=self._check_api_connection_thread, daemon=True).start()

    def _check_api_connection_thread(self):
        """Thread para verificar a conexão com a API"""
        if self.test_api_connection(self.API_KEY, self.API_URL):
            self.root.after(0, lambda: self.connection_status.set("Conectado"))
            self.root.after(0, lambda: self.update_status_style("Connected"))
            self.api_reconnect_attempts = 0
        else:
            self.root.after(0, lambda: self.connection_status.set("Desconectado"))
            self.root.after(0, lambda: self.update_status_style("Disconnected"))
        
        self.root.after(0, lambda: self.status_var.set("Pronto para conversar"))

    def show_help(self):
        """Exibe janela de ajuda com design futurista"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Ajuda - Neura AI")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        help_window.grab_set()
        help_window.configure(bg=self.colors["bg_primary"])
        
        # Frame principal
        main_frame = ttk.Frame(help_window, style="TFrame", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="Guia do Usuário", style="Header.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Criar notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de instruções
        instructions_frame = ttk.Frame(notebook, padding=10)
        notebook.add(instructions_frame, text="Instruções")
        
        instructions_text = scrolledtext.ScrolledText(
            instructions_frame, wrap=tk.WORD, 
            font=('Segoe UI', 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"]
        )
        instructions_text.pack(fill=tk.BOTH, expand=True)
        instructions_text.insert(tk.END, """Instruções de Uso:

1. Iniciar uma conversa:
   - Digite sua mensagem na caixa de texto na parte inferior
   - Pressione Enter ou clique no botão de envio
   - Use Shift+Enter para adicionar uma nova linha sem enviar

2. Gerenciar conversas:
   - Clique em "Nova Conversa" para reiniciar o chat
   - Use o botão "Salvar" para gravar a conversa atual em arquivo
   - Use o botão "Exportar" para criar um PDF da conversa

3. Configurações:
   - Clique no botão ⚙️ para acessar as configurações
   - Você pode alterar a API Key e URL do Dify se necessário
   - Personalize a interface com o modo escuro e tamanho da fonte

4. Recursos avançados:
   - Use o botão "Tema" para alternar entre modo claro e escuro
   - Ative a função de voz experimental (quando disponível)
   - Verifique estatísticas da conversa no menu Ferramentas

5. Dicas:
   - Faça perguntas claras e específicas
   - O assistente pode não ter conhecimento sobre eventos muito recentes
   - Seja educado e respeitoso nas interações
   - Em caso de erro de conexão, verifique sua internet e as configurações da API
        """)
        instructions_text.config(state=tk.DISABLED)
        
        # Aba Atalhos
        shortcuts_frame = ttk.Frame(notebook, padding=10)
        notebook.add(shortcuts_frame, text="Atalhos")
        
        shortcuts_text = scrolledtext.ScrolledText(
            shortcuts_frame, wrap=tk.WORD, 
            font=('Segoe UI', 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"]
        )
        shortcuts_text.pack(fill=tk.BOTH, expand=True)
        shortcuts_text.insert(tk.END, """Atalhos de Teclado:

Ctrl+N - Nova conversa
Ctrl+S - Salvar histórico
Ctrl+C - Copiar texto selecionado
Ctrl+V - Colar texto
F1 - Abrir este menu de ajuda
F5 - Verificar conexão com a API
Enter - Enviar mensagem
Shift+Enter - Inserir quebra de linha
        """)
        shortcuts_text.config(state=tk.DISABLED)
        
        # Aba Sobre
        about_frame = ttk.Frame(notebook, padding=10)
        notebook.add(about_frame, text="Sobre")
        
        about_text = scrolledtext.ScrolledText(
            about_frame, wrap=tk.WORD, 
            font=('Segoe UI', 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"]
        )
        about_text.pack(fill=tk.BOTH, expand=True)
        about_text.insert(tk.END, """Neura AI - Assistente Inteligente

Versão: 2.0

Este aplicativo foi desenvolvido para proporcionar uma interface moderna e futurista para interagir com modelos de inteligência artificial através da plataforma Dify.

Características:
• Interface gráfica moderna e responsiva
• Suporte a temas claro e escuro
• Histórico de conversas com exportação
• Configuração personalizada da API
• Animações e efeitos visuais
• Design neomórfico para elementos interativos

A integração utiliza a API do Dify para processar as mensagens e gerar respostas contextuais relevantes.

© 2025 - Todos os direitos reservados
        """)
        about_text.config(state=tk.DISABLED)
        
        # Aba de Solução de Problemas
        troubleshoot_frame = ttk.Frame(notebook, padding=10)
        notebook.add(troubleshoot_frame, text="Solução de Problemas")
        
        troubleshoot_text = scrolledtext.ScrolledText(
            troubleshoot_frame, wrap=tk.WORD, 
            font=('Segoe UI', 10),
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"]
        )
        troubleshoot_text.pack(fill=tk.BOTH, expand=True)
        troubleshoot_text.insert(tk.END, """Solução de Problemas Comuns:

Problema: Erro 404 na comunicação com a API
Solução: 
- Verifique se a URL da API está correta nas configurações
- Certifique-se de que a URL termina com 'chat-messages'
- Confira se o servidor Dify está em funcionamento

Problema: Erro 401 (Não Autorizado)
Solução:
- Confirme se a chave API está correta nas configurações
- Verifique se a aplicação no Dify está ativa
- Tente gerar uma nova chave API no painel do Dify

Problema: Aplicativo lento ou não responsivo
Solução:
- Reinicie o aplicativo
- Verifique sua conexão de internet
- Limpe o cache nas configurações avançadas

Problema: Interface gráfica com problemas de exibição
Solução:
- Ajuste o tamanho da fonte nas configurações
- Alterne entre os modos claro e escuro
- Reinicie o aplicativo

Se o problema persistir, verifique o log de erros e entre em contato com o suporte.
        """)
        troubleshoot_text.config(state=tk.DISABLED)
        
        # Botão de fechar
        close_button = NeoMorphicButton(
            main_frame, width=100, height=40, 
            text="Fechar", command=help_window.destroy,
            color=self.colors["bg_secondary"]
        )
        close_button.pack(pady=10)

    def show_about(self):
        """Exibe a janela Sobre com animação"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Sobre - Neura AI")
        about_window.geometry("400x500")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        about_window.configure(bg=self.colors["bg_primary"])
        
        # Frame principal
        main_frame = ttk.Frame(about_window, style="TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título animado
        title_canvas = tk.Canvas(main_frame, width=360, height=80, 
                               bg=self.colors["bg_primary"], highlightthickness=0)
        title_canvas.pack(pady=(0, 20))
        
        # Desenhar título com animação
        title_text = title_canvas.create_text(180, 40, text="NEURA AI", 
                                           font=("Segoe UI", 24, "bold"),
                                           fill=self.colors["accent"])
        
        def animate_title():
            colors = [self.colors["accent"], self.colors["success"], 
                    self.colors["warning"], self.colors["error"]]
            current_color = 0
            
            def update_color():
                nonlocal current_color
                title_canvas.itemconfig(title_text, fill=colors[current_color])
                current_color = (current_color + 1) % len(colors)
                about_window.after(1500, update_color)
            
            update_color()
        
        animate_title()
        
        # Descrição
        description = """
Neura AI é um assistente de conversação avançado com interface futurista e recursos modernos. Baseado na tecnologia do Dify e desenvolvido com Tkinter, este aplicativo oferece uma experiência de usuário excepcional para interagir com modelos de inteligência artificial.

Versão 2.0
        """
        
        desc_label = ttk.Label(main_frame, text=description, wraplength=360, 
                             style="TLabel", justify=tk.CENTER)
        desc_label.pack(pady=10)
        
        # Separador
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Informações técnicas
        tech_info = f"""
Sistema: {platform.system()} {platform.release()}
Python: {platform.python_version()}
Tkinter: {tk.TkVersion}
Processador: {platform.processor()}
        """
        
        tech_label = ttk.Label(main_frame, text=tech_info, style="TLabel", justify=tk.LEFT)
        tech_label.pack(pady=10, anchor=tk.W)
        
        # Créditos
        credits = """
Desenvolvido utilizando:
• Python e Tkinter
• Dify API para processamento de IA
• Design neomórfico e animações personalizadas

© 2025 - Todos os direitos reservados
        """
        
        credits_label = ttk.Label(main_frame, text=credits, style="TLabel", justify=tk.CENTER)
        credits_label.pack(pady=10)
        
        # Botão de fechar
        close_button = NeoMorphicButton(
            main_frame, width=100, height=40, 
            text="Fechar", command=about_window.destroy,
            color=self.colors["bg_secondary"]
        )
        close_button.pack(pady=10)

    def show_api_info(self):
        """Exibe informações sobre a API do Dify"""
        api_window = tk.Toplevel(self.root)
        api_window.title("Informações da API - Neura AI")
        api_window.geometry("500x400")
        api_window.resizable(False, False)
        api_window.transient(self.root)
        api_window.grab_set()
        api_window.configure(bg=self.colors["bg_primary"])
        
        # Frame principal
        main_frame = ttk.Frame(api_window, style="TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Informações da API", style="Header.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Informações da conexão
        ttk.Label(main_frame, text="Status da Conexão:", style="TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        connection_label = ttk.Label(main_frame, text=self.connection_status.get(), style="TLabel")
        connection_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="URL da API:", style="TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        api_url_label = ttk.Label(main_frame, text=self.API_URL, style="TLabel")
        api_url_label.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="API Key:", style="TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
        api_key_masked = f"{self.API_KEY[:5]}...{self.API_KEY[-5:]}" if len(self.API_KEY) > 10 else "****"
        api_key_label = ttk.Label(main_frame, text=api_key_masked, style="TLabel")
        api_key_label.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Estatísticas (simular alguns dados para demonstração)
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=15)
        
        ttk.Label(main_frame, text="Estatísticas:", style="TLabel", font=("Segoe UI", 12, "bold")).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Tempo médio de resposta:", style="TLabel").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="1.2 segundos", style="TLabel").grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Consultas realizadas:", style="TLabel").grid(row=6, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=str(len(self.history) // 2), style="TLabel").grid(row=6, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Taxa de sucesso:", style="TLabel").grid(row=7, column=0, sticky=tk.W, pady=5)
        
        # Calcular taxa de sucesso baseada na história
        success_count = 0
        total_queries = 0
        for entry in self.history:
            if entry["type"] == "user":
                total_queries += 1
            elif entry["type"] == "bot":
                success_count += 1
        
        success_rate = (success_count / total_queries * 100) if total_queries > 0 else 0
        ttk.Label(main_frame, text=f"{success_rate:.1f}%", style="TLabel").grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # Botões
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        refresh_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Atualizar", command=lambda: self.update_api_info(connection_label, api_url_label, api_key_label),
            color=self.colors["bg_secondary"]
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Fechar", command=api_window.destroy,
            color=self.colors["bg_secondary"]
        )
        close_btn.pack(side=tk.LEFT, padx=5)
        
        doc_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Documentação", command=lambda: webbrowser.open("https://docs.dify.ai"),
            color=self.colors["bg_secondary"]
        )
        doc_btn.pack(side=tk.LEFT, padx=5)

    def update_api_info(self, conn_label, url_label, key_label):
        """Atualiza as informações da API na janela de informações"""
        self.check_api_connection()
        conn_label.config(text=self.connection_status.get())
        url_label.config(text=self.API_URL)
        api_key_masked = f"{self.API_KEY[:5]}...{self.API_KEY[-5:]}" if len(self.API_KEY) > 10 else "****"
        key_label.config(text=api_key_masked)

    def show_conversation_stats(self):
        """Exibe estatísticas da conversa atual"""
        if not self.history:
            messagebox.showinfo("Estatísticas", "Não há histórico de conversa para analisar.")
            return
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estatísticas da Conversa - Neura AI")
        stats_window.geometry("600x500")
        stats_window.transient(self.root)
        stats_window.grab_set()
        stats_window.configure(bg=self.colors["bg_primary"])
        
        # Frame principal
        main_frame = ttk.Frame(stats_window, style="TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Análise da Conversa", style="Header.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Calcular estatísticas
        user_messages = [entry for entry in self.history if entry["type"] == "user"]
        bot_messages = [entry for entry in self.history if entry["type"] == "bot"]
        total_messages = len(user_messages) + len(bot_messages)
        
        # Calcular comprimento médio das mensagens
        user_words = sum(len(re.findall(r'\b\w+\b', msg["message"])) for msg in user_messages)
        bot_words = sum(len(re.findall(r'\b\w+\b', msg["message"])) for msg in bot_messages)
        
        avg_user_words = user_words / len(user_messages) if user_messages else 0
        avg_bot_words = bot_words / len(bot_messages) if bot_messages else 0
        
        # Frame para mostrar estatísticas
        stats_frame = ttk.Frame(main_frame, style="TFrame")
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Estatísticas gerais
        ttk.Label(stats_frame, text="Estatísticas Gerais:", style="TLabel", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(stats_frame, text="Total de mensagens:", style="TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(stats_frame, text=str(total_messages), style="TLabel").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(stats_frame, text="Mensagens do usuário:", style="TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(stats_frame, text=str(len(user_messages)), style="TLabel").grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(stats_frame, text="Respostas do assistente:", style="TLabel").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(stats_frame, text=str(len(bot_messages)), style="TLabel").grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(stats_frame, text="Média de palavras por mensagem do usuário:", style="TLabel").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Label(stats_frame, text=f"{avg_user_words:.1f}", style="TLabel").grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(stats_frame, text="Média de palavras por resposta do assistente:", style="TLabel").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Label(stats_frame, text=f"{avg_bot_words:.1f}", style="TLabel").grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(stats_frame, text="Tempo total da conversa:", style="TLabel").grid(row=6, column=0, sticky=tk.W, pady=5)
        
        # Calcular tempo total da conversa
        if len(self.history) >= 2:
            start_time = datetime.datetime.strptime(self.history[0]["time"], "%H:%M")
            end_time = datetime.datetime.strptime(self.history[-1]["time"], "%H:%M")
            
            # Ajustar se a conversa passar da meia-noite
            if end_time < start_time:
                end_time = end_time.replace(day=start_time.day + 1)
            
            duration = end_time - start_time
            duration_str = f"{duration.seconds // 60} minutos"
            ttk.Label(stats_frame, text=duration_str, style="TLabel").grid(row=6, column=1, sticky=tk.W, pady=5)
        else:
            ttk.Label(stats_frame, text="N/A", style="TLabel").grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # Visualização gráfica - exemplo de um gráfico simples de palavras
        canvas_frame = ttk.Frame(main_frame, style="TFrame")
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(canvas_frame, text="Distribuição de Palavras:", style="TLabel", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        chart_canvas = tk.Canvas(canvas_frame, height=150, bg=self.colors["bg_secondary"], highlightthickness=0)
        chart_canvas.pack(fill=tk.X, expand=True, pady=10)
        
        # Desenhar um gráfico de barras simples
        if user_words > 0 or bot_words > 0:
            max_words = max(user_words, bot_words)
            bar_width = 100
            scale_factor = 120 / max_words if max_words > 0 else 1
            
            # Barra do usuário
            user_height = user_words * scale_factor
            chart_canvas.create_rectangle(
                50, 150 - user_height, 
                50 + bar_width, 150,
                fill=self.colors["accent"], outline=""
            )
            chart_canvas.create_text(
                50 + bar_width//2, 150 - user_height - 10,
                text=str(user_words),
                fill=self.colors["text_primary"]
            )
            chart_canvas.create_text(
                50 + bar_width//2, 160,
                text="Usuário",
                fill=self.colors["text_primary"]
            )
            
            # Barra do assistente
            bot_height = bot_words * scale_factor
            chart_canvas.create_rectangle(
                200, 150 - bot_height, 
                200 + bar_width, 150,
                fill=self.colors["success"], outline=""
            )
            chart_canvas.create_text(
                200 + bar_width//2, 150 - bot_height - 10,
                text=str(bot_words),
                fill=self.colors["text_primary"]
            )
            chart_canvas.create_text(
                200 + bar_width//2, 160,
                text="Assistente",
                fill=self.colors["text_primary"]
            )
        
        # Botões
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=10)
        
        export_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Exportar", command=lambda: self.export_stats_as_csv(),
            color=self.colors["bg_secondary"]
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Fechar", command=stats_window.destroy,
            color=self.colors["bg_secondary"]
        )
        close_btn.pack(side=tk.RIGHT, padx=5)

    def export_stats_as_csv(self):
        """Exporta estatísticas da conversa como CSV"""
        try:
            # Pedir o nome do arquivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
                initialdir="./estatísticas",
                title="Exportar Estatísticas"
            )
            
            if not file_path:  # Se o usuário cancelou
                return
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Preparar dados
            user_messages = [entry for entry in self.history if entry["type"] == "user"]
            bot_messages = [entry for entry in self.history if entry["type"] == "bot"]
            
            stats_data = [
                ["Data", datetime.datetime.now().strftime("%d/%m/%Y")],
                ["Hora", datetime.datetime.now().strftime("%H:%M:%S")],
                [],
                ["Estatística", "Valor"],
                ["Total de mensagens", len(self.history)],
                ["Mensagens do usuário", len(user_messages)],
                ["Respostas do assistente", len(bot_messages)],
                ["Palavras do usuário", sum(len(re.findall(r'\b\w+\b', msg["message"])) for msg in user_messages)],
                ["Palavras do assistente", sum(len(re.findall(r'\b\w+\b', msg["message"])) for msg in bot_messages)],
                [],
                ["Histórico de Mensagens"],
                ["Hora", "Tipo", "Mensagem"]
            ]
            
            # Adicionar histórico de mensagens
            for entry in self.history:
                stats_data.append([
                    entry["time"],
                    "Usuário" if entry["type"] == "user" else "Assistente" if entry["type"] == "bot" else "Sistema",
                    entry["message"]
                ])
            
            # Escrever CSV
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                import csv
                writer = csv.writer(file)
                writer.writerows(stats_data)
            
            messagebox.showinfo("Sucesso", f"Estatísticas exportadas para: {file_path}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar estatísticas: {str(e)}")

    def show_history_window(self):
        """Exibe janela com histórico de conversas salvas"""
        history_dir = "./histórico"
        
        # Verificar se o diretório existe
        if not os.path.exists(history_dir):
            messagebox.showinfo("Histórico", "Não há histórico de conversas salvas.")
            return
        
        # Listar arquivos de histórico
        history_files = [f for f in os.listdir(history_dir) if f.endswith('.txt') or f.endswith('.csv')]
        
        if not history_files:
            messagebox.showinfo("Histórico", "Não há histórico de conversas salvas.")
            return
        
        # Criar janela
        history_window = tk.Toplevel(self.root)
        history_window.title("Histórico de Conversas - Neura AI")
        history_window.geometry("600x400")
        history_window.transient(self.root)
        history_window.grab_set()
        history_window.configure(bg=self.colors["bg_primary"])
        
        # Frame principal
        main_frame = ttk.Frame(history_window, style="TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Histórico de Conversas Salvas", style="Header.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Lista de arquivos
        file_frame = ttk.Frame(main_frame, style="TFrame")
        file_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(file_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        file_listbox = tk.Listbox(
            file_frame,
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_primary"],
            selectbackground=self.colors["accent"],
            selectforeground="white",
            font=("Segoe UI", 10),
            height=10,
            yscrollcommand=scrollbar.set
        )
        file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=file_listbox.yview)
        
        # Preencher listbox com arquivos
        for file in sorted(history_files, reverse=True):
            file_size = os.path.getsize(os.path.join(history_dir, file)) // 1024  # KB
            file_date = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(history_dir, file)))
            file_date_str = file_date.strftime("%d/%m/%Y %H:%M")
            file_listbox.insert(tk.END, f"{file} - {file_date_str} ({file_size} KB)")
        
        # Botões
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=10)
        
        open_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Abrir", 
            command=lambda: self.open_history_file(history_dir, history_files[file_listbox.curselection()[0]] if file_listbox.curselection() else None),
            color=self.colors["bg_secondary"]
        )
        open_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Excluir", 
            command=lambda: self.delete_history_file(history_dir, history_files[file_listbox.curselection()[0]] if file_listbox.curselection() else None, file_listbox),
            color=self.colors["bg_secondary"]
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = NeoMorphicButton(
            button_frame, width=120, height=40, 
            text="Fechar", command=history_window.destroy,
            color=self.colors["bg_secondary"]
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Associar duplo clique à abertura do arquivo
        file_listbox.bind("<Double-Button-1>", lambda e: self.open_history_file(
            history_dir, 
            history_files[file_listbox.curselection()[0]] if file_listbox.curselection() else None
        ))

    def open_history_file(self, directory, filename):
        """Abre um arquivo de histórico salvo"""
        if not filename:
            messagebox.showinfo("Abrir Arquivo", "Selecione um arquivo para abrir.")
            return
        
        try:
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                self.open_file(file_path)
            else:
                messagebox.showerror("Erro", f"Arquivo não encontrado: {file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir arquivo: {str(e)}")

    def delete_history_file(self, directory, filename, listbox):
        """Exclui um arquivo de histórico salvo"""
        if not filename:
            messagebox.showinfo("Excluir Arquivo", "Selecione um arquivo para excluir.")
            return
        
        try:
            if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o arquivo: {filename}?"):
                file_path = os.path.join(directory, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
                    # Atualizar listbox
                    selected_index = listbox.curselection()[0]
                    listbox.delete(selected_index)
                    
                    messagebox.showinfo("Sucesso", f"Arquivo excluído: {filename}")
                else:
                    messagebox.showerror("Erro", f"Arquivo não encontrado: {file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir arquivo: {str(e)}")

    def increase_font_size(self):
        """Aumenta o tamanho da fonte"""
        # Obter fonte atual
        current_font = self.chat_display.cget("font")
        if isinstance(current_font, str):
            font_family, font_size = current_font.split()
            font_size = int(font_size)
        else:
            font_family, font_size = current_font
        
        # Aumentar tamanho
        new_size = min(font_size + 1, 16)
        new_font = (font_family, new_size)
        
        # Aplicar nova fonte
        self.chat_display.config(font=new_font)
        self.user_input_box.config(font=new_font)
        
        # Salvar configuração
        self.save_settings({"font_size": new_size})
        
        # Atualizar status
        self.status_var.set(f"Tamanho da fonte aumentado para {new_size}")

    def decrease_font_size(self):
        """Diminui o tamanho da fonte"""
        # Obter fonte atual
        current_font = self.chat_display.cget("font")
        if isinstance(current_font, str):
            font_family, font_size = current_font.split()
            font_size = int(font_size)
        else:
            font_family, font_size = current_font
        
        # Diminuir tamanho
        new_size = max(font_size - 1, 8)
        new_font = (font_family, new_size)
        
        # Aplicar nova fonte
        self.chat_display.config(font=new_font)
        self.user_input_box.config(font=new_font)
        
        # Salvar configuração
        self.save_settings({"font_size": new_size})
        
        # Atualizar status
        self.status_var.set(f"Tamanho da fonte diminuído para {new_size}")

    def check_for_updates(self):
        """Simula verificação de atualizações"""
        self.status_var.set("Verificando atualizações...")
        
        # Simular verificação
        update_window = tk.Toplevel(self.root)
        update_window.title("Verificação de Atualizações - Neura AI")
        update_window.geometry("400x250")
        update_window.resizable(False, False)
        update_window.transient(self.root)
        update_window.grab_set()
        update_window.configure(bg=self.colors["bg_primary"])
        
        # Frame principal
        main_frame = ttk.Frame(update_window, style="TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Simular progresso
        progress_var = tk.DoubleVar()
        progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=300, 
                                 mode='determinate', variable=progress_var)
        progress.pack(pady=20)
        
        status_label = ttk.Label(main_frame, text="Verificando atualizações...", style="TLabel")
        status_label.pack(pady=10)
        
        # Função para simular progresso
        def simulate_progress():
            for i in range(101):
                progress_var.set(i)
                if i < 50:
                    status_label.config(text=f"Verificando atualizações... {i}%")
                elif i < 80:
                    status_label.config(text=f"Conectando ao servidor... {i}%")
                else:
                    status_label.config(text=f"Comparando versões... {i}%")
                update_window.update()
                time.sleep(0.02)
            
            # Resultado final
            progress.pack_forget()
            status_label.config(text="Verificação concluída!")
            
            result_frame = ttk.Frame(main_frame, style="TFrame")
            result_frame.pack(fill=tk.X, pady=20)
            
            # Escolher aleatoriamente se há atualizações
            has_update = random.choice([True, False])
            
            if has_update:
                result_icon = "✅"
                result_text = "Nova versão disponível: 2.1"
                update_btn = NeoMorphicButton(
                    main_frame, width=150, height=40, 
                    text="Atualizar Agora", command=update_window.destroy,
                    color=self.colors["accent"]
                )
                update_btn.pack(pady=10)
            else:
                result_icon = "✓"
                result_text = "Você já possui a versão mais recente (2.0)"
            
            result_label = ttk.Label(result_frame, text=f"{result_icon} {result_text}", 
                                   style="TLabel", font=("Segoe UI", 12))
            result_label.pack()
            
            # Botão de fechar
            if not has_update:
                close_btn = NeoMorphicButton(
                    main_frame, width=100, height=40, 
                    text="Fechar", command=update_window.destroy,
                    color=self.colors["bg_secondary"]
                )
                close_btn.pack(pady=10)
            
            # Atualizar status principal
            self.status_var.set("Verificação de atualizações concluída")
        
        # Iniciar simulação em uma thread
        threading.Thread(target=simulate_progress, daemon=True).start()


def main():
    """Função principal para iniciar o aplicativo"""
    root = tk.Tk()
    app = FuturisticChatBot(root)
    
    # Configurar o ícone do aplicativo (usando um ícone padrão do Tkinter)
    try:
        # Tentar usar o ícone padrão do Tkinter (pode variar dependendo do sistema)
        root.iconbitmap(default="")
    except:
        # Ignora se não for possível definir um ícone
        pass
    
    # Configurar o fechamento da janela
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    
    # Iniciar loop principal
    root.mainloop()


if __name__ == "__main__":
    main()