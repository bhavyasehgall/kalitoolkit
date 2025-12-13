#!/usr/bin/env python3
# ===========================================================
#           PRO AUTO DECODER GUI — FULL MIXED LAYER
# ===========================================================

# History configuration
HISTORY_FILE = "decoder_history.json"
HISTORY_LIMIT = 100
history = []

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import base64, binascii, string, json, os
from tkinter import font as tkfont
import webbrowser
from datetime import datetime

# Theme definitions
THEMES = {
    'Light': {
    'bg': '#f0f0f0',
    'text_bg': '#ffffff',
    'button_bg': '#1A7F3B',       # Brighter green
    'clear_button_bg': '#8B0000',
    'accent': '#0D47A1',
    'text': '#333333',
    'sidebar_bg': '#e0e0e0',
    'frame_bg': '#ffffff',
    'highlight': '#e3f2fd',
    'button_hover': '#145C2B',    # Slightly darker for hover
    'clear_hover': '#6B0000'
    },
    'Dark': {
    'bg': '#2d2d2d',
    'text_bg': '#1e1e1e',
    'button_bg': '#1E90FF',        # New blue buttons
    'clear_button_bg': '#E63E3E',  # Red for clear button
    'accent': '#0A3D7A',           # Dark blue accent
    'text': '#e0e0e0',
    'disabled': '#757575',
    'sidebar_bg': '#252526',
    'frame_bg': '#333333',
    'highlight': '#44475a',
    'button_hover': '#1C86EE',     # Hover effect for new buttons
    'clear_hover': '#4B0000'       # Hover for clear button
    },
    'Solarized': {
        'bg': '#fdf6e3',
        'text_bg': '#eee8d5',
        'button_bg': '#4A4A8F',  # Darker purple for better visibility
        'clear_button_bg': '#A51C1C',  # Darker red for better visibility
        'accent': '#268bd2',
        'text': '#586e75',
        'disabled': '#93a1a1',
        'sidebar_bg': '#eee8d5',
        'frame_bg': '#fdf6e3',
        'highlight': '#b58900',
        'button_hover': '#2A8E43',  # Even darker green for hover
        'clear_hover': '#B83030'    # Even darker red for hover
    },
    'Dracula': {
        'bg': '#282a36',
        'text_bg': '#44475a',
        'button_bg': '#3DC55D',  # Darker green for better visibility
        'clear_button_bg': '#E63E3E',  # Darker red for better visibility
        'accent': '#bd93f9',
        'text': '#f8f8f2',
        'disabled': '#6272a4',
        'sidebar_bg': '#21222C',
        'frame_bg': '#343746',
        'highlight': '#44475a',
        'button_hover': '#2A8E43',  # Even darker green for hover
        'clear_hover': '#B83030'    # Even darker red for hover
    }
}

# Set default theme
current_theme = 'Light'

def apply_theme(theme_name):
    global current_theme
    current_theme = theme_name
    theme = THEMES[theme_name]
    
    # Update root window
    root.config(bg=theme['bg'])
    
    # Update menu bar
    menubar.config(bg=theme['bg'], fg=theme['text'])
    
    # Update frames
    for frame in [main_frame, input_frame, result_frame, button_frame, sidebar_frame]:
        frame.config(style=f"{theme_name}.TFrame")
    
    # Update text areas
    text_input.config(
        bg=theme['text_bg'],
        fg=theme['text'],
        insertbackground=theme['text'],
        selectbackground=theme['accent']
    )
    
    result_display.config(
        bg=theme['text_bg'],
        fg=theme['text'],
        insertbackground=theme['text'],
        selectbackground=theme['accent']
    )
    
    # Update buttons
    for btn in [decode_btn, clear_btn]:
        btn.config(style=f"{theme_name}.TButton")
    
    # Update status bar
    status_bar.config(
        bg=theme['accent'],
        fg='white' if theme_name != 'Light' else 'white'
    )
    
    # Update theme buttons
    for name, btn in theme_buttons.items():
        if name == theme_name:
            btn.config(style=f"{theme_name}.Active.TButton")
        else:
            btn.config(style=f"{theme_name}.TButton")
    
    # Update tags
    text_input.tag_configure("highlight", background=theme['highlight'])
    result_display.tag_configure("header", font=('Arial', 10, 'bold'), foreground=theme['accent'])
    result_display.tag_configure("output", font=('Consolas', 10), foreground=theme['text'])
    
    update_status(f"Theme changed to {theme_name}", "info")

