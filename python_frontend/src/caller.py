import subprocess
import os
from tkinter import messagebox

def call(debug, key_path):
    command = [
        "java",
        "-cp",
        "../../java_backend/bin", #controller path
        "Controller.Controller", #package.class
        key_path
    ]
    try:
        response = subprocess.run(command, capture_output=True, text=True)
        if debug == True:
            print("LOG JAVA:", response.stdout)

        if response.returncode != 0:
            messagebox.showerror("Error:", f"{response.stderr}")
        else:
            #for the moment:
            messagebox.showinfo("Succes", "Operation success!")
            os.remove(key_path)
            #if it works well, the frontend should close and the
            #real banking app should open showing the profile of the user
            #!!!TO IMPLEMENT!!!
    except Exception as e:
        if debug == True:
            print(f"Fatal Error: {e}")
