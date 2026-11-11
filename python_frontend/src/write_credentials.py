from tkinter import messagebox

def write(action, username, password, key_path):
    username = username.strip()
    if not username or any(character in username for character in "\r\n:"):
        messagebox.showerror("Error", "Username must not be empty or contain new lines or ':'")
        return False

    if action == "REGISTER" and (
        len(password) < 8 or not any(not character.isalnum() for character in password)
    ):
        messagebox.showerror("Error", "Password must contain at least 8 characters and 1 special character.")
        return False

    try:
        with open(key_path, "w", encoding="utf-8") as file:
            file.write(action + "\n")
            file.write(username + "\n")
            file.write(password + "\n")
        return True

    except OSError as error:
        messagebox.showerror("Error", f"Could not create the request file: {error}")
        return False

def write_transaction(username, password, sender, receiver, amount, description, key_path):
    return write_transaction_request(
        "RECORD_TRANSACTION", username, password, sender, receiver,
        amount, description, key_path
    )


def write_transaction_request(
    action, username, credential, sender, receiver, amount, description, key_path
):
    fields = [username.strip(), sender.strip(), receiver.strip(), description.strip()]
    if any(not field or any(character in field for character in "\r\n") for field in fields):
        messagebox.showerror("Error", "Transaction fields must not be empty or contain new lines.")
        return False
    try:
        with open(key_path, "w", encoding="utf-8") as file:
            file.write(action + "\n")
            file.write(username.strip() + "\n")
            file.write(credential + "\n")
            file.write(sender.strip() + "\n")
            file.write(receiver.strip() + "\n")
            file.write(str(amount) + "\n")
            file.write(description.strip() + "\n")
        return True
    except OSError as error:
        messagebox.showerror("Error", f"Could not create the request file: {error}")
        return False


def write_history_request(username, password, key_path):
    return write_session_request(
        "GET_TRANSACTIONS_SESSION", username, password, key_path
    )


def write_session_request(action, username, token, key_path):
    try:
        with open(key_path, "w", encoding="utf-8") as file:
            file.write(action + "\n")
            file.write(username + "\n")
            file.write(token + "\n")
        return True
    except OSError as error:
        messagebox.showerror("Error", f"Could not create the request file: {error}")
        return False