# ===========================================================
# DECODERS
# ===========================================================

# ASCII decimal -> binary -> text
def ascii_decimal_to_binary(s):
    try:
        return "".join(chr(int(n)) for n in s.split())
    except:
        return None

def binary_to_text(s):
    try:
        return "".join(chr(int(b, 2)) for b in s.split())
    except:
        return None

# HEX
def decode_hex(s):
    try:
        return binascii.unhexlify(s.replace(" ", "")).decode(errors="replace")
    except:
        return None

# ASCII Decimal
def decode_ascii_decimal(s):
    try:
        nums = s.split()
        return "".join(chr(int(n)) for n in nums)
    except:
        return None

# Binary
def decode_binary(s):
    try:
        bits = s.split()
        return "".join(chr(int(b, 2)) for b in bits)
    except:
        return None

# Base64
def decode_base64(s):
    try:
        return base64.b64decode(s + "===").decode(errors="replace")
    except:
        return None

# Base32
def decode_base32(s):
    try:
        padded = s + "=" * ((8 - (len(s) % 8)) % 8)
        return base64.b32decode(padded).decode(errors="replace")
    except:
        return None

# Base58
BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def decode_base58(s):
    try:
        num = 0
        for c in s:
            num = num * 58 + BASE58.index(c)
        return num.to_bytes((num.bit_length() + 7) // 8, "big").decode(errors="replace")
    except:
        return None

# ROT13
def decode_rot13(s):
    letters = sum(c.isalpha() for c in s)
    if letters / max(len(s), 1) < 0.6:
        return None
    rot = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
    )
    return s.translate(rot)

# ROT47
def decode_rot47(s):
    if not all('!' <= c <= '~' or c.isspace() for c in s):
        return None
    return "".join(chr(33 + ((ord(c) - 33 + 47) % 94)) if '!' <= c <= '~' else c for c in s)

# MORSE
MORSE = {
    '.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F',
    '--.':'G','....':'H','..':'I','.---':'J','-.-':'K','.-..':'L',
    '--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q','.-.':'R',
    '...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X',
    '-.--':'Y','--..':'Z','-----':'0','.----':'1','..---':'2',
    '...--':'3','....-':'4','.....':'5','-....':'6','--...':'7',
    '---..':'8','----.':'9'
}
def decode_morse(s):
    try:
        parts = s.split()
        out = "".join(MORSE.get(p, "?") for p in parts)
        return out if is_good_text(out) else None
    except:
        return None

# TEXT VALIDATION
def is_good_text(s):
    if not s:
        return False
    printable = sum(c in string.printable for c in s)
    letters = sum(c.isalnum() or c in " .,!?-_'\"" for c in s)
    return (printable / len(s) > 0.9) and (letters / len(s) > 0.4)

