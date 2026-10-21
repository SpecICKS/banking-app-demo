import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

import customtkinter as ctk
from tkinter import messagebox

import caller
import data
import write_credentials


if data.DEBUG:
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.title(data.APP_TITLE)
window.geometry(f"{data.WIDTH}x{data.HEIGHT}")
window.minsize(data.WIDTH, data.HEIGHT)
window.configure(fg_color=data.BG_COLOR)
account_data = {}
session_password = ""


def clean_window():
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


def get_account(username):
    if username not in account_data:
        account_data[username] = {"balance": Decimal("0.00"), "transactions": []}
    return account_data[username]


def parse_amount(value):
    try:
        amount = Decimal(value.strip()).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None
    return amount if amount > 0 else None


def format_money(amount):
    return f"${amount:,.2f}"


def add_transaction(account, description, amount, sender, receiver, timestamp=None):
    account["transactions"].insert(0, {
        "date": datetime.now().strftime("%b %d, %Y"),
        "timestamp": timestamp or datetime.now().astimezone().isoformat(),
        "description": description,
        "amount": amount,
        "sender": sender,
        "receiver": receiver,
    })


def load_transactions(username, password):
    if not write_credentials.write_history_request(
        username, password, data.DEBUG, data.KEY_PATH
    ):
        return False
    success, output = caller.call_with_output(
        data.DEBUG, data.KEY_PATH, data.JAVA_CLASS_PATH
    )
    if not success:
        return False

    transactions = []
    for line in output.splitlines():
        if not line.startswith("TRANSACTION|"):
            continue
        fields = line.split("|", 5)
        if len(fields) != 6:
            continue
        try:
            amount = Decimal(fields[4]).quantize(Decimal("0.01"))
            timestamp = datetime.fromisoformat(fields[1])
        except (InvalidOperation, ValueError):
            continue
        transactions.append({
            "date": timestamp.strftime("%b %d, %Y"),
            "timestamp": timestamp.isoformat(),
            "description": fields[5],
            "amount": amount if fields[3] == username else -amount,
            "sender": fields[2],
            "receiver": fields[3],
        })
    account = get_account(username)
    account["transactions"] = list(reversed(transactions))
    account["balance"] = sum(
        (transaction["amount"] for transaction in transactions), Decimal("0.00")
    )
    return True


def show_transaction_form(username, action):
    clean_window()
    account = get_account(username)
    is_deposit = action == "ADD FUNDS"
    title = "Add funds" if is_deposit else "Make a payment"
    subtitle = (
        "Funds are added to your account and recorded in your transaction history."
        if is_deposit
        else "Payments are deducted from your account and recorded in your transaction history."
    )
    content = ctk.CTkFrame(window, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=35, pady=28)
    ctk.CTkLabel(content, text=title, text_color=data.TEXT_COLOR,
                 font=data.TITLE_FONT).pack(pady=(0, 7))
    ctk.CTkLabel(content, text=subtitle, text_color=data.SUBTEXT_COLOR,
                 font=data.SMALL_FONT, wraplength=290).pack(pady=(0, 22))

    recipient_entry = None
    if not is_deposit:
        ctk.CTkLabel(content, text="PAY TO", text_color=data.SUBTEXT_COLOR,
                     font=data.LABEL_FONT).pack(anchor="w")
        recipient_entry = ctk.CTkEntry(
            content, height=40, placeholder_text="Recipient or company",
            fg_color=data.INPUT_BG, border_color=data.BORDER_COLOR,
            text_color=data.TEXT_COLOR, font=data.INPUT_FONT)
        recipient_entry.pack(fill="x", pady=(5, 15))

    ctk.CTkLabel(content, text="AMOUNT", text_color=data.SUBTEXT_COLOR,
                 font=data.LABEL_FONT).pack(anchor="w")
    amount_entry = ctk.CTkEntry(
        content, height=40, placeholder_text="0.00", fg_color=data.INPUT_BG,
        border_color=data.BORDER_COLOR, text_color=data.TEXT_COLOR,
        font=data.INPUT_FONT)
    amount_entry.pack(fill="x", pady=(5, 15))
    ctk.CTkLabel(content, text="NOTE (OPTIONAL)", text_color=data.SUBTEXT_COLOR,
                 font=data.LABEL_FONT).pack(anchor="w")
    note_entry = ctk.CTkEntry(
        content, height=40, placeholder_text="Add a note",
        fg_color=data.INPUT_BG, border_color=data.BORDER_COLOR,
        text_color=data.TEXT_COLOR, font=data.INPUT_FONT)
    note_entry.pack(fill="x", pady=(5, 0))

    def submit():
        amount = parse_amount(amount_entry.get())
        if amount is None:
            messagebox.showerror("Invalid amount", "Enter an amount greater than $0.00.")
            return
        if is_deposit:
            description = note_entry.get().strip() or "Funds added"
            sender, receiver = "SYSTEM", username
        else:
            recipient = recipient_entry.get().strip()
            if not recipient:
                messagebox.showerror("Missing recipient", "Enter who should receive the payment.")
                return
            if amount > account["balance"]:
                messagebox.showerror("Insufficient funds", "This payment is greater than your available balance.")
                return
            description = note_entry.get().strip() or f"Payment to {recipient}"
            sender, receiver = username, recipient
        if not write_credentials.write_transaction(
            username, session_password, sender, receiver, amount,
            description, data.DEBUG, data.KEY_PATH
        ) or not caller.call(data.DEBUG, data.KEY_PATH, data.JAVA_CLASS_PATH):
            return
        account["balance"] += amount if receiver == username else -amount
        add_transaction(
            account, description, amount if receiver == username else -amount,
            sender, receiver
        )
        dashboard(username)

    make_button(content, "CONFIRM",
                data.BTN_REG_COLOR if is_deposit else data.BTN_LOGIN_COLOR,
                submit).pack(pady=(28, 10))
    ctk.CTkButton(
        content, text="< Back to dashboard", width=150, height=32,
        corner_radius=6, fg_color=data.BTN_BACK_COLOR,
        hover_color=data.darken(data.BTN_BACK_COLOR), text_color=data.TEXT_COLOR,
        font=data.SMALL_FONT, command=lambda: dashboard(username)).pack()
    amount_entry.focus_set()

