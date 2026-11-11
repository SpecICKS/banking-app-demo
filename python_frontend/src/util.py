import customtkinter as ctk

import data


def clean_window(window):
    for element in window.winfo_children():
        element.destroy()


def make_button(parent, text, color, command, width=220):
    return ctk.CTkButton(
        parent,
        text=text,
        width=width,
        height=42,
        corner_radius=8,
        fg_color=color,
        hover_color=data.darken(color),
        text_color=data.TEXT_COLOR,
        font=data.BUTTON_FONT,
        command=command,
    )


def make_page(window, title, subtitle, back_command):
    clean_window(window)
    content = ctk.CTkFrame(window, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=35, pady=28)
    ctk.CTkButton(
        content,
        text="< Back to dashboard",
        width=150,
        height=32,
        corner_radius=6,
        fg_color=data.BTN_BACK_COLOR,
        hover_color=data.darken(data.BTN_BACK_COLOR),
        text_color=data.TEXT_COLOR,
        font=data.SMALL_FONT,
        command=back_command,
    ).pack(anchor="w", pady=(0, 18))
    ctk.CTkLabel(
        content,
        text=title,
        text_color=data.TEXT_COLOR,
        font=data.TITLE_FONT,
    ).pack(pady=(0, 7))
    ctk.CTkLabel(
        content,
        text=subtitle,
        text_color=data.SUBTEXT_COLOR,
        font=data.SMALL_FONT,
        wraplength=290,
    ).pack(pady=(0, 22))
    return content