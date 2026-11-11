import threading
from datetime import datetime
from decimal import Decimal, InvalidOperation

import customtkinter as ctk
from tkinter import messagebox

import caller
import util
import data
import write_credentials


def logout(window, username, token, on_logged_out):
    if not write_credentials.write_session_request(
        "LOGOUT_SESSION", username, token, data.KEY_PATH
    ):
        return
    if caller.call(data.DEBUG, data.KEY_PATH, data.JAVA_CLASS_PATH):
        on_logged_out()


def get_account(account_data, username):
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


def load_transactions(account_data, username, token):
    if not write_credentials.write_history_request(
        username, token, data.KEY_PATH
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
    account = get_account(account_data, username)
    account["transactions"] = list(reversed(transactions))
    account["balance"] = sum(
        (transaction["amount"] for transaction in transactions), Decimal("0.00")
    )
    return True


def show_transaction_form(window, account_data, username, token, action, on_logout):
    account = get_account(account_data, username)
    is_deposit = action == "ADD FUNDS"
    title = "Add funds" if is_deposit else "Make a payment"
    subtitle = (
        "Funds are added to your account and recorded in your transaction history."
        if is_deposit
        else "Payments are deducted from your account and recorded in your transaction history."
    )
    content = util.make_page(
        window,
        title,
        subtitle,
        lambda: dashboard(window, account_data, username, token, on_logout),
    )

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
        if not write_credentials.write_transaction_request(
            "RECORD_TRANSACTION_SESSION", username, token, sender, receiver,
            amount, description, data.KEY_PATH
        ) or not caller.call(data.DEBUG, data.KEY_PATH, data.JAVA_CLASS_PATH):
            return
        account["balance"] += amount if receiver == username else -amount
        add_transaction(
            account, description, amount if receiver == username else -amount,
            sender, receiver
        )
        dashboard(window, account_data, username, token, on_logout)

    util.make_button(content, "CONFIRM",
                data.BTN_REG_COLOR if is_deposit else data.BTN_LOGIN_COLOR,
                submit).pack(pady=(28, 10))
    amount_entry.focus_set()

def show_transaction_info(
    window, account_data, username, token, transaction, on_logout
):
    content = util.make_page(
        window,
        "Transaction Details",
        "Review the details of this transaction.",
        lambda: dashboard(window, account_data, username, token, on_logout),
    )
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
def dashboard(window, account_data, username, token, on_logout):
    util.clean_window(window)
    account = get_account(account_data, username)

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
    util.make_button(
        actions, "+ ADD FUNDS", data.BTN_REG_COLOR,
        lambda: show_transaction_form(
            window, account_data, username, token, "ADD FUNDS", on_logout
        ), width=145
    ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
    util.make_button(
        actions, "MAKE PAYMENT", data.BTN_LOGIN_COLOR,
        lambda: show_transaction_form(
            window, account_data, username, token, "MAKE PAYMENT", on_logout
        ), width=145
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

            ctk.CTkButton(
                row, text="View", width=50, height=24,
                corner_radius=6, fg_color=data.BTN_BACK_COLOR,
                hover_color=data.darken(data.BTN_BACK_COLOR), text_color=data.TEXT_COLOR,
                font=data.SMALL_FONT, 
                command=lambda t=transaction: show_transaction_info(
                    window, account_data, username, token, t, on_logout
                )
            ).grid(row=0, column=2, sticky="e")

        ctk.CTkLabel(
            activity_card, text="Showing the five most recent transactions",
            text_color=data.SUBTEXT_COLOR, font=("Segoe UI", 8)
        ).pack(anchor="w", padx=18, pady=(5, 13))

    ctk.CTkLabel(
        content, text="Transaction history is stored for this account.",
        text_color=data.SUBTEXT_COLOR, font=("Segoe UI", 8)
    ).pack(pady=(0, 8))
    util.make_button(content, "LOG OUT", data.BTN_BACK_COLOR, on_logout).pack(
        pady=(0, 15)
    )


def open_dashboard(window, username, token, on_logged_out):
    account_data = {}
    util.clean_window(window)
    window.configure(cursor="watch")
    loading_frame = ctk.CTkFrame(window, fg_color="transparent")
    loading_frame.pack(fill="both", expand=True, padx=35, pady=55)
    ctk.CTkLabel(
        loading_frame,
        text="Banking App",
        text_color=data.TEXT_COLOR,
        font=data.TITLE_FONT,
    ).pack(pady=(0, 12))
    ctk.CTkLabel(
        loading_frame,
        text=f"Welcome, {username}",
        text_color=data.SUBTEXT_COLOR,
        font=data.SUBTITLE_FONT,
    ).pack()
    progress = ctk.CTkProgressBar(
        loading_frame,
        width=220,
        mode="indeterminate",
        progress_color=data.BTN_LOGIN_COLOR,
        fg_color=data.INPUT_BG,
    )
    progress.pack(pady=(24, 10))
    progress.start()
    loading_status = ctk.CTkLabel(
        loading_frame,
        text="Securely loading your account...",
        text_color=data.SUBTEXT_COLOR,
        font=data.SMALL_FONT,
    )
    loading_status.pack()
    window.update_idletasks()

    result = {}

    def load_account():
        try:
            result["loaded"] = load_transactions(account_data, username, token)
        except (OSError, ValueError, InvalidOperation) as error:
            result["error"] = error

    threading.Thread(target=load_account, daemon=True).start()

    def finish_loading():
        if "loaded" not in result and "error" not in result:
            loading_status.configure(text="Retrieving recent transactions...")
            window.after(50, finish_loading)
            return
        if result.get("error") or not result.get("loaded"):
            messagebox.showerror(
                "Dashboard error",
                "The dashboard could not load your account data. Please log in again.",
            )
            window.configure(cursor="")
            on_logged_out()
            return
        progress.stop()
        window.configure(cursor="")
        dashboard(
            window,
            account_data,
            username,
            token,
            lambda: logout(window, username, token, on_logged_out),
        )

    window.after(50, finish_loading)