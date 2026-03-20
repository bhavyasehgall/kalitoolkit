#!/usr/bin/env python3
# ===========================================================
#           PRO STEGHIDE GUI — PROFESSIONAL STYLE
# ===========================================================

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import os

# ===========================================================
# THEME DEFINITIONS
# ===========================================================

THEMES = {
    'Light': {
        'bg': '#f0f0f0',
        'text_bg': '#ffffff',
        'button_bg': '#1A7F3B',
        'clear_button_bg': '#8B0000',
        'accent': '#0D47A1',
        'text': '#333333',
        'sidebar_bg': '#e0e0e0',
        'frame_bg': '#ffffff',
        'highlight': '#e3f2fd',
        'button_hover': '#145C2B',
        'clear_hover': '#6B0000'
    },
    'Dark': {
        'bg': '#2d2d2d',
        'text_bg': '#1e1e1e',
        'button_bg': '#1E90FF',
        'clear_button_bg': '#E63E3E',
        'accent': '#0A3D7A',
        'text': '#e0e0e0',
        'sidebar_bg': '#252526',
        'frame_bg': '#333333',
        'highlight': '#44475a',
        'button_hover': '#1C86EE',
        'clear_hover': '#4B0000'
    },
    'Solarized': {
        'bg': '#fdf6e3',
        'text_bg': '#eee8d5',
        'button_bg': '#4A4A8F',
        'clear_button_bg': '#A51C1C',
        'accent': '#268bd2',
        'text': '#586e75',
        'sidebar_bg': '#eee8d5',
        'frame_bg': '#fdf6e3',
        'highlight': '#b58900',
        'button_hover': '#2A8E43',
        'clear_hover': '#B83030'
    },
    'Dracula': {
        'bg': '#282a36',
        'text_bg': '#44475a',
        'button_bg': '#3DC55D',
        'clear_button_bg': '#E63E3E',
        'accent': '#bd93f9',
        'text': '#f8f8f2',
        'sidebar_bg': '#21222C',
        'frame_bg': '#343746',
        'highlight': '#44475a',
        'button_hover': '#2A8E43',
        'clear_hover': '#B83030'
    }
}

current_theme = 'Light'

# ===========================================================
# THEME FUNCTION
# ===========================================================

def apply_theme(theme_name):
    global current_theme
    current_theme = theme_name
    theme = THEMES[theme_name]

    root.config(bg=theme['bg'])
    
    for frame in [sidebar_frame, main_frame, input_frame, button_frame, result_frame]:
        frame.config(style=f"{theme_name}.TFrame")
    
    for btn in [embed_btn, extract_btn, clear_btn, browse_cover_btn, browse_data_btn]:
        btn.config(style=f"{theme_name}.TButton")

    for widget in [cover_entry, data_entry, password_entry, text_input]:
        widget.config(bg=theme['text_bg'], fg=theme['text'], insertbackground=theme['text'])

    status_bar.config(bg=theme['accent'], fg='white')
    
    for name, btn in theme_buttons.items():
        if name == theme_name:
            btn.config(style=f"{theme_name}.Active.TButton")
        else:
            btn.config(style=f"{theme_name}.TButton")

    update_status(f"Theme changed to {theme_name}", "info")

# ===========================================================
# FILE FUNCTIONS
# ===========================================================

def browse_cover():
    path = filedialog.askopenfilename(title="Select Cover File", filetypes=[("Image Files","*.jpg *.png *.bmp"), ("All Files","*.*")])
    if path:
        cover_entry.delete(0, tk.END)
        cover_entry.insert(0, path)

def browse_data():
    path = filedialog.askopenfilename(title="Select Data File", filetypes=[("Text Files","*.txt"), ("All Files","*.*")])
    if path:
        data_entry.delete(0, tk.END)
        data_entry.insert(0, path)

def embed_data(event=None):
    cover = cover_entry.get().strip()
    passwd = password_entry.get().strip()
    
    if use_text_var.get():
        text_content = text_input.get("1.0", tk.END).strip()
        if not text_content:
            update_status("No text to embed", "error")
            return
        temp_file = "temp_embed.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(text_content)
        data_to_use = temp_file
    else:
        data_to_use = data_entry.get().strip()
        if not data_to_use:
            update_status("No data file selected", "error")
            return

    if not cover:
        update_status("Cover file missing", "error")
        return

    cmd = ['steghide', 'embed', '-cf', cover, '-ef', data_to_use, '-p', passwd, '-f']
    try:
        subprocess.run(cmd, check=True)
        update_status("Data embedded successfully!", "success")
    except subprocess.CalledProcessError as e:
        update_status(f"Embedding failed: {e}", "error")
    finally:
        if use_text_var.get() and os.path.exists(temp_file):
            os.remove(temp_file)