# AUTO DECODER
def auto_decode(s):
    bin_str = ascii_decimal_to_binary(s)
    if bin_str:
        text_out = binary_to_text(bin_str)
        if text_out:
            return "[ASCII decimal -> Binary -> Text]", text_out

    if all(c in ".-/ " for c in s):
        out = decode_morse(s)
        if out:
            return "Morse", out

    if all(c in string.hexdigits + " " for c in s) and any(c.isalpha() for c in s):
        out = decode_hex(s)
        if out and is_good_text(out):
            return "Hex", out

    if all(c.isdigit() or c.isspace() for c in s):
        out = decode_ascii_decimal(s)
        if out and is_good_text(out):
            return "ASCII Decimal", out

    if all(c in "01 " for c in s):
        out = decode_binary(s)
        if out and is_good_text(out):
            return "Binary", out

    if all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567=" for c in s):
        out = decode_base32(s)
        if out and is_good_text(out):
            return "Base32", out

    out = decode_base64(s)
    if out and is_good_text(out):
        return "Base64", out

    if all(c in BASE58 for c in s.replace(" ","")):
        out = decode_base58(s)
        if out and is_good_text(out):
            return "Base58", out

    out = decode_rot13(s)
    if out:
        return "ROT13", out

    out = decode_rot47(s)
    if out:
        return "ROT47", out

    return "Unknown / Possibly Custom Cipher", None

# ===========================================================
# GUI SETUP
# ===========================================================

def load_history():
    """Load history from file if it exists"""
    global history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history
        except:
            return []
    return []

