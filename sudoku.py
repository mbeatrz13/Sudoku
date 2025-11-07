import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import time


class SudokuGenerator: #aplicação do backtracking 
    """Gera e resolve tabuleiros de Sudoku configuráveis."""
    
    def __init__(self, tamanho_bloco=3, num_celulas_conhecidas=20):
        self.B = tamanho_bloco
        self.N = tamanho_bloco * tamanho_bloco
        self.num_conhecidas = num_celulas_conhecidas
        self.grid = [[0] * self.N for _ in range(self.N)]

    def _e_valido(self, linha, coluna, num):
        
        if num in self.grid[linha]: 
            return False

        for i in range(self.N):
            if self.grid[i][coluna] == num: 
                return False

        start_row = linha - linha % self.B
        start_col = coluna - coluna % self.B
        for i in range(self.B):
            for j in range(self.B):
                if self.grid[start_row + i][start_col + j] == num: 
                    return False
        return True

    def _preencher_grid(self):
        
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == 0:
                    numeros = list(range(1, self.N + 1))
                    random.shuffle(numeros) 
                    for num in numeros:
                        if self._e_valido(i, j, num):
                            self.grid[i][j] = num
                            if self._preencher_grid():
                                return True
                            self.grid[i][j] = 0
                    return False
        return True

    def gerar_sudoku(self):
        
        try:
           
            self.grid = [[0] * self.N for _ in range(self.N)]
            if not self._preencher_grid():
                raise Exception("Não foi possível gerar um gabarito de Sudoku.")

            casas_a_remover = (self.N * self.N) - self.num_conhecidas
            celulas = [(r, c) for r in range(self.N) for c in range(self.N)]
            random.shuffle(celulas)

            removidas = 0
            for linha, coluna in celulas:
                if removidas >= casas_a_remover:
                    break
                
                if self.grid[linha][coluna] != 0:
                    self.grid[linha][coluna] = 0
                    removidas += 1
            
            return self.grid

        except Exception as e:
            messagebox.showerror("Erro de Geração", str(e))
            return None

    def _preencher_grid_visual(self):
       
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == 0:
                    numeros = list(range(1, self.N + 1))
                    for num in numeros:
                        if self._e_valido(i, j, num):
                            self.grid[i][j] = num
                            
                            yield (i, j, num, 'tentativa') 
                            
                            if (yield from self._preencher_grid_visual()):
                                return True
                            
                            self.grid[i][j] = 0
                            
                            yield (i, j, 0, 'backtrack') 
                    return False 
        return True 



