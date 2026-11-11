import customtkinter as ctk
from tkinter import messagebox

import caller
import data
import dashboard
import util
import write_credentials


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.title(data.APP_TITLE)
window.geometry(f"{data.WIDTH}x{data.HEIGHT}")
window.minsize(data.WIDTH, data.HEIGHT)
window.configure(fg_color=data.BG_COLOR)


def open_form(action):
    util.clean_window(window)

    title = "Authentication" if action == "LOGIN" else "Create New Account"
    button_color = data.BTN_LOGIN_COLOR if action == "LOGIN" else data.BTN_REG_COLOR

    content = ctk.CTkFrame(window, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=35, pady=25)

    ctk.CTkLabel(
        content,
        text=title,
        text_color=data.TEXT_COLOR,
        font=data.TITLE_FONT,
    ).pack(pady=(5, 25))

    ctk.CTkLabel(
        content,
        text="USERNAME",
        text_color=data.SUBTEXT_COLOR,
        font=data.LABEL_FONT,
    ).pack(anchor="w")

    entry_user = ctk.CTkEntry(
        content,
        height=40,
        placeholder_text="Enter your username",
        fg_color=data.INPUT_BG,
        border_color=data.BORDER_COLOR,
        text_color=data.TEXT_COLOR,
        font=data.INPUT_FONT,
    )
    entry_user.pack(fill="x", pady=(5, 15))

    ctk.CTkLabel(
        content,
        text="PASSWORD",
        text_color=data.SUBTEXT_COLOR,
        font=data.LABEL_FONT,
    ).pack(anchor="w")

    entry_pass = ctk.CTkEntry(
        content,
        height=40,
        placeholder_text="Enter your password",
        show="*",
        fg_color=data.INPUT_BG,
        border_color=data.BORDER_COLOR,
        text_color=data.TEXT_COLOR,
        font=data.INPUT_FONT,
    )
    entry_pass.pack(fill="x", pady=(5, 0))

    if action == "REGISTER":
        ctk.CTkLabel(
            content,
            text="Minimum 8 characters and 1 special character",
            text_color=data.SUBTEXT_COLOR,
            font=data.SMALL_FONT,
        ).pack(anchor="w", pady=(5, 0))

    def submit():
        username = entry_user.get().strip()
        password = entry_pass.get()
        submit_button.configure(state="disabled", text="OPENING...")
        if write_credentials.write(
            action, username, password, data.KEY_PATH
        ):
            if action == "LOGIN":
                success, output = caller.call_with_output(
                    data.DEBUG, data.KEY_PATH, data.JAVA_CLASS_PATH
                )
                if not success:
                    submit_button.configure(state="normal", text=action)
                    return
                token = next(
                    (
                        line.split("|", 1)[1]
                        for line in output.splitlines()
                        if line.startswith("SESSION|")
                    ),
                    None,
                )
                if not token:
                    messagebox.showerror(
                        "Login error", "The backend did not return a session."
                    )
                    submit_button.configure(state="normal", text=action)
                    return
                dashboard.open_dashboard(window, username, token, start_screen)
            else:
                if caller.call(data.DEBUG, data.KEY_PATH, data.JAVA_CLASS_PATH):
                    start_screen()
                else:
                    submit_button.configure(state="normal", text=action)
        else:
            submit_button.configure(state="normal", text=action)

    submit_button = util.make_button(
        content, action, button_color, submit
    )
    submit_button.pack(pady=(30, 10))

    ctk.CTkButton(
        content,
        text="< Back",
        width=120,
        height=32,
        corner_radius=6,
        fg_color=data.BTN_BACK_COLOR,
        hover_color=data.darken(data.BTN_BACK_COLOR),
        text_color=data.TEXT_COLOR,
        font=data.SMALL_FONT,
        command=start_screen,
    ).pack()

    entry_user.focus_set()


def start_screen():
    util.clean_window(window)

    content = ctk.CTkFrame(window, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=35, pady=55)

    ctk.CTkLabel(
        content,
        text="Banking App",
        text_color=data.TEXT_COLOR,
        font=data.TITLE_FONT,
    ).pack(pady=(0, 8))

    ctk.CTkLabel(
        content,
        text="Choose an option to start",
        text_color=data.SUBTEXT_COLOR,
        font=data.SUBTITLE_FONT,
    ).pack(pady=(0, 35))

    util.make_button(
        content,
        "LOGIN",
        data.BTN_LOGIN_COLOR,
        lambda: open_form("LOGIN"),
    ).pack(pady=8)

    util.make_button(
        content,
        "REGISTER",
        data.BTN_REG_COLOR,
        lambda: open_form("REGISTER"),
    ).pack(pady=8)


start_screen()
window.mainloop()