def save_history():
    """Save history to file"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_to_history(input_text, result, enc_type):
    """Add a new entry to the history"""
    global history
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        'timestamp': timestamp,
        'input': input_text,
        'result': result,
        'type': enc_type
    }
    history.insert(0, entry)
    if len(history) > HISTORY_LIMIT:
        history = history[:HISTORY_LIMIT]
    save_history()

def show_history():
    """Show history window with previous decodings"""
    history_window = tk.Toplevel(root)
    history_window.title("Decoding History")
    history_window.geometry("800x600")
    
    # Apply theme
    history_window.config(bg=THEMES[current_theme]['bg'])
    
    # Create main container
    container = ttk.Frame(history_window, style=f"{current_theme}.TFrame")
    container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Title
    ttk.Label(
        container,
        text="Decoding History",
        font=('Segoe UI', 14, 'bold'),
        style=f"{current_theme}.TLabel"
    ).pack(pady=(0, 10))
    
    # Create listbox with scrollbar
    frame = ttk.Frame(container, style=f"{current_theme}.TFrame")
    frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    history_list = tk.Listbox(
        frame,
        yscrollcommand=scrollbar.set,
        font=('Segoe UI', 10),
        bg=THEMES[current_theme]['text_bg'],
        fg=THEMES[current_theme]['text'],
        selectbackground=THEMES[current_theme]['accent'],
        selectforeground='white',
        borderwidth=0,
        highlightthickness=0
    )
    history_list.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=history_list.yview)
    
    # Add history items to listbox
    for entry in history:
        preview = f"[{entry['timestamp']}] {entry['type']}: {entry['input'][:50]}..."
        history_list.insert(tk.END, preview)
    
    def view_selected():
        selection = history_list.curselection()
        if not selection:
            return
            
        idx = selection[0]
        entry = history[idx]
        
        # Create view window
        view_window = tk.Toplevel(history_window)
        view_window.title("View History Entry")
        view_window.geometry("700x500")
        
        # Apply theme
        view_window.config(bg=THEMES[current_theme]['bg'])
        
        # Create main container
        container = ttk.Frame(view_window, style=f"{current_theme}.TFrame")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Entry info
        info_frame = ttk.Frame(container, style=f"{current_theme}.TFrame")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            info_frame,
            text=f"Timestamp: {entry['timestamp']}",
            style=f"{current_theme}.TLabel"
        ).pack(anchor='w')
        
        ttk.Label(
            info_frame,
            text=f"Encoding Type: {entry['type']}",
            style=f"{current_theme}.TLabel"
        ).pack(anchor='w')
        
        # Input section
        ttk.Label(
            container,
            text="Input:",
            font=('Segoe UI', 10, 'bold'),
            style=f"{current_theme}.TLabel"
        ).pack(anchor='w')
        
        input_text = scrolledtext.ScrolledText(
            container,
            height=8,
            font=("Consolas", 10),
            bg=THEMES[current_theme]['text_bg'],
            fg=THEMES[current_theme]['text'],
            wrap=tk.WORD
        )
        input_text.insert('1.0', entry['input'])
        input_text.config(state='disabled')
        input_text.pack(fill=tk.X, pady=(0, 10))
        
        # Output section
        ttk.Label(
            container,
            text="Output:",
            font=('Segoe UI', 10, 'bold'),
            style=f"{current_theme}.TLabel"
        ).pack(anchor='w')
        
        output_text = scrolledtext.ScrolledText(
            container,
            height=12,
            font=("Consolas", 10),
            bg=THEMES[current_theme]['text_bg'],
            fg=THEMES[current_theme]['text'],
            wrap=tk.WORD
        )
        output_text.insert('1.0', entry['result'])
        output_text.config(state='disabled')
        output_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(container, style=f"{current_theme}.TFrame")
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        def load_entry():
            text_input.delete('1.0', tk.END)
            text_input.insert('1.0', entry['input'])
            result_display.config(state='normal')
            result_display.delete('1.0', tk.END)
            result_display.insert('1.0', entry['result'])
            result_display.config(state='disabled')
            view_window.destroy()
            history_window.destroy()
            text_input.focus_set()
            update_status(f"Loaded history entry from {entry['timestamp']}", "success")
        
        ttk.Button(
            btn_frame,
            text="Load This Entry",
            command=load_entry,
            style=f"{current_theme}.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Close",
            command=view_window.destroy,
            style=f"{current_theme}.TButton"
        ).pack(side=tk.RIGHT, padx=5)
    
    # Button frame
    btn_frame = ttk.Frame(container, style=f"{current_theme}.TFrame")
    btn_frame.pack(fill=tk.X, pady=(10, 0))
    
    ttk.Button(
        btn_frame,
        text="View Selected",
        command=view_selected,
        style=f"{current_theme}.TButton"
    ).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(
        btn_frame,
        text="Close",
        command=history_window.destroy,
        style=f"{current_theme}.TButton"
    ).pack(side=tk.RIGHT, padx=5)
    
    # Bind double-click to view entry
    history_list.bind('<Double-1>', lambda e: view_selected())

def decode_input(event=None):
    user_text = text_input.get("1.0", tk.END).strip()
    if not user_text:
        update_status("Error: No input provided", "error")
        return
        
    update_status("Decoding...", "info")
    root.update()
    
    try:
        enc_type, result = auto_decode(user_text)
        result_display.config(state='normal')
        result_display.delete("1.0", tk.END)
        
        # Add detected encoding type with styling
        result_display.tag_configure("header", font=('Arial', 10, 'bold'))
        result_display.insert(tk.END, "Detected: ", "header")
        result_display.insert(tk.END, f"{enc_type}\n\n")
        
        if result:
            # Add output with styling
            result_display.tag_configure("output", font=('Consolas', 10))
            result_display.insert(tk.END, f"{result}", "output")
            update_status("Decoding completed successfully", "success")
            
            # Add to history
            add_to_history(user_text, result, enc_type)
        else:
            result_display.insert(tk.END, "[!] Unable to decode automatically.", "error")
            update_status("Decoding failed", "error")
            
    except Exception as e:
        update_status(f"Error: {str(e)}", "error")
        messagebox.showerror("Error", f"An error occurred during decoding: {str(e)}")
    finally:
        result_display.config(state='disabled')

def clear_text(event=None):
    text_input.delete("1.0", tk.END)
    result_display.config(state='normal')
    result_display.delete("1.0", tk.END)
    result_display.config(state='disabled')
    update_status("Cleared all content", "info")

def update_status(message, msg_type="info"):
    """Update status bar with message and appropriate color"""
    if 'status_bar' not in globals() or not status_bar.winfo_exists():
        return  # Skip if status bar not initialized yet
        
    status_var.set(message)
    theme = THEMES.get(current_theme, THEMES['Light'])  # Fallback to Light theme
    
    if msg_type == "error":
        status_bar.config(
            bg=theme.get('error_bg', '#ffcdd2'),
            fg=theme.get('error_fg', '#b71c1c')
        )
    elif msg_type == "success":
        status_bar.config(
            bg=theme.get('success_bg', '#c8e6c9'),
            fg=theme.get('success_fg', '#1b5e20')
        )
    else:  # info
        status_bar.config(
            bg=theme.get('accent', '#2196F3'),
            fg='white'
        )
        
def copy_to_clipboard():
    """Copy result to clipboard"""
    if result_display.compare("end-1c", "!=", "1.0"):  # If not empty
        text = result_display.get("1.0", tk.END).strip()
        root.clipboard_clear()
        root.clipboard_append(text)
        update_status("Copied to clipboard", "success")
    else:
        update_status("No content to copy", "error")

def show_about():
    """Show about dialog"""
    about_text = """PRO AUTO DECODER GUI