def show_transaction_info(username, transaction):
    clean_window()
    content = ctk.CTkFrame(window, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=35, pady=28)
    ctk.CTkLabel(content, text="Transaction Details", text_color=data.TEXT_COLOR,
                 font=data.TITLE_FONT).pack(pady=(0, 7))
    timestamp = datetime.fromisoformat(transaction["timestamp"])
    direction = "Incoming" if transaction["amount"] > 0 else "Outgoing"
    details = (
        ("Status", direction),
        ("Date", timestamp.strftime("%b %d, %Y")),
        ("Time", timestamp.strftime("%H:%M:%S %Z")),
        ("Sender", transaction["sender"]),
        ("Receiver", transaction["receiver"]),
        ("Description", transaction["description"]),
        ("Amount", format_money(abs(transaction["amount"]))),
    )
    details_frame = ctk.CTkFrame(content, fg_color=data.INPUT_BG, corner_radius=10)
    details_frame.pack(fill="x", pady=(12, 22))
    for label, value in details:
        row = ctk.CTkFrame(details_frame, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=6)
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            row, text=label, text_color=data.SUBTEXT_COLOR,
            font=data.LABEL_FONT, anchor="w"
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            row, text=value, text_color=data.TEXT_COLOR,
            font=data.INPUT_FONT, anchor="e", justify="right",
            wraplength=190
        ).grid(row=0, column=1, sticky="e", padx=(15, 0))
    ctk.CTkButton(
        content, text="< Back to dashboard", width=150, height=32,
        corner_radius=6, fg_color=data.BTN_BACK_COLOR,
        hover_color=data.darken(data.BTN_BACK_COLOR), text_color=data.TEXT_COLOR,
        font=data.SMALL_FONT, command=lambda: dashboard(username)).pack(pady=(20, 0))


def open_form(action):
    clean_window()

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
        global session_password
        username = entry_user.get().strip()
        password = entry_pass.get()
        if write_credentials.write(
            action, username, password, data.DEBUG, data.KEY_PATH
        ) and caller.call(data.DEBUG, data.KEY_PATH, data.JAVA_CLASS_PATH):
            if action == "LOGIN":
                session_password = password
                load_transactions(username, password)
                dashboard(username)
            else:
                start_screen()

    make_button(content, action, button_color, submit).pack(pady=(30, 10))

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


