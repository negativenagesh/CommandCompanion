"""
GUI interface components for CommandCompanion
"""

import tkinter as tk
from config.settings import GUI_CONFIG

def create_interface(root, on_submit):
    """
    Create the GUI interface for CommandCompanion.
    
    Args:
        root (tk.Tk): The root Tkinter window
        on_submit (function): Callback function for submit button
        
    Returns:
        tuple: A tuple containing (entry_widget, status_label)
    """
    # Create a custom font
    title_font = GUI_CONFIG["title_font"]
    normal_font = GUI_CONFIG["normal_font"]
    status_font = GUI_CONFIG["status_font"]

    # Create a header frame
    header_frame = tk.Frame(root, bg=GUI_CONFIG["header_bg"], height=60)
    header_frame.pack(fill=tk.X)
    header_frame.pack_propagate(False)

    # Header title
    header_label = tk.Label(header_frame, text="CommandCompanion", font=title_font, bg=GUI_CONFIG["header_bg"], fg="white")
    header_label.pack(pady=15)

    # Main content frame
    content_frame = tk.Frame(root, bg=GUI_CONFIG["bg_color"], padx=30, pady=25)
    content_frame.pack(fill=tk.BOTH, expand=True)

    # Description text
    desc_label = tk.Label(content_frame, 
                         text="Your AI-powered command assistant",
                         font=normal_font, bg=GUI_CONFIG["bg_color"], fg="#34495e")
    desc_label.pack(anchor="w", pady=(0, 20))

    # Input frame
    input_frame = tk.Frame(content_frame, bg=GUI_CONFIG["bg_color"])
    input_frame.pack(fill=tk.X)

    # Input field
    entry = tk.Entry(input_frame, font=normal_font, bd=2, relief=tk.SOLID)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry.focus()

    # Execute button with nicer styling
    submit_btn = tk.Button(input_frame, text="Execute", bg=GUI_CONFIG["button_bg"], fg="white", 
                          font=normal_font, relief=tk.FLAT, padx=15, 
                          activebackground=GUI_CONFIG["button_active_bg"], activeforeground="white",
                          command=on_submit)
    submit_btn.pack(side=tk.RIGHT, padx=(10, 0))

    # Status frame
    status_frame = tk.LabelFrame(content_frame, text="Status", bd=1, relief=tk.GROOVE, 
                               bg="white", font=normal_font, padx=10, pady=10)
    status_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

    # Status label
    status_label = tk.Label(status_frame, text="Ready", wraplength=580, 
                           font=status_font, bg="white", fg="#2c3e50",
                           anchor="w", justify=tk.LEFT)
    status_label.pack(fill=tk.BOTH, expand=True)

    # Footer frame
    footer_frame = tk.Frame(root, bg=GUI_CONFIG["footer_bg"], height=30)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

    # Footer text
    footer_label = tk.Label(footer_frame, text="Press Enter to execute commands", 
                          font=("Helvetica", 8), bg=GUI_CONFIG["footer_bg"], fg=GUI_CONFIG["footer_fg"])
    footer_label.pack(pady=8)
    
    return entry, status_label