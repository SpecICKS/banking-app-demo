import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)


def write(action, username, password, debug, key_path):
    username = username.strip()
    if not username or any(character in username for character in "\r\n:"):
        messagebox.showerror("ERROR", "Username must not be empty or contain new lines or ':'")
        return False

    if action == "REGISTER" and (
        len(password) < 8 or not any(not character.isalnum() for character in password)
    ):
        messagebox.showerror("ERROR", "Password does not contain at least 8 characters and 1 special character!")
        return False

    try:
        with open(key_path, "w", encoding="utf-8") as file:
            file.write(action + "\n")
            file.write(username + "\n")
            file.write(password + "\n")
        if debug:
            logger.debug("Prepared %s request file for backend processing", action.lower())
        return True

    except OSError as error:
        messagebox.showerror("ERROR", f"Couldn't create the file {error}")
        return False


def write_transaction(username, password, sender, receiver, amount, description, debug, key_path):
    fields = [username.strip(), sender.strip(), receiver.strip(), description.strip()]
    if any(not field or any(character in field for character in "\r\n") for field in fields):
        messagebox.showerror("ERROR", "Transaction fields must not be empty or contain new lines.")
        return False
    try:
        with open(key_path, "w", encoding="utf-8") as file:
            file.write("RECORD_TRANSACTION\n")
            file.write(username.strip() + "\n")
            file.write(password + "\n")
            file.write(sender.strip() + "\n")
            file.write(receiver.strip() + "\n")
            file.write(str(amount) + "\n")
            file.write(description.strip() + "\n")
        if debug:
            logger.debug("Prepared transaction request for backend processing")
        return True
    except OSError as error:
        messagebox.showerror("ERROR", f"Couldn't create the file {error}")
        return False


def write_history_request(username, password, debug, key_path):
    try:
        with open(key_path, "w", encoding="utf-8") as file:
            file.write("GET_TRANSACTIONS\n")
            file.write(username + "\n")
            file.write(password + "\n")
        if debug:
            logger.debug("Prepared transaction history request for backend processing")
        return True
    except OSError as error:
        messagebox.showerror("ERROR", f"Couldn't create the file {error}")
        return False