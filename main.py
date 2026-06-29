import customtkinter as ctk
import threading
from tkinter import filedialog
from core.data_loader import load_data
from core.simulation import run_simulation
from core.finance import calculate_financials
from core.statistics import generate_statistics

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

plt.style.use('dark_background')

# Configurações de tema do CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") # Tema verde para combinar com finanças

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎰 B-TESTER PRO")
        self.geometry("1200x750") # Um pouco maior para os cards
        self.configure(fg_color="#0b0f19")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color="#151a28", border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="🎰 B-TESTER PRO", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#10b981")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(35, 25))
        
        # Parâmetros Frame
        self.param_frame = ctk.CTkFrame(self.sidebar, fg_color="#1e2536", corner_radius=12, border_width=1, border_color="#2b3548")
        self.param_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.lbl_targets = ctk.CTkLabel(self.param_frame, text="Números Alvo (separados por vírgula):", font=ctk.CTkFont(size=13, weight="bold"), text_color="#94a3b8")
        self.lbl_targets.pack(padx=20, pady=(20, 5), anchor="w")
        self.entry_targets = ctk.CTkEntry(self.param_frame, width=240, height=35, fg_color="#0b0f19", border_color="#2b3548", text_color="#e2e8f0")
        self.entry_targets.insert(0, "9,22,18,31,29,16,33,1,20,24,30,11,36,8,13")
        self.entry_targets.pack(padx=20, pady=(0, 15))
        
        self.lbl_attempts = ctk.CTkLabel(self.param_frame, text="Máximo de Tentativas:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#94a3b8")
        self.lbl_attempts.pack(padx=20, pady=(0, 5), anchor="w")
        self.entry_attempts = ctk.CTkEntry(self.param_frame, width=240, height=35, fg_color="#0b0f19", border_color="#2b3548", text_color="#e2e8f0")
        self.entry_attempts.insert(0, "4")
        self.entry_attempts.pack(padx=20, pady=(0, 15))
        
        self.lbl_martingale = ctk.CTkLabel(self.param_frame, text="Multiplicadores Martingale:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#94a3b8")
        self.lbl_martingale.pack(padx=20, pady=(0, 5), anchor="w")
        self.entry_martingale = ctk.CTkEntry(self.param_frame, width=240, height=35, fg_color="#0b0f19", border_color="#2b3548", text_color="#e2e8f0")
        self.entry_martingale.insert(0, "1,2,4,8")
        self.entry_martingale.pack(padx=20, pady=(0, 20))
        
        # Botões
        self.btn_run = ctk.CTkButton(self.sidebar, text="▶ INICIAR BACKTEST", height=55, font=ctk.CTkFont(size=15, weight="bold"), 
                                     fg_color="#10b981", hover_color="#059669", text_color="white", corner_radius=12,
                                     command=self.run_backtest_thread)
        self.btn_run.grid(row=7, column=0, padx=20, pady=(15, 5), sticky="ew")
        
        self.btn_tutorial = ctk.CTkButton(self.sidebar, text="❓ Como Usar", height=35, font=ctk.CTkFont(size=13, weight="bold"), 
                                          fg_color="#2b3548", hover_color="#374151", text_color="#e2e8f0", corner_radius=10,
                                          command=self.show_tutorial)
        self.btn_tutorial.grid(row=8, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        # Status & Progress
        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Aguardando dados...", font=ctk.CTkFont(size=12, slant="italic"), text_color="#94a3b8")
        self.lbl_status.grid(row=9, column=0, padx=20, pady=(0, 5), sticky="s")
        
        self.progress = ctk.CTkProgressBar(self.sidebar, height=10, progress_color="#10b981", fg_color="#1e2536", corner_radius=5)
        self.progress.grid(row=10, column=0, padx=20, pady=(0, 25), sticky="ew")
        self.progress.set(0)

        # MAIN AREA (TABS)
        self.main_frame = ctk.CTkFrame(self, fg_color="#0b0f19")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(self.main_frame, corner_radius=12, fg_color="#151a28", 
                                      segmented_button_fg_color="#1e2536",
                                      segmented_button_selected_color="#10b981",
                                      segmented_button_selected_hover_color="#059669")
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tabview._segmented_button.configure(font=ctk.CTkFont(size=16, weight="bold"))
        
        self.tab_data = self.tabview.add("📊 Fonte de Dados")
        self.tab_dash = self.tabview.add("📈 Dashboard Visual")
        self.tab_hist = self.tabview.add("📋 Auditoria (Histórico)")
        
        # --- TAB 1: DADOS ---
        self.tab_data.grid_rowconfigure(3, weight=1)
        self.tab_data.grid_columnconfigure(0, weight=1)
        
        self.header_data = ctk.CTkLabel(self.tab_data, text="Importação de Dados (Excel / CSV)", font=ctk.CTkFont(size=20, weight="bold"), text_color="#e2e8f0")
        self.header_data.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        self.btn_select_file = ctk.CTkButton(self.tab_data, text="📂 Selecionar Arquivo Local", command=self.select_file, height=45, fg_color="#2b3548", hover_color="#374151", corner_radius=10)
        self.btn_select_file.grid(row=1, column=0, sticky="w", padx=20, pady=5)
        
        self.lbl_file_name = ctk.CTkLabel(self.tab_data, text="Nenhum arquivo selecionado.", text_color="#94a3b8", font=ctk.CTkFont(size=13))
        self.lbl_file_name.grid(row=1, column=0, sticky="w", padx=(250, 20), pady=5)
        
        self.lbl_data_manual = ctk.CTkLabel(self.tab_data, text="Ou cole os resultados de roleta manualmente:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#94a3b8")
        self.lbl_data_manual.grid(row=2, column=0, sticky="w", padx=20, pady=(25, 10))
        
        self.text_data = ctk.CTkTextbox(self.tab_data, fg_color="#0b0f19", border_color="#2b3548", border_width=1, corner_radius=10, text_color="#e2e8f0", font=ctk.CTkFont(size=14))
        self.text_data.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.selected_file_path = None
        
        # --- TAB 2: DASHBOARD (NOVO DESIGN COM CARDS) ---
        self.tab_dash.grid_rowconfigure(1, weight=1)
        self.tab_dash.grid_columnconfigure(0, weight=1)
        
        # KPI Frame
        self.kpi_frame = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        self.kpi_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=15)
        for i in range(4):
            self.kpi_frame.grid_columnconfigure(i, weight=1)
            
        def create_card(parent, title, default_val):
            card = ctk.CTkFrame(parent, fg_color="#1e2536", corner_radius=12, border_width=1, border_color="#2b3548")
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#94a3b8").pack(pady=(20, 5))
            val_lbl = ctk.CTkLabel(card, text=default_val, font=ctk.CTkFont(size=32, weight="bold"), text_color="#e2e8f0")
            val_lbl.pack(pady=(0, 20))
            return card, val_lbl
            
        card1, self.val_triggers = create_card(self.kpi_frame, "Gatilhos Identificados", "0")
        card1.grid(row=0, column=0, padx=10, sticky="ew")
        
        card2, self.val_winrate = create_card(self.kpi_frame, "Taxa de Assertividade", "0.0%")
        card2.grid(row=0, column=1, padx=10, sticky="ew")
        
        card3, self.val_fixed = create_card(self.kpi_frame, "Balanço (Aposta Fixa)", "0.00")
        card3.grid(row=0, column=2, padx=10, sticky="ew")
        
        card4, self.val_mart = create_card(self.kpi_frame, "Balanço (Martingale)", "0.00")
        card4.grid(row=0, column=3, padx=10, sticky="ew")
        
        # Chart Frame
        self.chart_frame = ctk.CTkFrame(self.tab_dash, fg_color="#0b0f19", corner_radius=12, border_width=1, border_color="#2b3548")
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(5, 10))
        self.canvas_widget = None

        # Text Summary
        self.dash_text = ctk.CTkTextbox(self.tab_dash, font=("Consolas", 15), fg_color="#0b0f19", border_width=1, border_color="#2b3548", corner_radius=10, text_color="#10b981", height=110)
        self.dash_text.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # --- TAB 3: HISTORICO ---
        self.tab_hist.grid_rowconfigure(0, weight=1)
        self.tab_hist.grid_columnconfigure(0, weight=1)
        self.text_history = ctk.CTkTextbox(self.tab_hist, font=("Consolas", 14), fg_color="#0b0f19", border_width=1, border_color="#2b3548", corner_radius=10, text_color="#e2e8f0")
        self.text_history.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Exibir tutorial ao iniciar
        self.after(500, self.show_tutorial)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo",
            filetypes=[("Planilhas", "*.xlsx *.xls *.csv"), ("Todos", "*.*")]
        )
        if file_path:
            self.selected_file_path = file_path
            self.lbl_file_name.configure(text=file_path.split("/")[-1], text_color="#10b981")
            self.text_data.delete("1.0", "end")
            self.text_data.insert("1.0", f"Arquivo vinculado com sucesso:\n{file_path}\n\nPode iniciar o Backtest.")

    def run_backtest_thread(self):
        threading.Thread(target=self.run_backtest).start()

    def update_ui(self, status, prog=None):
        self.lbl_status.configure(text=status)
        if prog is not None:
            self.progress.set(prog)
        self.update_idletasks()

    def run_backtest(self):
        self.btn_run.configure(state="disabled", fg_color="#2b3548")
        self.text_history.delete("1.0", "end")
        self.dash_text.delete("1.0", "end")
        
        try:
            self.update_ui("Lendo parâmetros...", 0.1)
            targets_str = self.entry_targets.get()
            target_numbers = [int(x.strip()) for x in targets_str.split(',')]
            max_attempts = int(self.entry_attempts.get())
            mart_str = self.entry_martingale.get()
            mart_multipliers = [float(x.strip()) for x in mart_str.split(',')]
            
            self.update_ui("Processando banco de dados...", 0.3)
            if self.selected_file_path:
                numbers = load_data(file_path=self.selected_file_path)
            else:
                raw_data = self.text_data.get("1.0", "end-1c")
                numbers = load_data(text_data=raw_data)
            
            if not numbers:
                self.update_ui("Aviso: Nenhum dado válido.", 0.0)
                self.btn_run.configure(state="normal", fg_color="#10b981")
                return
                
            self.update_ui("Motor de simulação rodando...", 0.5)
            sim_results = run_simulation(numbers, target_numbers, max_attempts)
            
            self.update_ui("Calculando indicadores financeiros...", 0.7)
            fin_results = calculate_financials(sim_results, bet_amount=1.0, payout_multiplier=36, target_count=len(target_numbers), martingale_multipliers=mart_multipliers)
            
            self.update_ui("Renderizando Dashboard...", 0.9)
            stats = generate_statistics(sim_results, fin_results, len(numbers))
            
            # Atualiza KPIs (Cards)
            self.val_triggers.configure(text=str(stats['total_triggers']))
            self.val_winrate.configure(text=f"{stats['win_rate']:.1f}%")
            
            color_fixed = "#10b981" if stats['net_fixed_profit'] >= 0 else "#ef4444"
            self.val_fixed.configure(text=f"{stats['net_fixed_profit']:.2f}", text_color=color_fixed)
            
            color_mart = "#10b981" if stats['net_martingale_profit'] >= 0 else "#ef4444"
            self.val_mart.configure(text=f"{stats['net_martingale_profit']:.2f}", text_color=color_mart)
            
            self.dash_text.insert("end", f"▶ RESUMO EXECUTIVO:\n\n")
            self.dash_text.insert("end", f"  • Foram analisados {len(numbers)} giros da roleta, encontrando {stats['total_triggers']} gatilhos válidos para a estratégia.\n")
            self.dash_text.insert("end", f"  • A taxa de sucesso (assertividade) final da estratégia foi de {stats['win_rate']:.1f}%.\n")
            
            msg = "RESULTADO POSITIVO (LUCRO)" if stats['net_martingale_profit'] >= 0 else "RESULTADO NEGATIVO (PREJUÍZO)"
            self.dash_text.insert("end", f"  • Conclusão: A estratégia obteve um {msg} ao utilizar Martingale.")

            # Populate History Tab
            hist_out = " ID   | GATILHO | ÍNDICE | RESULTADO | TENTATIVA | LUCRO FIXO | LUCRO MART.\n"
            hist_out += "-"*75 + "\n"
            for i, (s, f) in enumerate(zip(sim_results, fin_results)):
                res_str = "GREEN" if s['hit'] else "RED  "
                att_str = str(s['hit_attempt']) if s['hit'] else "-"
                hist_out += f" #{i+1:<4} | TIPO {s['trigger_type']}  | {s['trigger_index']:<6} | {res_str}     | {att_str:<9} | {f['fixed_profit']:<10.2f} | {f['martingale_profit']:.2f}\n"
            self.text_history.insert("end", hist_out)
            
            # Plot
            self.plot_equity(fin_results)
            
            self.update_ui("Backtest Concluído!", 1.0)
            self.tabview.set("📈 Dashboard Visual")
            
        except Exception as e:
            self.update_ui("Erro de Execução.", 0.0)
            self.text_history.insert("end", f"\nErro Crítico: {str(e)}")
            
        # Restaura botão (voltando para a cor padrão do tema verde)
        self.btn_run.configure(state="normal", fg_color="#10b981")

    def plot_equity(self, fin_results):
        if self.canvas_widget:
            self.canvas_widget.destroy()
            
        cum_fixed = [0]
        cum_mart = [0]
        for f in fin_results:
            cum_fixed.append(cum_fixed[-1] + f['fixed_profit'])
            cum_mart.append(cum_mart[-1] + f['martingale_profit'])
            
        fig = Figure(figsize=(8, 4.5), dpi=100)
        fig.patch.set_facecolor('#0b0f19') # Fundo para combinar com a UI
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0b0f19')
        
        ax.plot(cum_fixed, label="Aposta Fixa", color="#3b82f6", linewidth=2.5, alpha=0.9)
        ax.plot(cum_mart, label="Estratégia Martingale", color="#10b981", linewidth=2.5, alpha=0.9)
        
        ax.set_title("Evolução Financeira", color='#e2e8f0', fontsize=16, pad=15, weight='bold')
        ax.set_xlabel("Quantidade de Gatilhos", color='#94a3b8', fontsize=12)
        ax.set_ylabel("Saldo Financeiro (u.m.)", color='#94a3b8', fontsize=12)
        ax.tick_params(colors='#94a3b8', labelsize=10)
        
        # Legend styling
        legend = ax.legend(facecolor='#1e2536', edgecolor='#2b3548', labelcolor='#e2e8f0', fontsize=11)
        ax.grid(True, color='#2b3548', linestyle='--', alpha=0.6)
        
        # Remove top/right borders
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#2b3548')
        ax.spines['left'].set_color('#2b3548')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    def show_tutorial(self):
        tutorial_win = ctk.CTkToplevel(self)
        tutorial_win.title("Como Usar o B-TESTER PRO")
        tutorial_win.geometry("600x480")
        tutorial_win.configure(fg_color="#0b0f19")
        tutorial_win.attributes("-topmost", True)
        tutorial_win.grab_set()
        
        lbl_title = ctk.CTkLabel(tutorial_win, text="Bem-vindo ao B-TESTER PRO! 🎰", font=ctk.CTkFont(size=22, weight="bold"), text_color="#10b981")
        lbl_title.pack(pady=(30, 20))
        
        tutorial_text = (
            "Siga os passos abaixo para realizar o seu Backtest:\n\n"
            "1. Insira os 'Números Alvo' separados por vírgula na barra lateral.\n\n"
            "2. Configure o número máximo de tentativas e os multiplicadores de Martingale.\n\n"
            "3. Na aba 'Fonte de Dados', selecione um arquivo Excel/CSV com o histórico\n"
            "   da roleta OU cole os números manualmente na caixa de texto.\n\n"
            "4. Clique no botão verde '▶ INICIAR BACKTEST'.\n\n"
            "Acompanhe o 'Dashboard Visual' para ver os gráficos e a aba 'Auditoria'\n"
            "para consultar o histórico detalhado, jogada a jogada."
        )
        
        txt_box = ctk.CTkTextbox(tutorial_win, font=ctk.CTkFont(size=14), fg_color="#151a28", border_width=1, border_color="#2b3548", text_color="#e2e8f0", corner_radius=10)
        txt_box.pack(padx=30, pady=10, fill="both", expand=True)
        txt_box.insert("1.0", tutorial_text)
        txt_box.configure(state="disabled")
        
        btn_close = ctk.CTkButton(tutorial_win, text="Entendi! Fechar", height=45, fg_color="#10b981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=tutorial_win.destroy)
        btn_close.pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
