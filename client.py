import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class EmuNESGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("emunes 1.0 [C] Team Flames 1.0")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Emulator state
        self.rom_loaded = False
        self.rom_path = None
        self.is_playing = False
        
        self.setup_gui()
        
    def setup_gui(self):
        # Main menu bar
        self.create_menu_bar()
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        self.create_toolbar(main_frame)
        
        # Display area (where the game would show)
        self.create_display_area(main_frame)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open ROM", command=self.open_rom, accelerator="Ctrl+O")
        file_menu.add_command(label="Close ROM", command=self.close_rom)
        file_menu.add_separator()
        file_menu.add_command(label="Save State", command=self.save_state)
        file_menu.add_command(label="Load State", command=self.load_state)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Emulation menu
        emu_menu = tk.Menu(menubar, tearoff=0)
        emu_menu.add_command(label="Play", command=self.play_emu, accelerator="F5")
        emu_menu.add_command(label="Pause", command=self.pause_emu, accelerator="F6")
        emu_menu.add_command(label="Reset", command=self.reset_emu, accelerator="F7")
        emu_menu.add_separator()
        emu_menu.add_command(label="Fullscreen", command=self.toggle_fullscreen, accelerator="Alt+Enter")
        menubar.add_cascade(label="Emulation", menu=emu_menu)
        
        # Config menu
        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="Input", command=self.config_input)
        config_menu.add_command(label="Video", command=self.config_video)
        config_menu.add_command(label="Sound", command=self.config_sound)
        menubar.add_cascade(label="Config", menu=config_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Cheats", command=self.open_cheats)
        tools_menu.add_command(label="Debugger", command=self.open_debugger)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def create_toolbar(self, parent):
        toolbar = ttk.Frame(parent, height=40)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Toolbar buttons
        buttons = [
            ("Open", self.open_rom, "📁"),
            ("Play", self.play_emu, "▶️"),
            ("Pause", self.pause_emu, "⏸️"),
            ("Reset", self.reset_emu, "🔄"),
            ("Fullscreen", self.toggle_fullscreen, "⛶")
        ]
        
        for text, command, icon in buttons:
            btn = ttk.Button(toolbar, text=f"{icon} {text}", command=command)
            btn.pack(side=tk.LEFT, padx=2)
            
    def create_display_area(self, parent):
        display_frame = ttk.LabelFrame(parent, text="Display", padding=10)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Game display area
        self.display_canvas = tk.Canvas(
            display_frame, 
            bg='#000000', 
            highlightthickness=1, 
            highlightbackground='#555555'
        )
        self.display_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder text with new branding
        self.display_canvas.create_text(
            400, 200, 
            text="emunes 1.0\nTeam Flames\n\nNo ROM Loaded\nClick 'Open ROM' to load a game", 
            fill='#666666', 
            font=('Arial', 12), 
            justify=tk.CENTER
        )
        
    def create_control_panel(self, parent):
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Left side - ROM info
        info_frame = ttk.LabelFrame(control_frame, text="ROM Information", padding=5)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.rom_info_text = tk.Text(
            info_frame, 
            height=3, 
            width=50, 
            bg='#1a1a1a', 
            fg='#cccccc', 
            font=('Courier', 9)
        )
        self.rom_info_text.pack(fill=tk.X)
        self.rom_info_text.insert(tk.END, "No ROM loaded")
        self.rom_info_text.config(state=tk.DISABLED)
        
        # Right side - Controls
        ctrl_frame = ttk.LabelFrame(control_frame, text="Quick Controls", padding=5)
        ctrl_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ctrl_buttons = [
            ("Save State 1", lambda: self.quick_save(1)),
            ("Load State 1", lambda: self.quick_load(1)),
            ("Screenshot", self.take_screenshot)
        ]
        
        for text, command in ctrl_buttons:
            btn = ttk.Button(ctrl_frame, text=text, command=command)
            btn.pack(fill=tk.X, pady=1)
            
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_text = ttk.Label(status_frame, text="Ready - emunes 1.0 [C] Team Flames")
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        # FPS counter
        self.fps_label = ttk.Label(status_frame, text="FPS: --")
        self.fps_label.pack(side=tk.RIGHT, padx=5)
        
        # ROM status
        self.rom_status = ttk.Label(status_frame, text="No ROM")
        self.rom_status.pack(side=tk.RIGHT, padx=20)
        
    def show_about(self):
        about_text = """emunes 1.0

[C] Team Flames 1.0

NES Emulator Frontend
Built with Python and Tkinter

This is a GUI frontend for NES emulation.
Actual emulation core would be integrated separately."""
        messagebox.showinfo("About emunes 1.0", about_text)
        
    # Menu functions
    def open_rom(self):
        file_path = filedialog.askopenfilename(
            title="Open NES ROM - emunes 1.0",
            filetypes=[
                ("NES ROMs", "*.nes"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.rom_path = file_path
            self.rom_loaded = True
            filename = os.path.basename(file_path)
            
            # Update display
            self.display_canvas.delete("all")
            self.display_canvas.create_text(
                400, 200, 
                text=f"emunes 1.0\nTeam Flames\n\nROM Loaded:\n{filename}\n\nClick 'Play' to start", 
                fill='#00ff00', 
                font=('Arial', 12), 
                justify=tk.CENTER
            )
            
            # Update ROM info
            self.rom_info_text.config(state=tk.NORMAL)
            self.rom_info_text.delete(1.0, tk.END)
            self.rom_info_text.insert(tk.END, f"File: {filename}\nPath: {file_path}\nSize: {os.path.getsize(file_path)} bytes")
            self.rom_info_text.config(state=tk.DISABLED)
            
            # Update status
            self.rom_status.config(text=f"ROM: {filename}")
            self.status_text.config(text="ROM loaded successfully - emunes 1.0")
            
    def close_rom(self):
        if self.rom_loaded:
            self.rom_loaded = False
            self.is_playing = False
            self.rom_path = None
            
            # Reset display
            self.display_canvas.delete("all")
            self.display_canvas.create_text(
                400, 200, 
                text="emunes 1.0\nTeam Flames\n\nNo ROM Loaded\nClick 'Open ROM' to load a game", 
                fill='#666666', 
                font=('Arial', 12), 
                justify=tk.CENTER
            )
            
            # Reset ROM info
            self.rom_info_text.config(state=tk.NORMAL)
            self.rom_info_text.delete(1.0, tk.END)
            self.rom_info_text.insert(tk.END, "No ROM loaded")
            self.rom_info_text.config(state=tk.DISABLED)
            
            self.rom_status.config(text="No ROM")
            self.status_text.config(text="ROM closed - emunes 1.0")
            
    def play_emu(self):
        if self.rom_loaded and not self.is_playing:
            self.is_playing = True
            self.display_canvas.delete("all")
            self.display_canvas.create_text(
                400, 200, 
                text="emunes 1.0\nTeam Flames\n\nGame Playing\n(Press Pause to stop)", 
                fill='#00ff00', 
                font=('Arial', 12), 
                justify=tk.CENTER
            )
            self.status_text.config(text="Emulation running - emunes 1.0")
            self.fps_label.config(text="FPS: 60")
            
    def pause_emu(self):
        if self.is_playing:
            self.is_playing = False
            self.display_canvas.delete("all")
            self.display_canvas.create_text(
                400, 200, 
                text="emunes 1.0\nTeam Flames\n\nGame Paused\n(Press Play to continue)", 
                fill='#ffff00', 
                font=('Arial', 12), 
                justify=tk.CENTER
            )
            self.status_text.config(text="Emulation paused - emunes 1.0")
            self.fps_label.config(text="FPS: --")
            
    def reset_emu(self):
        if self.rom_loaded:
            self.is_playing = False
            self.display_canvas.delete("all")
            self.display_canvas.create_text(
                400, 200, 
                text="emunes 1.0\nTeam Flames\n\nGame Reset\n(Press Play to start)", 
                fill='#ff9900', 
                font=('Arial', 12), 
                justify=tk.CENTER
            )
            self.status_text.config(text="Emulation reset - emunes 1.0")
            self.fps_label.config(text="FPS: --")
            
    def toggle_fullscreen(self):
        messagebox.showinfo("Fullscreen", "Fullscreen mode would be activated here")
        
    def save_state(self):
        if self.rom_loaded:
            messagebox.showinfo("Save State", "Game state saved")
            
    def load_state(self):
        if self.rom_loaded:
            messagebox.showinfo("Load State", "Game state loaded")
            
    def config_input(self):
        messagebox.showinfo("Input Config", "Input configuration dialog would open here")
        
    def config_video(self):
        messagebox.showinfo("Video Config", "Video configuration dialog would open here")
        
    def config_sound(self):
        messagebox.showinfo("Sound Config", "Sound configuration dialog would open here")
        
    def open_cheats(self):
        messagebox.showinfo("Cheats", "Cheat code manager would open here")
        
    def open_debugger(self):
        messagebox.showinfo("Debugger", "Debugger window would open here")
        
    def quick_save(self, slot):
        if self.rom_loaded:
            self.status_text.config(text=f"Quick save to slot {slot} - emunes 1.0")
            
    def quick_load(self, slot):
        if self.rom_loaded:
            self.status_text.config(text=f"Quick load from slot {slot} - emunes 1.0")
            
    def take_screenshot(self):
        if self.rom_loaded:
            self.status_text.config(text="Screenshot saved - emunes 1.0")

def main():
    root = tk.Tk()
    app = EmuNESGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