def extract_data(event=None):
    cover_file = cover_entry.get().strip()
    passwd = password_entry.get().strip()
    if not cover_file:
        update_status("Select a cover file first", "error")
        return

    try:
        temp_out = "extracted_temp.txt"
        cmd = ['steghide', 'extract', '-sf', cover_file, '-xf', temp_out, '-p', passwd, '-f']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            with open(temp_out, 'r', encoding='utf-8', errors='ignore') as f:
                extracted_text = f.read()
            result_display.config(state='normal')
            result_display.delete("1.0", tk.END)
            result_display.insert(tk.END, extracted_text)
            result_display.config(state='disabled')
            os.remove(temp_out)
            update_status("Extraction successful", "success")
        else:
            update_status(f"Extraction failed: {result.stderr}", "error")
            messagebox.showerror("Error", result.stderr)
    except Exception as e:
        update_status(f"Error: {str(e)}", "error")
        messagebox.showerror("Error", str(e))

def clear_all(event=None):
    cover_entry.delete(0, tk.END)
    data_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    text_input.delete("1.0", tk.END)
    result_display.config(state='normal')
    result_display.delete("1.0", tk.END)
    result_display.config(state='disabled')
    update_status("Cleared all fields", "info")

def update_status(msg, msg_type="info"):
    status_var.set(msg)
    if msg_type == "error":
        status_bar.config(bg="#ff4444", fg="white")
    elif msg_type == "success":
        status_bar.config(bg="#4CAF50", fg="white")
    else:
        status_bar.config(bg=THEMES[current_theme]['accent'], fg="white")

def copy_to_clipboard(widget):
    text = widget.get("1.0", tk.END).strip()
    if text:
        root.clipboard_clear()
        root.clipboard_append(text)
        update_status("Copied to clipboard", "success")
    else:
        update_status("Nothing to copy", "error")

# ===========================================================
# GUI SETUP
# ===========================================================

