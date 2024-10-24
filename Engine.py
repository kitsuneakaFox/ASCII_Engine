import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, colorchooser
import os
import json
import re  # Přidáno pro regulární výrazy
import subprocess

class ASCIIEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Engine Demo")
        self.create_menu()

        # Frame for line numbers and text area
        self.frame = tk.Frame(root)
        self.frame.pack(expand=True, fill=tk.BOTH)

        # Line numbers
        self.line_numbers = tk.Text(self.frame, width=4, bg="white", fg="black", font=("Courier New", 12), padx=5, pady=5)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Text widget with scrollbar
        self.text_frame = tk.Frame(self.frame)
        self.text_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.scrollbar = tk.Scrollbar(self.text_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(self.text_frame, wrap=tk.WORD, bg="black", fg="white", font=("Courier New", 12), yscrollcommand=self.scrollbar.set)
        self.text.pack(expand=True, fill=tk.BOTH)
        self.text.bind("<KeyRelease>", self.update_line_numbers)
        self.text.bind("<MouseWheel>", self.on_mouse_wheel)

        self.scrollbar.config(command=self.on_scroll)

        # Initialize color tags
        self.text.tag_config("command", foreground="blue")
        self.text.tag_config("symbol", foreground="orange")
        self.text.tag_config("comment", foreground="green")

        # Load settings
        self.load_settings()

        # Initial update of line numbers
        self.update_line_numbers()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Soubor", menu=file_menu)
        file_menu.add_command(label="Nový projekt", command=self.novy_projekt, accelerator="Ctrl+N")
        file_menu.add_command(label="Uložit jako...", command=self.ulozit_jako, accelerator="Ctrl+S")
        file_menu.add_command(label="Otevřít", command=self.otevrit, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Konec", command=self.root.quit, accelerator="Ctrl+Q")

        # Game Menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hra", menu=game_menu)
        game_menu.add_command(label="Editor map", command=self.editor_map)

        # Build Menu
        build_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Zestavit", menu=build_menu)
        build_menu.add_command(label="Zestavit ", command=self.zestavit_a_spustit, accelerator="Ctrl+R")

        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Nastavení", menu=settings_menu)
        settings_menu.add_command(label="Změnit barvu pozadí", command=self.zmenit_barvu_pozadi)
        settings_menu.add_command(label="Změnit barvu textu", command=self.zmenit_barvu_textu)
        settings_menu.add_command(label="Změnit velikost písma", command=self.zmenit_velikost_pisma)

        # About Menu
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="O ASCII Engine", menu=about_menu)
        about_menu.add_command(label="Informace", command=self.zobrazit_info)
        about_menu.add_command(label="Manuál", command=self.zobrazit_manual)  # New Manual option

    def update_line_numbers(self, event=None):
        """Update line numbers in the line_numbers text widget."""
        line_count = int(self.text.index('end-1c').split('.')[0])
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete(1.0, tk.END)  # Clear current line numbers
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")  # Insert new line numbers
        self.line_numbers.config(state=tk.DISABLED)  # Make it read-only

    def on_scroll(self, *args):
        """Scroll the text and line numbers together."""
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling."""
        self.text.yview_scroll(int(-1*(event.delta/120)), "units")
        self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")

        # Binding shortcuts
        self.root.bind("<Control-n>", lambda event: self.novy_projekt())
        self.root.bind("<Control-s>", lambda event: self.ulozit_jako())
        self.root.bind("<Control-o>", lambda event: self.otevrit())
        self.root.bind("<Control-h>", lambda event: self.zobrazit_napovedu())

    def load_settings(self):
        save_folder = "Save"
        os.makedirs(save_folder, exist_ok=True)
        settings_file = os.path.join(save_folder, "settings.json")

        if os.path.exists(settings_file):
            with open(settings_file, 'r') as file:
                settings = json.load(file)
                # Load background and foreground colors, font size
                self.text.config(bg=settings.get("bg_color", "black"), fg=settings.get("fg_color", "white"))
                font_size = settings.get("font_size", 12)
                self.text.config(font=("Courier New", font_size))
            
                # Load window geometry and state
                window_geometry = settings.get("window_geometry", None)
                if window_geometry:
                    self.root.geometry(window_geometry)
            
                # Restore maximized state
                is_maximized = settings.get("is_maximized", False)
                if is_maximized:
                    self.root.state('zoomed')  # Maximized state for Windows

    def save_settings(self):
        save_folder = "Save"
        os.makedirs(save_folder, exist_ok=True)
        settings_file = os.path.join(save_folder, "settings.json")

        # Get window's current geometry (size and position)
        window_geometry = self.root.winfo_geometry()

        # Check if the window is maximized
        is_maximized = (self.root.state() == 'zoomed')

        settings = {
            "bg_color": self.text.cget("bg"),
            "fg_color": self.text.cget("fg"),
            "font_size": self.get_font_size(),
            "window_geometry": window_geometry,
            "is_maximized": is_maximized
        }

        with open(settings_file, 'w') as file:
            json.dump(settings, file)


    def get_font_size(self):
        font_info = self.text.cget("font")
        match = re.search(r'(\d+)', font_info)
        return int(match.group(0)) if match else 12

    def novy_projekt(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textové soubory", "*.txt")])
        if file_path:
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, f"# Nový projekt: {file_path}\n")
            self.text.tag_add("comment", "1.0", "1.end")
            self.root.title(f"ASCII Engine - {file_path}")

    def ulozit_jako(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textové soubory", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text.get("1.0", tk.END))
            self.root.title(f"ASCII Engine - {file_path}")
            self.save_settings()

    def otevrit(self):
        file_path = filedialog.askopenfilename(filetypes=[("Textové soubory", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, file.read())
            self.root.title(f"ASCII Engine - {file_path}")

    def zmenit_barvu_pozadi(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.text.config(bg=color)
            self.save_settings()

    def zmenit_barvu_textu(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.text.config(fg=color)
            self.save_settings()

    def zmenit_velikost_pisma(self):
        size = simpledialog.askinteger("Změnit velikost písma", "Zadejte velikost písma:")
        if size:
            self.text.config(font=("Courier New", size))
            self.save_settings()

    def zobrazit_manual(self):
         # Vytvoření nového okna pro manuál
        manual_window = tk.Toplevel(self.root)
        manual_window.title("Manuál - ASCII Engine")
        manual_window.geometry("619x769")  # Nastavení velikosti okna

        # Přidání textového widgetu pro obsah manuálu
        manual_text = tk.Text(manual_window, wrap=tk.WORD, bg="white", fg="black", font=("Courier New", 12))
        manual_text.pack(expand=True, fill=tk.BOTH)

        # Přidání posuvníku
        scrollbar = tk.Scrollbar(manual_window, command=manual_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        manual_text.config(yscrollcommand=scrollbar.set)

        # Obsah manuálu
        manual_content = (
            "ASCII Engine - Manuál\n"
            "-------------------------------\n"
            "Úvod:\n"
            "ASCII Engine je aplikace určená pro vývoj textových her v prostředí CMD.\n"
            "\n"
            "Funkce:\n"
            "- Tvorba textových her s moderním uživatelským rozhraním.\n"
            "- Podpora pro vlastní skripty.\n"
            "- Možnost přizpůsobení barev a textových formátů.\n"
            "\n"
            "Použití:\n"
            "1. Vytvořte nový projekt pomocí 'Nový projekt' v menu Soubory.\n"
            "2. Zapište váš kód do textového pole.\n"
            "3. Uložte svůj projekt a spusťte ho pomocí 'Zestavit'.\n"
            "\n"
            "Příklady příkazů:\n"
            "- echo Hello World\n"
            "- set VAR=value\n"
            "\n"
            "Základní příkazy:\n"
            "- pause\n"
            "- start\n"
            "- cls\n"
            "- exit\n"
            "- set\n"
            "\n"
            "Symboly:\n"
            "- @, #, $, %, ^, &, *, (\n"
            "\n"
            "Nastavení:\n"
            "Můžete upravit barvu pozadí, barvu textu a velikost písma v menu Nastavení.\n"
            "\n"
            "Podpora:\n"
            "Pokud potřebujete pomoc, kontaktujte nás na Gamejolt.\n"
            "-------------------------------\n"
        )

        # Vložení obsahu do textového widgetu
        manual_text.insert(tk.END, manual_content)

        # Zamezení editaci textu
        manual_text.config(state=tk.DISABLED)

    def zbarvit_text(self, event=None):
        # Vyčistit předchozí tagy
        self.text.tag_remove("command", "1.0", tk.END)
        self.text.tag_remove("symbol", "1.0", tk.END)
        self.text.tag_remove("comment", "1.0", tk.END)

        # Získat text z textového pole
        text_content = self.text.get("1.0", tk.END)

        # Rozdělit text na slova
        lines = text_content.splitlines()

        for line_number, line in enumerate(lines):
            for word in line.split():
                # Změna barvy pro příkazy
                if word in ["pause", "start", "echo", "echo off", "cls", "exit", "set", "call", "if", "goto", "title", "color", "copy", "del"]:
                    start_index = line.index(word)
                    end_index = start_index + len(word)
                    self.text.tag_add("command", f"{line_number + 1}.{start_index}", f"{line_number + 1}.{end_index}")

                # Změna barvy pro symboly
                for symbol in "(@)#$%^&*":
                    if symbol in word:
                        start_index = line.index(symbol)
                        end_index = start_index + 1
                        self.text.tag_add("symbol", f"{line_number + 1}.{start_index}", f"{line_number + 1}.{end_index}")

                # Zbarvení pro komentáře
                if line.strip().startswith("REM") or line.strip().startswith("::"):
                    self.text.tag_add("comment", f"{line_number + 1}.0", f"{line_number + 1}.end")

    def zobrazit_napovedu(self):
        help_message = "Dostupné příkazy:\n" \
                       "pause - pozastaví provádění skriptu\n" \
                       "start - spustí nový proces\n" \
                       "echo - zobrazí zprávu\n" \
                       "REM - komentář\n" \
                       ":: - také komentář\n" \
                       "set - nastaví hodnotu proměnné\n" \
                       "if - podmíněné vykonání příkazů\n" \
                       "goto - skok na označenou část skriptu\n" \
                       "call - volá jiný skript\n" \
                       "exit - ukončí skript\n" \
                       "cls - vymaže obrazovku\n" \
                       "del - smaže soubor\n" \
                       "copy - zkopíruje soubor\n" \
                       "dir - zobrazí seznam souborů a adresářů\n" \
                       "title - nastaví název okna příkazového řádku\n" \
                       "color - změní barvu textu a pozadí\n" \
                       "Použijte 'Zobrazit nápovědu' pro více informací."
        messagebox.showinfo("Nápověda", help_message)

    def zobrazit_info(self):
        info_message = (
            "ASCII Engine - Demo Verze 2.4\n"
            "-------------------------------\n"
            "Vyvinuto pro vývoj textových her v CMD\n"
            "Technologie: Python, tkinter\n"
            "Možnosti:\n"
            "- Tvorba textových her s moderním UI\n"
            "- Podpora vlastních skriptů\n"
            "- Nastavení barev a textových formátů\n"
            "Plánované funkce:\n"
            "- Integrovaná podpora pro více jazyků\n"
            "- Rozšířená správa herních projektů\n"
            "-------------------------------\n"
            "Vývojář: DarkCraft Games\n"
            "Rok: 2024\n"
            "Copyright © 2024\n"
        )
        messagebox.showinfo("O ASCII Engine", info_message)


    def vyber_nazvy(self):
        # Create a new Toplevel window for name input
        name_window = tk.Toplevel(self.root)
        name_window.title("Zadejte názvy hry a studia")
        name_window.geometry("425x354")  # Set the size of the window
        name_window.configure(bg="#f0f0f0")  # Background color

        # Header label
        header_label = tk.Label(name_window, text="Vytvořte novou hru",
                                 font=("Arial", 16, "bold"), bg="#f0f0f0")
        header_label.pack(pady=10)

        # Information label
        info_label = tk.Label(name_window, text="Zadejte název hry a studia. \n"
                                                 "Systém automaticky vytvoří potřebné složky.",
                              bg="#f0f0f0", wraplength=350, justify="center")
        info_label.pack(pady=5)

        # Create labels and entry fields
        tk.Label(name_window, text="Název hry (bez přípony):", bg="#f0f0f0").pack(pady=5)
        game_name_entry = tk.Entry(name_window)
        game_name_entry.pack(pady=5)

        tk.Label(name_window, text="Název studia:", bg="#f0f0f0").pack(pady=5)
        studio_name_entry = tk.Entry(name_window)
        studio_name_entry.pack(pady=5)

        # Create a submit button
        def submit():
            game_name = game_name_entry.get() or "temp_game"
            studio_name = studio_name_entry.get() or "temp_studio"
            name_window.destroy()  # Close the window
            return game_name, studio_name

        tk.Button(name_window, text="Potvrdit", command=lambda: submit(), bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)

        # Center the window on the screen
        name_window.eval('tk::PlaceWindow %s center' % name_window.winfo_toplevel())

        name_window.transient(self.root)  # Make the window a modal
        name_window.grab_set()  # Prevent interaction with other windows until closed
        self.root.wait_window(name_window)  # Wait until the window is closed

        # Return the inputted names
        return submit()  # This will return the values after the window is closed

    def ulozit_text_do_bat(self, jmeno_hry, game_folder):
        # Save current text directly into .bat file in game folder
        bat_path = os.path.join(game_folder, f"{jmeno_hry}.bat")
        with open(bat_path, 'w') as bat_file:
            # Python code written directly into the .bat file
            bat_file.write(f'@echo off\n')
            bat_file.write(f'python -c "{self.text.get("1.0", tk.END).replace("\"", "\\\"")}"\npause\n')

        if os.path.exists(bat_path):
            return bat_path
        else:
            messagebox.showerror("Chyba", "Nepodařilo se vytvořit .bat soubor.")
            return None

    def vytvorit_licenci(self, jmeno_hry, jmeno_studia, game_folder):
        license_text = f"""\
# Licenční smlouva pro {jmeno_hry}

Tato aplikace je poskytována "tak, jak je", bez jakýchkoli záruk a podmínek jakéhokoli druhu. 
Používáním této aplikace souhlasíte s následujícími podmínkami:

1. Můžete použít, kopírovat a distribuovat tuto aplikaci za předpokladu, že nedojde k její modifikaci.
2. Nejsme odpovědní za žádné škody způsobené používáním této aplikace.
3. Jakékoli použití této aplikace je na vaše vlastní riziko.

Děkujeme za vaši podporu!

# Informace o složkách:
Složky, které budou vytvořeny pro tuto hru, zahrnují:
- bin
- Save_game
- {jmeno_hry}_DATA
- {jmeno_studia}
"""
        with open(os.path.join(game_folder, f"{jmeno_hry}_license.txt"), 'w') as license_file:
            license_file.write(license_text)

    def vytvorit_slozky(self, jmeno_hry):
        # Create main folder and subfolders for the game
        main_folder = jmeno_hry
        os.makedirs(main_folder, exist_ok=True)

        # Create subfolders
        subfolders = ['bin', 'Save_game', f'{jmeno_hry}_DATA']
        for subfolder in subfolders:
            os.makedirs(os.path.join(main_folder, subfolder), exist_ok=True)

        return main_folder  # Return the main folder path for bat file creation

    def zestavit_a_spustit(self):
        jmeno_hry, jmeno_studia = self.vyber_nazvy()

        # Create game folder and subfolders
        game_folder = self.vytvorit_slozky(jmeno_hry)

        # Save .bat file and license
        bat_path = self.ulozit_text_do_bat(jmeno_hry, game_folder)
        self.vytvorit_licenci(jmeno_hry, jmeno_studia, game_folder)

        # Open the game folder
        if bat_path:
            subprocess.Popen(f'explorer {game_folder}')  # Open the folder in Windows Explorer
            messagebox.showinfo("Úspěch", f"Složka {game_folder} byla úspěšně vytvořena.")

    def editor_map(self):
        # Otevře okno pro editor map
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Editor map")

        # Nastavení barevného schématu
        editor_window.configure(bg="#f0f0f0")

        # Vytvoří textovou oblast pro mapový editor
        editor_text = tk.Text(editor_window, wrap="none", width=80, height=25, bg="#ffffff", fg="#000000", font=("Arial", 12))
        editor_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Přidá posuvníky pro vertikální a horizontální posouvání
        v_scroll = tk.Scrollbar(editor_window, orient=tk.VERTICAL, command=editor_text.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        editor_text.config(yscrollcommand=v_scroll.set)

        h_scroll = tk.Scrollbar(editor_window, orient=tk.HORIZONTAL, command=editor_text.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        editor_text.config(xscrollcommand=h_scroll.set)

        # Přidání základního menu do editoru
        menu_bar = tk.Menu(editor_window)
        editor_window.config(menu=menu_bar)

        # Menu "Soubor"
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Soubor", menu=file_menu)
        file_menu.add_command(label="Nový", command=lambda: editor_text.delete("1.0", tk.END))
        file_menu.add_command(label="Otevřít", command=self.open_map_file)
        file_menu.add_command(label="Uložit", command=lambda: self.save_map_file(editor_text))
        file_menu.add_separator()
        file_menu.add_command(label="Zavřít", command=editor_window.destroy)

        # Menu "Nápověda"
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Nápověda", menu=help_menu)
        help_menu.add_command(label="Jak používat editor", command=self.show_map_help)

        # Přidání formátovacích tlačítek
        format_frame = tk.Frame(editor_window, bg="#f0f0f0")
        format_frame.pack(side=tk.TOP, fill=tk.X)

        bold_button = tk.Button(format_frame, text="Tučné", command=lambda: self.toggle_bold(editor_text))
        bold_button.pack(side=tk.LEFT, padx=5, pady=5)

        italic_button = tk.Button(format_frame, text="Kurzíva", command=lambda: self.toggle_italic(editor_text))
        italic_button.pack(side=tk.LEFT, padx=5, pady=5)

        color_button = tk.Button(format_frame, text="Barva textu", command=lambda: self.change_text_color(editor_text))
        color_button.pack(side=tk.LEFT, padx=5, pady=5)

    def show_map_help(self):
        # Pomocná funkce pro zobrazení nápovědy
        help_text = (
            "Nápověda pro editor map:\n\n"
            "1. Vytvořte nový dokument kliknutím na 'Nový'.\n"
            "2. Otevřete existující mapu kliknutím na 'Otevřít'.\n"
            "3. Uložte svou práci kliknutím na 'Uložit'.\n"
            "4. Použijte tlačítka pro formátování textu:\n"
            "   - 'Tučné': Zvýrazní vybraný text.\n"
            "   - 'Kurzíva': Změní vybraný text na kurzívu.\n"
            "   - 'Barva textu': Umožňuje změnit barvu vybraného textu.\n"
            "5. Zde je příklad, jak může vaše mapa vypadat:\n\n"
            "XXXXXOOO\n"
            "XXXXOOOO\n"
            "XOOOOWWW\n"
            "XMMMMWWW\n"
            "XWWWWWWW\n\n"
            "6. Pokud potřebujete pomoc, znovu klikněte na 'Jak používat editor'."
        )
        messagebox.showinfo("Nápověda", help_text)

    def toggle_bold(self, text_widget):
        # Přepínání tučného písma
        current_tags = text_widget.tag_names("sel.first")
        if "bold" in current_tags:
            text_widget.tag_remove("bold", "sel.first", "sel.last")
        else:
            text_widget.tag_add("bold", "sel.first", "sel.last")
            text_widget.tag_configure("bold", font=("Arial", 12, "bold"))

    def toggle_italic(self, text_widget):
        # Přepínání kurzívy
        current_tags = text_widget.tag_names("sel.first")
        if "italic" in current_tags:
            text_widget.tag_remove("italic", "sel.first", "sel.last")
        else:
            text_widget.tag_add("italic", "sel.first", "sel.last")
            text_widget.tag_configure("italic", font=("Arial", 12, "italic"))

    def change_text_color(self, text_widget):
        # Změna barvy textu
        color = colorchooser.askcolor()[1]
        if color:
            text_widget.tag_add("colored", "sel.first", "sel.last")
            text_widget.tag_configure("colored", foreground=color)

    def open_map_file(self):
        file_path = filedialog.askopenfilename(title="Otevřít mapu", filetypes=[("Map Files", "*.map"), ("Textové soubory", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
            messagebox.showinfo("Editor map", f"Mapa {file_path} byla úspěšně načtena.")
            return content

    def save_map_file(self, editor_text):
        file_path = filedialog.asksaveasfilename(defaultextension=".map", filetypes=[("Map Files", "*.map"), ("Textové soubory", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(editor_text.get("1.0", tk.END))
            messagebox.showinfo("Editor map", f"Mapa byla úspěšně uložena do {file_path}.")

if __name__ == "__main__":
    root = tk.Tk()
    engine = ASCIIEngine(root)
    root.mainloop()