class SudokuGUI:
    def __init__(self, master):
        self.master = master
        master.title("Visualizador de Backtracking Sudoku")
        master.resizable(False, False)

        # Variáveis de Configuração
        self.tamanho_bloco_var = tk.IntVar(value=3)
        self.pistas_var = tk.IntVar(value=30)
        self.velocidade_var = tk.IntVar(value=20) 

        self.current_grid_size = 0
        self.current_sudoku_problem = None 
        self.entries = [] 
        self.solver_generator = None 

        # --- Frames Principais ---
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._setup_config_frame(main_frame)
        self._setup_action_frame(main_frame)
        
        self.sudoku_frame = ttk.Frame(main_frame, padding="5", relief="sunken", borderwidth=2)
        self.sudoku_frame.pack(pady=10)

        
        self.gerar_e_exibir_sudoku()

    def _setup_config_frame(self, parent):
        """Cria a seção de entrada de configurações."""
        config_frame = ttk.LabelFrame(parent, text="Configurações", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        config_frame.columnconfigure(1, weight=1)

        
        ttk.Label(config_frame, text="Tamanho do Bloco (B):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.tamanho_bloco_entry = ttk.Entry(config_frame, textvariable=self.tamanho_bloco_var, width=5)
        self.tamanho_bloco_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        ttk.Label(config_frame, text="Ex: 2=4x4, 3=9x9").grid(row=0, column=2, padx=5, pady=5, sticky='w')

      
        ttk.Label(config_frame, text="Nº de Pistas (Dificuldade):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.pistas_entry = ttk.Entry(config_frame, textvariable=self.pistas_var, width=5)
        self.pistas_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

       
        self.generate_button = ttk.Button(config_frame, text="Gerar Novo Sudoku", command=self.gerar_e_exibir_sudoku)
        self.generate_button.grid(row=0, column=3, rowspan=2, padx=10, ipady=10)

    def _setup_action_frame(self, parent):
        """Cria a seção com botões de ação (Resolver) e status."""
        action_frame = ttk.LabelFrame(parent, text="Ações", padding="10")
        action_frame.pack(fill=tk.X, pady=5)
        action_frame.columnconfigure(1, weight=1) # Faz o slider expandir

        self.solve_button = ttk.Button(action_frame, text="Resolver (Visualização)", command=self._iniciar_resolucao_visual)
        self.solve_button.grid(row=0, column=0, padx=5)

        
        ttk.Label(action_frame, text="Lento").grid(row=0, column=1, padx=(5, 0))
        self.velocidade_slider = ttk.Scale(action_frame, from_=100, to=1, variable=self.velocidade_var, orient=tk.HORIZONTAL)
        self.velocidade_slider.grid(row=0, column=2, padx=5, sticky='ew')
        ttk.Label(action_frame, text="Rápido").grid(row=0, column=3, padx=(0, 10))
        
        self.solving_label = ttk.Label(parent, text="", font=('Arial', 10, 'italic'))
        self.solving_label.pack(pady=(0, 5))

    def _limpar_grid(self):
        """Remove todos os widgets da grade atual."""
        for widget in self.sudoku_frame.winfo_children():
            widget.destroy()
        self.entries = []

    def gerar_e_exibir_sudoku(self):
        """Lê configurações, gera e exibe o novo Sudoku."""
       
        if self.solver_generator:
            try: self.solver_generator.close()
            except GeneratorExit: pass
            self.solver_generator = None
            
        try:
            bloco_size = self.tamanho_bloco_var.get()
            pistas = self.pistas_var.get()

            if bloco_size < 2 or bloco_size > 4:
                messagebox.showerror("Erro", "Tamanho do Bloco deve ser 2 (4x4), 3 (9x9) ou 4 (16x16).")
                return

            grid_size = bloco_size * bloco_size
            max_cells = grid_size * grid_size
            if pistas < 1 or pistas > max_cells:
                messagebox.showerror("Erro", f"Nº de Pistas deve estar entre 1 e {max_cells}.")
                return

            
            generator = SudokuGenerator(tamanho_bloco=bloco_size, num_celulas_conhecidas=pistas)
            new_sudoku = generator.gerar_sudoku()

            if new_sudoku is not None:
                self.current_grid_size = grid_size
                # Armazena o problema gerado
                self.current_sudoku_problem = [row[:] for row in new_sudoku]
                
                
                self._limpar_grid()
                self._desenhar_grid(new_sudoku, bloco_size)
                self._habilitar_controles()
                self.solving_label.config(text=f"Grid {grid_size}x{grid_size} gerado com {pistas} pistas.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def _desenhar_grid(self, sudoku_grid, bloco_size):
        """Desenha a grid do Sudoku com base no tabuleiro gerado."""
        self.entries = []
        N = len(sudoku_grid)

        for i in range(N):
            row_entries = []
            for j in range(N):
                value = sudoku_grid[i][j]

               
                is_prefilled = (value != 0)
                font_weight = "bold" if is_prefilled else "normal"
                fg_color = "black" if is_prefilled else "blue" 
                bg_color = "lightgray" if is_prefilled else "white"

                entry = tk.Entry(self.sudoku_frame,
                                 width=3,
                                 font=('Arial', 14, font_weight),
                                 justify='center',
                                 fg=fg_color,
                                 relief='flat',
                                 highlightthickness=1,
                                 highlightcolor='gray',
                                 highlightbackground='lightgray',
                                 )

                if is_prefilled:
                    entry.insert(0, str(value))
                
                
                entry.config(state='readonly', readonlybackground=bg_color)

               
                pad_top = 3 if (i % bloco_size == 0 and i != 0) else (1, 0)
                pad_left = 3 if (j % bloco_size == 0 and j != 0) else (1, 0)
                
                entry.grid(row=i, column=j, padx=pad_left, pady=pad_top, ipady=5, ipadx=5)
                row_entries.append(entry)
            self.entries.append(row_entries)

    def _habilitar_controles(self):
        """Habilita todos os botões e campos de entrada."""
        self.solve_button.config(state='normal')
        self.generate_button.config(state='normal')
        self.tamanho_bloco_entry.config(state='normal')
        self.pistas_entry.config(state='normal')
        self.velocidade_slider.config(state='normal')

    def _desabilitar_controles(self):
        """Desabilita controles durante a resolução."""
        self.solve_button.config(state='disabled')
        self.generate_button.config(state='disabled')
        self.tamanho_bloco_entry.config(state='disabled')
        self.pistas_entry.config(state='disabled')
        self.velocidade_slider.config(state='disabled')

    def _iniciar_resolucao_visual(self):
        """Prepara e inicia o processo de resolução visual."""
        if self.solver_generator:
            try: self.solver_generator.close() # Para o anterior
            except GeneratorExit: pass
            
        if self.current_sudoku_problem is None:
            messagebox.showerror("Erro", "Gere um Sudoku primeiro.")
            return
            
        self._desabilitar_controles()
        self.solving_label.config(text="Resolvendo...")
        
       
        temp_generator = SudokuGenerator(self.tamanho_bloco_var.get())
        
        
        temp_generator.grid = [row[:] for row in self.current_sudoku_problem]
        
       
        for r in range(self.current_grid_size):
            for c in range(self.current_grid_size):
                if self.current_sudoku_problem[r][c] == 0:
                    entry = self.entries[r][c]
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.config(state='readonly')
        
        
        self.solver_generator = temp_generator._preencher_grid_visual()
        self.start_time = time.time()
        
        
        self.master.after(10, self._proximo_passo_visual)

    def _proximo_passo_visual(self):
        """Executa um passo do gerador do resolvedor e atualiza a GUI."""
        try:
            
            passo = next(self.solver_generator, None)
            
            if passo:
                r, c, num, tipo = passo
                entry = self.entries[r][c]
                
                
                entry.config(state='normal') 
                entry.delete(0, tk.END)
                
                if tipo == 'tentativa':
                    entry.insert(0, str(num))
                    entry.config(fg='green', font=('Arial', 14, 'normal'))
                elif tipo == 'backtrack':
                    entry.config(fg='blue') 

                entry.config(state='readonly')
                
                
                self.master.after(self.velocidade_var.get(), self._proximo_passo_visual)
            else:
                
                self._finalizar_resolucao()
                
        except StopIteration:
            
            self._finalizar_resolucao()
        except Exception as e:
            
            if 'invalid command name' not in str(e):
                 messagebox.showerror("Erro na Resolução", str(e))
            self._habilitar_controles()

    def _finalizar_resolucao(self):
        """Chamado quando o resolvedor termina."""
        tempo_total = time.time() - self.start_time
        self.solver_generator = None
        self._habilitar_controles()
        
        
        solucao_completa = True
        for r in range(self.current_grid_size):
            if not solucao_completa: break
            for c in range(self.current_grid_size):
                if self.entries[r][c].get() == "":
                    solucao_completa = False
                    break
        
        if not solucao_completa:
            self.solving_label.config(text=f"Falha ao resolver! (Tempo: {tempo_total:.2f}s)")
        else:
            self.solving_label.config(text=f"Resolvido com sucesso! (Tempo: {tempo_total:.2f}s)")
            
            for i in range(self.current_grid_size):
                for j in range(self.current_grid_size):
                    
                    if self.current_sudoku_problem[i][j] == 0:
                        self.entries[i][j].config(fg='black')



if __name__ == "__main__":
    root = tk.Tk()
    
    style = ttk.Style()
    style.theme_use('clam') 

   
    style.configure('TButton', padding=6, relief='flat', font=('Arial', 10))
    style.configure('TLabel', font=('Arial', 10))
    style.configure('TLabelframe', padding=5, font=('Arial', 11, 'bold'))
    style.configure('TLabelframe.Label', font=('Arial', 11, 'bold'))

    app = SudokuGUI(root)
    root.mainloop()