def create_gui():
    global root, sidebar_frame, main_frame, input_frame, result_frame, button_frame
    global cover_entry, data_entry, password_entry
    global embed_btn, extract_btn, clear_btn, browse_cover_btn, browse_data_btn
    global status_bar, status_var, theme_buttons, use_text_var, text_input, result_display

    root = tk.Tk()
    root.title("PRO STEGHIDE GUI")
    root.geometry("850x500")
    root.minsize(800, 450)

    # Style
    style = ttk.Style()
    for theme_name, theme in THEMES.items():
        style.configure(f"{theme_name}.TFrame", background=theme['bg'])
        style.configure(f"{theme_name}.TButton", background=theme['button_bg'], foreground='#000000', font=('Segoe UI', 10, 'bold'))
        style.map(f"{theme_name}.TButton", background=[('active', theme['button_hover'])])
        style.configure(f"{theme_name}.Active.TButton", background=theme['accent'], foreground='white', font=('Segoe UI', 10, 'bold'))

    # Main container
    main_container = ttk.Frame(root)
    main_container.pack(fill=tk.BOTH, expand=True)

    # Sidebar
    sidebar_frame = ttk.Frame(main_container, width=150, style=f"{current_theme}.TFrame")
    sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

    ttk.Label(sidebar_frame, text="Themes", font=('Segoe UI', 10, 'bold')).pack(pady=(10,5), anchor='w')
    theme_buttons = {}
    for theme in THEMES:
        btn = ttk.Button(sidebar_frame, text=theme, command=lambda t=theme: apply_theme(t), style=f"{current_theme}.TButton")
        btn.pack(fill=tk.X, pady=2, padx=5)
        theme_buttons[theme] = btn

    ttk.Separator(sidebar_frame, orient='horizontal').pack(fill=tk.X, pady=10)
    ttk.Label(sidebar_frame, text="Shortcuts", font=('Segoe UI', 10, 'bold')).pack(pady=(0,5), anchor='w')
    ttk.Label(sidebar_frame, text="Ctrl+E: Embed", font=('Segoe UI', 8)).pack(anchor='w', padx=5)
    ttk.Label(sidebar_frame, text="Ctrl+X: Extract", font=('Segoe UI', 8)).pack(anchor='w', padx=5)
    ttk.Label(sidebar_frame, text="Ctrl+C: Copy Output", font=('Segoe UI', 8)).pack(anchor='w', padx=5)
    ttk.Label(sidebar_frame, text="Esc: Clear", font=('Segoe UI', 8)).pack(anchor='w', padx=5)

    # Main frame
    main_frame = ttk.Frame(main_container, padding=10, style=f"{current_theme}.TFrame")
    main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Input frame
    input_frame = ttk.LabelFrame(main_frame, text="Files & Password", padding=10, style=f"{current_theme}.TFrame")
    input_frame.pack(fill=tk.X, pady=(0,10))

    tk.Label(input_frame, text="Cover File:", anchor='w').grid(row=0, column=0, sticky='w', padx=5, pady=5)
    cover_entry = tk.Entry(input_frame)
    cover_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    browse_cover_btn = ttk.Button(input_frame, text="Browse", command=browse_cover, style=f"{current_theme}.TButton")
    browse_cover_btn.grid(row=0, column=2, padx=5, pady=5)

    tk.Label(input_frame, text="Data File:", anchor='w').grid(row=1, column=0, sticky='w', padx=5, pady=5)
    data_entry = tk.Entry(input_frame)
    data_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
    browse_data_btn = ttk.Button(input_frame, text="Browse", command=browse_data, style=f"{current_theme}.TButton")
    browse_data_btn.grid(row=1, column=2, padx=5, pady=5)

    tk.Label(input_frame, text="Password:", anchor='w').grid(row=2, column=0, sticky='w', padx=5, pady=5)
    password_entry = tk.Entry(input_frame, show='*')
    password_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

    # Use direct text
    use_text_var = tk.BooleanVar(value=False)
    use_text_chk = tk.Checkbutton(input_frame, text="Use Direct Text", variable=use_text_var,
                                  bg=THEMES[current_theme]['bg'], fg=THEMES[current_theme]['text'])
    use_text_chk.grid(row=3, column=0, sticky='w', padx=5, pady=5)

    text_input = scrolledtext.ScrolledText(input_frame, height=5, font=("Consolas", 10),
                                           bg=THEMES[current_theme]['text_bg'],
                                           fg=THEMES[current_theme]['text'],
                                           wrap=tk.WORD)
    text_input.grid(row=4, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
    input_frame.rowconfigure(4, weight=1)
    input_frame.columnconfigure(1, weight=1)

    # Buttons frame
    button_frame = ttk.Frame(main_frame, style=f"{current_theme}.TFrame")
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    embed_btn = ttk.Button(button_frame, text=" EMBED (Ctrl+E) ", command=embed_data, style=f"{current_theme}.TButton")
    embed_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=3)

    extract_btn = ttk.Button(button_frame, text=" EXTRACT (Ctrl+X) ", command=extract_data, style=f"{current_theme}.TButton")
    extract_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=3)

    clear_btn = ttk.Button(button_frame, text=" CLEAR (Esc) ", command=clear_all, style=f"{current_theme}.TButton")
    clear_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=3)

    # Result Section
    result_frame = ttk.LabelFrame(main_frame, text=" Extracted Data ", padding=10, style=f"{current_theme}.TLabelframe")
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(10,10))

    result_display = scrolledtext.ScrolledText(result_frame, height=15, font=("Consolas", 11),
                                               bg=THEMES[current_theme]['text_bg'],
                                               fg=THEMES[current_theme]['text'],
                                               state='disabled',
                                               insertbackground=THEMES[current_theme]['text'],
                                               selectbackground=THEMES[current_theme]['accent'],
                                               padx=10, pady=10, wrap=tk.WORD)
    result_display.pack(fill=tk.BOTH, expand=True)

    # Status bar
    status_var = tk.StringVar()
    status_var.set("Ready")
    status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                          bg=THEMES[current_theme]['accent'], fg="white", font=("Segoe UI", 9))
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Keyboard bindings
    root.bind("<Control-e>", embed_data)
    root.bind("<Control-E>", embed_data)
    root.bind("<Control-x>", extract_data)
    root.bind("<Control-X>", extract_data)
    root.bind("<Escape>", clear_all)
    root.bind("<Control-c>", lambda e: copy_to_clipboard(result_display))

    apply_theme(current_theme)

if __name__ == "__main__":
    create_gui()
    root.mainloop()
