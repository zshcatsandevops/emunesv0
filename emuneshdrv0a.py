#!/usr/bin/env python3
# emunes-tk.py – Minimal NES Emulator Core with Tkinter frontend
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

# ==============================
# CPU 6502 Core
# ==============================
class CPU6502:
    def __init__(self, memory):
        self.A = 0x00
        self.X = 0x00
        self.Y = 0x00
        self.SP = 0xFD
        self.PC = 0x0000
        self.flags = {'C':0,'Z':0,'I':0,'D':0,'B':0,'U':1,'V':0,'N':0}
        self.memory = memory

    def set_flag(self, f, c): self.flags[f] = 1 if c else 0
    def update_zn(self, v): self.set_flag('Z', v==0); self.set_flag('N', v & 0x80)

    def reset(self):
        lo,hi = self.memory[0xFFFC], self.memory[0xFFFD]
        self.PC = (hi<<8)|lo

    def step(self):
        opcode = self.memory[self.PC]; self.PC+=1
        if opcode == 0xA9:  # LDA #
            v=self.memory[self.PC]; self.PC+=1
            self.A=v; self.update_zn(self.A)
        elif opcode == 0xA2:  # LDX #
            v=self.memory[self.PC]; self.PC+=1
            self.X=v; self.update_zn(self.X)
        elif opcode == 0xE8:  # INX
            self.X=(self.X+1)&0xFF; self.update_zn(self.X)
        elif opcode == 0x00:  # BRK
            return False
        else:
            print(f"Unknown opcode {opcode:02X}"); return False
        return True

# ==============================
# NES ROM Loader
# ==============================
def load_nes_rom(path, memory):
    with open(path, "rb") as f:
        data = f.read()

    if data[0:4] != b"NES\x1A":
        raise ValueError("Not a valid iNES ROM")

    prg_size = data[4] * 16 * 1024   # PRG ROM size
    chr_size = data[5] * 8 * 1024    # CHR ROM size (ignored for now)

    prg_start = 16
    prg_data = data[prg_start:prg_start+prg_size]

    # Map PRG-ROM into 0x8000-0xFFFF
    for i,b in enumerate(prg_data):
        memory[0x8000+i] = b

    # If only 16KB PRG, mirror it into 0xC000-0xFFFF
    if prg_size == 16384:
        for i in range(16384):
            memory[0xC000+i] = prg_data[i]

    # Set reset vector to PRG-ROM start if not provided
    if memory[0xFFFC] == 0 and memory[0xFFFD] == 0:
        memory[0xFFFC] = 0x00
        memory[0xFFFD] = 0x80

    return len(prg_data)

# ==============================
# Emulator GUI
# ==============================
class EmuNESApp:
    def __init__(self, root):
        self.root=root; self.root.title("emunes 1.0 - NES Core Demo")
        self.memory=[0x00]*65536
        self.cpu=CPU6502(self.memory)
        self.running=False
        self.create_gui()

    def create_gui(self):
        menubar=tk.Menu(self.root)
        filemenu=tk.Menu(menubar,tearoff=0)
        filemenu.add_command(label="Open ROM (.nes)",command=self.open_rom)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",command=self.root.quit)
        menubar.add_cascade(label="File",menu=filemenu)
        self.root.config(menu=menubar)

        top=ttk.Frame(self.root); top.pack(fill=tk.X,padx=5,pady=5)
        mid=ttk.Frame(self.root); mid.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)

        ttk.Button(top,text="Reset",command=self.reset).pack(side=tk.LEFT,padx=5)
        ttk.Button(top,text="Step",command=self.step).pack(side=tk.LEFT,padx=5)
        ttk.Button(top,text="Run 20 instr",command=self.run20).pack(side=tk.LEFT,padx=5)

        self.reg_text=tk.Text(mid,width=30,height=15,bg="#1a1a1a",fg="#00ff00",font=("Courier",10))
        self.reg_text.pack(side=tk.LEFT,fill=tk.Y)
        self.log=scrolledtext.ScrolledText(mid,bg="#000000",fg="#cccccc",font=("Courier",9))
        self.log.pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)

        self.update_registers()

    def open_rom(self):
        path=filedialog.askopenfilename(title="Open NES ROM",
                                        filetypes=[("NES ROMs","*.nes"),("All files","*.*")])
        if not path: return
        try:
            size=load_nes_rom(path, self.memory)
            self.cpu.reset()
            self.log.insert(tk.END,f"Loaded {os.path.basename(path)}, {size} bytes PRG-ROM\n")
            self.update_registers()
        except Exception as e:
            self.log.insert(tk.END,f"Error loading ROM: {e}\n")

    def reset(self):
        self.cpu.reset()
        self.log.insert(tk.END,"CPU reset\n")
        self.update_registers()

    def step(self):
        ok=self.cpu.step()
        self.log.insert(tk.END,f"Step: PC={self.cpu.PC:04X} A={self.cpu.A:02X} X={self.cpu.X:02X}\n")
        self.update_registers()
        if not ok:
            self.log.insert(tk.END,"Execution stopped (BRK or invalid)\n")

    def run20(self):
        for _ in range(20):
            if not self.cpu.step():
                break
        self.log.insert(tk.END,"Ran 20 steps\n")
        self.update_registers()

    def update_registers(self):
        self.reg_text.config(state=tk.NORMAL)
        self.reg_text.delete(1.0,tk.END)
        r=self.cpu
        txt=f"""A={r.A:02X} X={r.X:02X} Y={r.Y:02X}
SP={r.SP:02X}  PC={r.PC:04X}
Flags: C{r.flags['C']} Z{r.flags['Z']} I{r.flags['I']} D{r.flags['D']}
       B{r.flags['B']} U{r.flags['U']} V{r.flags['V']} N{r.flags['N']}"""
        self.reg_text.insert(tk.END,txt)
        self.reg_text.config(state=tk.DISABLED)

def main():
    root=tk.Tk()
    app=EmuNESApp(root)
    root.geometry("800x600")
    root.mainloop()

if __name__=="__main__":
    main()
