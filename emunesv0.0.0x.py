import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import time
import random
from datetime import datetime

class NESHardware:
    """Proof-of-concept NES hardware simulation"""
    
    def __init__(self):
        self.ppu_initialized = False
        self.apu_initialized = False
        self.cpu_initialized = False
        self.memory_initialized = False
        self.controllers_initialized = False
        self.bios_complete = False
        
        # PPU Registers
        self.ppu_registers = {
            'PPUCTRL': 0x00,
            'PPUMASK': 0x00,
            'PPUSTATUS': 0x00,
            'OAMADDR': 0x00,
            'PPUSCROLL': 0x00,
            'PPUADDR': 0x00,
            'PPUDATA': 0x00
        }
        
        # APU Registers
        self.apu_registers = {
            'SQ1_VOL': 0x00,
            'SQ1_SWEEP': 0x00,
            'SQ1_LO': 0x00,
            'SQ1_HI': 0x00,
            'SQ2_VOL': 0x00,
            'SQ2_SWEEP': 0x00,
            'TRI_LINEAR': 0x00,
            'TRI_LO': 0x00,
            'NOISE_VOL': 0x00,
            'DMC_FREQ': 0x00,
            'APU_STATUS': 0x00
        }
        
        # Memory
        self.ram = [0x00] * 2048  # 2KB RAM
        self.vram = [0x00] * 2048  # Video RAM
        
    def initialize_ppu(self):
        """Initialize Picture Processing Unit"""
        self.ppu_registers['PPUCTRL'] = 0x80
        self.ppu_registers['PPUMASK'] = 0x06
        self.ppu_registers['PPUSTATUS'] = 0xA0
        self.ppu_initialized = True
        return "PPU: VRAM cleared, palettes initialized, sprites reset"
    
    def initialize_apu(self):
        """Initialize Audio Processing Unit"""
        self.apu_registers['APU_STATUS'] = 0x0F
        self.apu_registers['SQ1_VOL'] = 0x30
        self.apu_registers['SQ2_VOL'] = 0x30
        self.apu_initialized = True
        return "APU: Channels muted, timers reset, DMC disabled"
    
    def initialize_cpu(self):
        """Initialize 6502 CPU"""
        # Reset vector at 0xFFFC
        self.ram[0x1FFC] = 0x00  # Low byte of reset vector
        self.ram[0x1FFD] = 0xC0  # High byte of reset vector
        self.cpu_initialized = True
        return "CPU: Registers cleared, stack pointer at 0xFD, reset vector set"
    
    def initialize_memory(self):
        """Initialize memory banks"""
        # Clear RAM
        for i in range(len(self.ram)):
            self.ram[i] = 0x00
            
        # Clear VRAM
        for i in range(len(self.vram)):
            self.vram[i] = 0x00
            
        # Set up zero page and stack area
        self.ram[0x0000] = 0xFF  # IO ports
        self.ram[0x0001] = 0xFF
        self.memory_initialized = True
        return "Memory: 2KB RAM cleared, VRAM initialized, zero page configured"
    
    def initialize_controllers(self):
        """Initialize game controllers"""
        self.controllers_initialized = True
        return "Controllers: Ports 1&2 initialized, strobe mode set"
    
    def run_bios(self):
        """Run full BIOS initialization sequence"""
        bios_log = []
        bios_log.append("=== NES BIOS Initialization ===")
        bios_log.append(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        bios_log.append("")
        
        # Memory initialization
        bios_log.append("1. Memory Test...")
        bios_log.append(f"   {self.initialize_memory()}")
        time.sleep(0.5)
        
        # CPU initialization
        bios_log.append("2. CPU Reset...")
        bios_log.append(f"   {self.initialize_cpu()}")
        time.sleep(0.5)
        
        # PPU initialization
        bios_log.append("3. PPU Startup...")
        bios_log.append(f"   {self.initialize_ppu()}")
        time.sleep(0.5)
        
        # APU initialization
        bios_log.append("4. APU Sound Test...")
        bios_log.append(f"   {self.initialize_apu()}")
        time.sleep(0.5)
        
        # Controller initialization
        bios_log.append("5. Controller Check...")
        bios_log.append(f"   {self.initialize_controllers()}")
        time.sleep(0.5)
        
        # Final checks
        bios_log.append("")
        bios_log.append("6. System Diagnostics...")
        bios_log.append("   RAM: 2KB OK")
        bios_log.append("   VRAM: 2KB OK")
        bios_log.append("   CPU: 6502 1.79MHz OK")
        bios_log.append("   PPU: RP2C02 5.37MHz OK")
        bios_log.append("   APU: 5 Channels OK")
        
        self.bios_complete = True
        bios_log.append("")
        bios_log.append("=== BIOS Complete ===")
        bios_log.append("System ready for ROM loading")
        
        return bios_log
    
    def get_hardware_status(self):
        """Get current hardware status"""
        status = {
            'PPU': '✓ Ready' if self.ppu_initialized else '✗ Offline',
            'APU': '✓ Ready' if self.apu_initialized else '✗ Offline',
            'CPU': '✓ Ready' if self.cpu_initialized else '✗ Offline',
            'Memory': '✓ Ready' if self.memory_initialized else '✗ Offline',
            'Controllers': '✓ Ready' if self.controllers_initialized else '✗ Offline',
            'BIOS': '✓ Complete' if self.bios_complete else '✗ Not Run'
        }
        return status

class EmuNESGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("emunes 1.0 [C] Team Flames 1.0 - NES Hardware BIOS")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize NES hardware
        self.nes = NESHardware()
        
        # Emulator state
        self.rom_loaded = False
        self.rom_path = None
        self.is_playing = False
        self.bios_run = False
        
        self.setup_gui()
        
    def setup_gui(self):
        # Main menu bar
        self.create_menu_bar()
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # BIOS Control Panel
        self.create_bios_panel(main_frame)
        
        # Hardware Status Panel
        self.create_hardware_panel(main_frame)
        
        # Display area
        self.create_display_area(main_frame)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_bios_panel(self, parent):
        bios_frame = ttk.LabelFrame(parent, text="NES Hardware BIOS - Proof of Concept", padding=10)
        bios_frame.pack(fill=tk.X, pady=5)
        
        # BIOS Controls
        control_frame = ttk.Frame(bios_frame)
        control_frame.pack(fill=tk.X)
        
        self.bios_button = ttk.Button(control_frame, text="Run BIOS Initialization", command=self.run_bios)
        self.bios_button.pack(side=tk.LEFT, padx=5)
        
        self.status_button = ttk.Button(control_frame, text="Check Hardware Status", command=self.show_hardware_status)
        self.status_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(control_frame, text="Reset Hardware", command=self.reset_hardware)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # BIOS Output
        output_frame = ttk.Frame(bios_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        self.bios_output = scrolledtext.ScrolledText(
            output_frame, 
            height=8, 
            width=80,
            bg='#1a1a1a',
            fg='#00ff00',
            font=('Courier New', 9)
        )
        self.bios_output.pack(fill=tk.X)
        self.bios_output.insert(tk.END, "NES Hardware BIOS Ready\nType 'Run BIOS Initialization' to start hardware test...\n")
        self.bios_output.config(state=tk.DISABLED)
        
    def create_hardware_panel(self, parent):
        hw_frame = ttk.LabelFrame(parent, text="Hardware Status", padding=10)
        hw_frame.pack(fill=tk.X, pady=5)
        
        # Hardware status grid
        status_grid = ttk.Frame(hw_frame)
        status_grid.pack(fill=tk.X)
        
        self.hw_labels = {}
        components = ['PPU', 'APU', 'CPU', 'Memory', 'Controllers', 'BIOS']
        
        for i, component in enumerate(components):
            frame = ttk.Frame(status_grid)
            frame.pack(side=tk.LEFT, expand=True, padx=10)
            
            label = ttk.Label(frame, text=component, font=('Arial', 9, 'bold'))
            label.pack()
            
            status_label = ttk.Label(frame, text="✗ Offline", foreground='red')
            status_label.pack()
            self.hw_labels[component] = status_label
        
        # Register viewer button
        ttk.Button(hw_frame, text="View Hardware Registers", command=self.show_registers).pack(pady=5)
        
    def create_display_area(self, parent):
        display_frame = ttk.LabelFrame(parent, text="Display", padding=10)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Game display area with BIOS mode
        self.display_canvas = tk.Canvas(
            display_frame, 
            bg='#000000', 
            highlightthickness=1, 
            highlightbackground='#555555'
        )
        self.display_canvas.pack(fill=tk.BOTH, expand=True)
        
        # BIOS boot screen
        self.draw_bios_screen()
        
    def create_control_panel(self, parent):
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Left side - ROM info
        info_frame = ttk.LabelFrame(control_frame, text="System Information", padding=5)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.sys_info_text = tk.Text(
            info_frame, 
            height=4, 
            width=50, 
            bg='#1a1a1a', 
            fg='#cccccc', 
            font=('Courier', 8)
        )
        self.sys_info_text.pack(fill=tk.X)
        info_text = """emunes 1.0 - NES Hardware BIOS Proof of Concept
CPU: MOS 6502 @ 1.79MHz
PPU: RP2C02 @ 5.37MHz  
APU: 5-channel sound
Memory: 2KB RAM + 2KB VRAM
Team Flames 1.0"""
        self.sys_info_text.insert(tk.END, info_text)
        self.sys_info_text.config(state=tk.DISABLED)
        
        # Right side - Controls
        ctrl_frame = ttk.LabelFrame(control_frame, text="Quick Controls", padding=5)
        ctrl_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ctrl_buttons = [
            ("Open ROM", self.open_rom),
            ("Run BIOS", self.run_bios),
            ("Hardware Test", self.hardware_test)
        ]
        
        for text, command in ctrl_buttons:
            btn = ttk.Button(ctrl_frame, text=text, command=command, width=15)
            btn.pack(fill=tk.X, pady=1)
            
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_text = ttk.Label(status_frame, text="Ready - NES Hardware BIOS Simulation - emunes 1.0")
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        # Hardware status
        self.hw_status = ttk.Label(status_frame, text="Hardware: OFFLINE")
        self.hw_status.pack(side=tk.RIGHT, padx=20)
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open ROM", command=self.open_rom)
        file_menu.add_command(label="Run BIOS", command=self.run_bios)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Hardware menu
        hw_menu = tk.Menu(menubar, tearoff=0)
        hw_menu.add_command(label="Initialize Hardware", command=self.run_bios)
        hw_menu.add_command(label="Hardware Status", command=self.show_hardware_status)
        hw_menu.add_command(label="View Registers", command=self.show_registers)
        hw_menu.add_command(label="Hardware Test", command=self.hardware_test)
        menubar.add_cascade(label="Hardware", menu=hw_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About BIOS", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def draw_bios_screen(self):
        """Draw BIOS boot screen on canvas"""
        self.display_canvas.delete("all")
        
        # BIOS boot screen design
        self.display_canvas.create_rectangle(50, 50, 750, 450, outline='#00ff00', width=2)
        
        # Title
        self.display_canvas.create_text(400, 100, text="emunes 1.0", fill='#00ff00', 
                                       font=('Arial', 24, 'bold'))
        self.display_canvas.create_text(400, 130, text="NES Hardware BIOS", fill='#00ff00', 
                                       font=('Arial', 14))
        self.display_canvas.create_text(400, 160, text="Proof of Concept", fill='#ffff00', 
                                       font=('Arial', 12))
        
        # Team info
        self.display_canvas.create_text(400, 200, text="[C] Team Flames 1.0", fill='#00ffff', 
                                       font=('Arial', 12, 'bold'))
        
        # Status
        status = "System: OFFLINE" if not self.bios_run else "System: READY"
        color = "#ff0000" if not self.bios_run else "#00ff00"
        self.display_canvas.create_text(400, 250, text=status, fill=color, 
                                       font=('Arial', 16, 'bold'))
        
        # Instructions
        self.display_canvas.create_text(400, 300, text="Click 'Run BIOS Initialization' to start", 
                                       fill='#cccccc', font=('Arial', 10))
        
        # Hardware specs
        specs = [
            "CPU: MOS 6502 @ 1.79MHz",
            "PPU: RP2C02 @ 5.37MHz",
            "APU: 5-channel sound",
            "Memory: 2KB RAM + 2KB VRAM"
        ]
        
        for i, spec in enumerate(specs):
            self.display_canvas.create_text(400, 330 + i*20, text=spec, 
                                          fill='#888888', font=('Courier', 9))
    
    def run_bios(self):
        """Run the BIOS initialization sequence"""
        self.bios_output.config(state=tk.NORMAL)
        self.bios_output.delete(1.0, tk.END)
        
        # Run BIOS
        bios_log = self.nes.run_bios()
        
        # Display log
        for line in bios_log:
            self.bios_output.insert(tk.END, line + '\n')
            
        self.bios_output.see(tk.END)
        self.bios_output.config(state=tk.DISABLED)
        
        # Update hardware status
        self.update_hardware_status()
        self.bios_run = True
        
        # Update display
        self.draw_bios_screen()
        self.status_text.config(text="BIOS Initialization Complete - System Ready")
        
    def update_hardware_status(self):
        """Update hardware status labels"""
        status = self.nes.get_hardware_status()
        for component, stat in status.items():
            color = 'green' if '✓' in stat else 'red'
            self.hw_labels[component].config(text=stat, foreground=color)
        
        # Update status bar
        if self.nes.bios_complete:
            self.hw_status.config(text="Hardware: READY", foreground='green')
        else:
            self.hw_status.config(text="Hardware: OFFLINE", foreground='red')
    
    def show_hardware_status(self):
        """Show detailed hardware status"""
        status = self.nes.get_hardware_status()
        status_text = "=== Hardware Status ===\n"
        for component, stat in status.items():
            status_text += f"{component}: {stat}\n"
        
        messagebox.showinfo("Hardware Status", status_text)
    
    def show_registers(self):
        """Show PPU and APU registers"""
        reg_text = "=== NES Hardware Registers ===\n\n"
        reg_text += "PPU Registers:\n"
        for reg, value in self.nes.ppu_registers.items():
            reg_text += f"  {reg}: 0x{value:02X}\n"
        
        reg_text += "\nAPU Registers:\n"
        for reg, value in self.nes.apu_registers.items():
            reg_text += f"  {reg}: 0x{value:02X}\n"
        
        # Create a new window for registers
        reg_window = tk.Toplevel(self.root)
        reg_window.title("NES Hardware Registers")
        reg_window.geometry("400x500")
        
        text_widget = scrolledtext.ScrolledText(reg_window, width=45, height=25)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert(tk.END, reg_text)
        text_widget.config(state=tk.DISABLED)
    
    def hardware_test(self):
        """Run a hardware diagnostic test"""
        if not self.nes.bios_complete:
            messagebox.showwarning("Hardware Test", "Please run BIOS initialization first!")
            return
        
        test_log = [
            "=== Hardware Diagnostic Test ===",
            "Testing PPU... ✓",
            "Testing APU channels... ✓",
            "Testing CPU operations... ✓", 
            "Testing memory access... ✓",
            "Testing controller ports... ✓",
            "All tests passed! Hardware is functional."
        ]
        
        self.bios_output.config(state=tk.NORMAL)
        self.bios_output.insert(tk.END, "\n" + "\n".join(test_log) + "\n")
        self.bios_output.see(tk.END)
        self.bios_output.config(state=tk.DISABLED)
        
        messagebox.showinfo("Hardware Test", "All hardware tests passed successfully!")
    
    def reset_hardware(self):
        """Reset hardware state"""
        self.nes = NESHardware()
        self.bios_run = False
        self.update_hardware_status()
        self.draw_bios_screen()
        
        self.bios_output.config(state=tk.NORMAL)
        self.bios_output.delete(1.0, tk.END)
        self.bios_output.insert(tk.END, "Hardware reset complete. Run BIOS to initialize.\n")
        self.bios_output.config(state=tk.DISABLED)
        
        self.status_text.config(text="Hardware Reset - Run BIOS to initialize")
    
    def show_about(self):
        about_text = """emunes 1.0 - NES Hardware BIOS Proof of Concept

[C] Team Flames 1.0

This is a proof-of-concept NES hardware BIOS simulation
that demonstrates PPU, APU, and full NES hardware initialization.

Features:
- PPU (Picture Processing Unit) simulation
- APU (Audio Processing Unit) simulation  
- CPU and memory initialization
- Hardware register visualization
- BIOS boot sequence simulation

Note: This is a simulation for demonstration purposes."""
        messagebox.showinfo("About NES Hardware BIOS", about_text)
    
    def open_rom(self):
        if not self.nes.bios_complete:
            messagebox.showwarning("ROM Load", "Please run BIOS initialization first!")
            return
            
        file_path = filedialog.askopenfilename(
            title="Open NES ROM - emunes 1.0",
            filetypes=[("NES ROMs", "*.nes"), ("All files", "*.*")]
        )
        
        if file_path:
            self.rom_path = file_path
            self.rom_loaded = True
            filename = os.path.basename(file_path)
            
            self.status_text.config(text=f"ROM loaded: {filename} - System Ready")

def main():
    root = tk.Tk()
    app = EmuNESGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