def dashboard(username):
    clean_window()
    account = get_account(username)

    content = ctk.CTkScrollableFrame(
        window, fg_color="transparent", scrollbar_button_color=data.BORDER_COLOR
    )
    content.pack(fill="both", expand=True, padx=18, pady=20)

    ctk.CTkLabel(
        content,
        text="Account Dashboard",
        text_color=data.TEXT_COLOR,
        font=data.TITLE_FONT,
    ).pack(pady=(5, 6))

    ctk.CTkLabel(
        content,
        text=f"Welcome, {username}",
        text_color=data.SUBTEXT_COLOR,
        font=data.SUBTITLE_FONT,
    ).pack(pady=(0, 18))

    account_card = ctk.CTkFrame(
        content,
        fg_color=data.INPUT_BG,
        corner_radius=12,
    )
    account_card.pack(fill="x", padx=5)

    ctk.CTkLabel(
        account_card,
        text="ACCOUNT OVERVIEW",
        text_color=data.SUBTEXT_COLOR,
        font=data.LABEL_FONT,
    ).pack(pady=(18, 5))

    ctk.CTkLabel(
        account_card,
        text="Account status: Active",
        text_color=data.TEXT_COLOR,
        font=data.INPUT_FONT,
    ).pack(pady=3)

    ctk.CTkLabel(
        account_card,
        text=format_money(account["balance"]),
        text_color=data.TEXT_COLOR,
        font=("Segoe UI", 24, "bold"),
    ).pack(pady=(3, 2))
    ctk.CTkLabel(
        account_card, text="Available balance", text_color=data.SUBTEXT_COLOR,
        font=data.SMALL_FONT
    ).pack(pady=(0, 18))

    actions = ctk.CTkFrame(content, fg_color="transparent")
    actions.pack(fill="x", pady=18)
    actions.grid_columnconfigure(0, weight=1)
    actions.grid_columnconfigure(1, weight=1)
    make_button(
        actions, "+ ADD FUNDS", data.BTN_REG_COLOR,
        lambda: show_transaction_form(username, "ADD FUNDS"), width=145
    ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
    make_button(
        actions, "MAKE PAYMENT", data.BTN_LOGIN_COLOR,
        lambda: show_transaction_form(username, "MAKE PAYMENT"), width=145
    ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    activity_card = ctk.CTkFrame(content, fg_color=data.INPUT_BG, corner_radius=12)
    activity_card.pack(fill="x", padx=5, pady=(0, 18))
    ctk.CTkLabel(
        activity_card, text="RECENT ACTIVITY", text_color=data.SUBTEXT_COLOR,
        font=data.LABEL_FONT
    ).pack(anchor="w", padx=18, pady=(15, 8))
    transactions = account["transactions"]
    if not transactions:
        ctk.CTkLabel(
            activity_card,
            text="No transactions yet. Add funds or make a payment to get started.",
            text_color=data.SUBTEXT_COLOR, font=data.SMALL_FONT, wraplength=270
        ).pack(anchor="w", padx=18, pady=(0, 16))
    else:
        for transaction in transactions[:5]:
            row = ctk.CTkFrame(activity_card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=5)
            row.grid_columnconfigure(0, weight=1)
            
            # Display description and date
            ctk.CTkLabel(
                row, text=f'{transaction["description"]}\n{transaction["date"]}',
                justify="left", anchor="w", text_color=data.TEXT_COLOR,
                font=data.SMALL_FONT
            ).grid(row=0, column=0, sticky="w")
            
            amount = transaction["amount"]
            
            # Display amount
            ctk.CTkLabel(
                row, text=("+" if amount > 0 else "") + format_money(amount),
                text_color=data.BTN_REG_COLOR if amount > 0 else data.TEXT_COLOR,
                font=("Segoe UI", 10, "bold")
            ).grid(row=0, column=1, sticky="e", padx=(0, 10))

            # ADDED: "View" button to trigger show_transaction_info
            ctk.CTkButton(
                row, text="View", width=50, height=24,
                corner_radius=6, fg_color=data.BTN_BACK_COLOR,
                hover_color=data.darken(data.BTN_BACK_COLOR), text_color=data.TEXT_COLOR,
                font=data.SMALL_FONT, 
                command=lambda t=transaction: show_transaction_info(username, t)
            ).grid(row=0, column=2, sticky="e")

        ctk.CTkLabel(
            activity_card, text="Showing the five most recent transactions",
            text_color=data.SUBTEXT_COLOR, font=("Segoe UI", 8)
        ).pack(anchor="w", padx=18, pady=(5, 13))

    ctk.CTkLabel(
        content, text="Transaction history is stored for this account.",
        text_color=data.SUBTEXT_COLOR, font=("Segoe UI", 8)
    ).pack(pady=(0, 8))
    make_button(content, "LOG OUT", data.BTN_BACK_COLOR, start_screen).pack(pady=(0, 15))


def start_screen():
    global session_password
    session_password = ""
    clean_window()

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

    make_button(
        content,
        "LOGIN",
        data.BTN_LOGIN_COLOR,
        lambda: open_form("LOGIN"),
    ).pack(pady=8)

    make_button(
        content,
        "REGISTER",
        data.BTN_REG_COLOR,
        lambda: open_form("REGISTER"),
    ).pack(pady=8)


start_screen()
window.mainloop()
