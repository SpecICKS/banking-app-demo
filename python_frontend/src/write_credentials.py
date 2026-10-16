from tkinter import messagebox

def write(action ,username, password, debug, key_path):
    if (len(password) < 8 or not any(not c.isalnum() for c in password)) and action == "REGISTER":
        messagebox.showerror("ERROR", "Password does not contain at least 8 characters and 1 special character!")
        return False
    try:
        with open(key_path, "w") as file:
            file.write(action + "\n")
            file.write(username + "\n")
            file.write(password + "\n")
        if debug == True:
            messagebox.showinfo("Success", "Saved credentials")
        return True
            
    except Exception as e:
        messagebox.showerror("ERROR", f"Couldn't create the file {e}")
        return False