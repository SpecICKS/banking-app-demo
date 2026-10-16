from tkinter import messagebox

def write(action ,username, password):
    path = "../../java_backend/key.txt"
    try:
        with open(path, "w") as file:
            file.write(action + "\n")
            file.write(username + "\n")
            file.write(password + "\n")
            messagebox.showinfo("Success", "Saved credentials")
    except Exception as e:

        messagebox.showerror("ERROR", f"Couldn't create the file {e}")