A powerful text decoder that supports multiple encoding formats:
- Base64, Base32, Base58
- Hex
- Binary
- ASCII Decimal
- ROT13, ROT47
- Morse Code

Created with Python and Tkinter
Version 1.0.0"""
    messagebox.showinfo("About", about_text)

def create_gui():
    global root, text_input, result_display, status_var, status_bar, \
           main_frame, input_frame, result_frame, button_frame, sidebar_frame, \
           decode_btn, clear_btn, theme_buttons, menubar
    
    # Main window setup
    root = tk.Tk()
    root.title("PRO AUTO DECODER")
    root.geometry("900x650")
    root.minsize(800, 600)
    
    # Set default theme
    global current_theme
    current_theme = 'Light'
    
    # Apply theme to root window
    root.config(bg=THEMES[current_theme]['bg'])
    
    # Set application icon (if available)
    try:
        root.iconbitmap("icon.ico")  # Place an icon.ico file in the same directory
    except:
        pass  # Use default icon if custom icon not found
    
    # Configure styles for each theme
    style = ttk.Style()
    
    # Configure base styles
    style.configure('.', font=('Segoe UI', 10))
    
    # Configure styles for each theme
    for theme_name, theme in THEMES.items():
        # Frame style
        style.configure(f"{theme_name}.TFrame", background=theme['bg'])
        
        # Button style with consistent sizing
        style.configure(
            f"{theme_name}.TButton",
            padding=8,
            relief="raised",
            borderwidth=2,
            background=theme['button_bg'],
            foreground='#000000',  # Black text for better visibility
            font=('Segoe UI', 10, 'bold'),
            borderradius=4,
            width=15  # Fixed width for all buttons
        )
        style.map(
            f"{theme_name}.TButton",
            background=[
                ('active', theme.get('button_hover', theme['button_bg'])),
                ('!disabled', theme['button_bg'])
            ],
            foreground=[('active', '#000000'), ('!disabled', '#000000')],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')],
            bordercolor=[('focus', theme['accent'])]
        )
        
        # Clear button style with same dimensions as main button
        style.configure(
            f"{theme_name}.Clear.TButton",
            padding=8,
            relief="raised",
            borderwidth=2,
            background=theme['clear_button_bg'],
            foreground='#000000',  # Black text for better visibility
            font=('Segoe UI', 10, 'bold'),
            borderradius=4,
            width=15  # Same fixed width as main button
        )
        style.map(
            f"{theme_name}.Clear.TButton",
            background=[
                ('active', theme.get('clear_hover', theme['clear_button_bg'])),
                ('!disabled', theme['clear_button_bg'])
            ],
            foreground=[('active', '#000000'), ('!disabled', '#000000')],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')],
            bordercolor=[('focus', theme['accent'])]
        )
        
        # Active button style (for selected theme)
        style.configure(
            f"{theme_name}.Active.TButton",
            padding=6,
            relief="sunken",
            background=theme['accent'],
            foreground=theme['accent'],
            font=('Segoe UI', 9, 'bold')
        )
        
        # LabelFrame style
        style.configure(
            f"{theme_name}.TLabelframe",
            background=theme['bg'],
            foreground=theme['text']
        )
        style.configure(
            f"{theme_name}.TLabelframe.Label",
            background=theme['bg'],
            foreground=theme['accent'],
            font=('Segoe UI', 9, 'bold')
        )
    
    # Set initial theme
    current_theme = 'Light'
    
    # Create menu bar
    menubar = tk.Menu(root, bg=THEMES[current_theme]['bg'], fg=THEMES[current_theme]['text'])
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0, bg=THEMES[current_theme]['bg'], fg=THEMES[current_theme]['text'])
    file_menu.add_command(label="Clear All", command=clear_text, accelerator="Ctrl+C")
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    
    # Edit menu
    edit_menu = tk.Menu(menubar, tearoff=0, bg=THEMES[current_theme]['bg'], fg=THEMES[current_theme]['text'])
    edit_menu.add_command(label="Copy Result", command=copy_to_clipboard, accelerator="Ctrl+Shift+C")
    edit_menu.add_separator()
    edit_menu.add_command(label="History", command=show_history, accelerator="Ctrl+H")
    menubar.add_cascade(label="Edit", menu=edit_menu)
    
    # View menu
    view_menu = tk.Menu(menubar, tearoff=0, bg=THEMES[current_theme]['bg'], fg=THEMES[current_theme]['text'])
    for theme in THEMES:
        view_menu.add_command(
            label=theme,
            command=lambda t=theme: apply_theme(t)
        )
    menubar.add_cascade(label="Themes", menu=view_menu)
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0, bg=THEMES[current_theme]['bg'], fg=THEMES[current_theme]['text'])
    help_menu.add_command(label="About", command=show_about)
    menubar.add_cascade(label="Help", menu=help_menu)
    
    root.config(menu=menubar)
    
    # Create main container with sidebar
    main_container = ttk.Frame(root)
    main_container.pack(fill=tk.BOTH, expand=True)
    
    # Create sidebar
    sidebar_frame = ttk.Frame(main_container, width=150, style=f"{current_theme}.TFrame")
    sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
    
    # Add theme buttons to sidebar
    ttk.Label(sidebar_frame, text="Themes", font=('Segoe UI', 10, 'bold')).pack(pady=(10, 5), anchor='w')
    
    theme_buttons = {}
    for theme in THEMES:
        btn = ttk.Button(
            sidebar_frame,
            text=theme,
            command=lambda t=theme: apply_theme(t),
            style=f"{current_theme}.TButton"
        )
        btn.pack(fill=tk.X, pady=2, padx=5)
        theme_buttons[theme] = btn
    
    # Add separator
    ttk.Separator(sidebar_frame, orient='horizontal').pack(fill=tk.X, pady=10)
    
    # Add other sidebar elements here if needed
    ttk.Label(sidebar_frame, text="Shortcuts", font=('Segoe UI', 10, 'bold')).pack(pady=(0, 5), anchor='w')
    ttk.Label(sidebar_frame, text="Enter: Decode", font=('Segoe UI', 8)).pack(anchor='w', padx=5)
    ttk.Label(sidebar_frame, text="Esc: Clear", font=('Segoe UI', 8)).pack(anchor='w', padx=5)
    ttk.Label(sidebar_frame, text="Ctrl+Shift+C: Copy", font=('Segoe UI', 8)).pack(anchor='w', padx=5)
    ttk.Label(sidebar_frame, text="Ctrl+H: History", font=('Segoe UI', 8)).pack(anchor='w', padx=5)
    
    # Add separator and History button to sidebar
    ttk.Separator(sidebar_frame, orient='horizontal').pack(fill=tk.X, pady=10)
    history_btn = ttk.Button(
        sidebar_frame,
        text=" History (Ctrl+H)",
        command=show_history,
        style=f"{current_theme}.TButton"
    )
    history_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
    
    # Main content area
    main_frame = ttk.Frame(main_container, padding="10", style=f"{current_theme}.TFrame")
    main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Input Section
    input_frame = ttk.LabelFrame(
        main_frame,
        text=" Input Text ",
        padding=10,
        style=f"{current_theme}.TLabelframe"
    )
    input_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
    
    text_input = scrolledtext.ScrolledText(
        input_frame, 
        height=8, 
        font=("Consolas", 11), 
        bg=THEMES[current_theme]['text_bg'], 
        fg=THEMES[current_theme]['text'],
        insertbackground=THEMES[current_theme]['text'],
        selectbackground=THEMES[current_theme]['accent'],
        padx=10,
        pady=10,
        wrap=tk.WORD
    )
    text_input.pack(fill=tk.BOTH, expand=True)
    
    # Buttons Frame
    button_frame = ttk.Frame(main_frame, style=f"{current_theme}.TFrame")
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    
    
    # Bottom padding frame for main content
    ttk.Frame(main_frame, height=5, style=f"{current_theme}.TFrame").pack(side=tk.BOTTOM, fill=tk.X)
    
    # Add Decode button to button frame
    decode_btn = ttk.Button(
        button_frame, 
        text=" DECODE (Enter)", 
        command=decode_input,
        style=f"{current_theme}.TButton"
    )
    decode_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=3)

     # Add Clear button
    clear_btn = ttk.Button(
        button_frame, 
        text=" CLEAR (Esc)", 
        command=clear_text,
        style=f"{current_theme}.Clear.TButton"
    )
    clear_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=3)
    
    # Result Section
    result_frame = ttk.LabelFrame(
        main_frame,
        text=" Decoded Output ",
        padding=10,
        style=f"{current_theme}.TLabelframe"
    )
    result_frame.pack(fill=tk.BOTH, expand=True)
    
    result_display = scrolledtext.ScrolledText(
        result_frame,
        height=15,
        font=("Consolas", 11),
        bg=THEMES[current_theme]['text_bg'],
        fg=THEMES[current_theme]['text'],
        state='disabled',
        insertbackground=THEMES[current_theme]['text'],
        selectbackground=THEMES[current_theme]['accent'],
        padx=10,
        pady=10,
        wrap=tk.WORD
    )
    result_display.pack(fill=tk.BOTH, expand=True)
    
    # Status Bar
    status_var = tk.StringVar()
    status_var.set("Ready")
    status_bar = tk.Label(
        root, 
        textvariable=status_var, 
        bd=1, 
        relief=tk.SUNKEN, 
        anchor=tk.W,
        bg=THEMES[current_theme]['accent'],
        fg="white",
        font=("Segoe UI", 9)
    )
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Configure tags for text styling
    text_input.tag_configure("highlight", background=THEMES[current_theme]['highlight'])
    result_display.tag_configure("header", font=('Arial', 10, 'bold'), foreground=THEMES[current_theme]['accent'])
    result_display.tag_configure("output", font=('Consolas', 10), foreground=THEMES[current_theme]['text'])
    
    # Keyboard bindings
    root.bind("<Return>", decode_input)
    root.bind("<Escape>", clear_text)
    root.bind("<Control-c>", lambda e: clear_text())
    root.bind("<Control-C>", lambda e: clear_text())
    root.bind("<Control-Return>", decode_input)
    root.bind("<Control-Shift-C>", lambda e: copy_to_clipboard())
    
    # Focus on input field when starting
    text_input.focus_set()
    
    # Apply the default theme
    apply_theme(current_theme)
    
    # Set initial status
    update_status("Ready to decode text. Press Enter to decode.", "info")
    
    # Load history
    load_history()
    
    # Add keyboard shortcut for history
    root.bind("<Control-h>", lambda e: show_history())
    root.bind("<Control-H>", lambda e: show_history())

if __name__ == "__main__":
    create_gui()
    root.mainloop()
