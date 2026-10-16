# writing.py
import data
import write_credentials
import tkinter as tk

fereastra = tk.Tk()
fereastra.title(data.APP_TITLE)
fereastra.geometry(f"{data.LENGHT}x{data.HEIGHT}")
fereastra.configure(bg=data.BG_COLOR) # Setăm culoarea de fundal a ferestrei


# Funcție care șterge elementele vechi de pe ecran când schimbăm pagina
def curata_ecranul():
    for element in fereastra.winfo_children():
        element.destroy()


# ================= ECRANUL 2: FORMULARUL (LOGIN SAU REGISTER) =================
def deschide_formular(tip_actiune):
    curata_ecranul()

    # Titlu dinamic (se schimbă în funcție de ce ai apăsat)
    titlu_text = "Authentification" if tip_actiune == "LOGIN" else "Create New Account"
    culoare_buton = data.BTN_LOGIN_COLOR if tip_actiune == "LOGIN" else data.BTN_REG_COLOR

    label_titlu = tk.Label(
        fereastra, text=titlu_text, 
        font=("Segoe UI", 18, "bold"), 
        bg=data.BG_COLOR, fg=data.TEXT_COLOR
    )
    label_titlu.pack(pady=(30, 20))

    # Căsuța pentru Username
    label_user = tk.Label(
        fereastra, text="USERNAME", 
        font=("Segoe UI", 9, "bold"), 
        bg=data.BG_COLOR, fg=data.SUBTEXT_COLOR
    )
    label_user.pack(pady=(5, 2))
    
    entry_user = tk.Entry(
        fereastra, font=("Segoe UI", 12), 
        bg=data.INPUT_BG, fg=data.TEXT_COLOR, 
        insertbackground="white", bd=0, justify="center"
    )
    entry_user.pack(pady=5, ipady=6, ipadx=10)

    # Căsuța pentru Parolă
    label_parola = tk.Label(
        fereastra, text="Password", 
        font=("Segoe UI", 9, "bold"), 
        bg=data.BG_COLOR, fg=data.SUBTEXT_COLOR
    )
    label_parola.pack(pady=(15, 2))
    
    entry_parola = tk.Entry(
        fereastra, show="●", font=("Segoe UI", 12), 
        bg=data.INPUT_BG, fg=data.TEXT_COLOR, 
        insertbackground="white", bd=0, justify="center"
    )
    entry_parola.pack(pady=5, ipady=6, ipadx=10)

    # Butonul de confirmare (Login sau Register)
    buton_confirmare = tk.Button(
        fereastra, text=tip_actiune, 
        font=("Segoe UI", 11, "bold"), 
        bg=culoare_buton, fg=data.TEXT_COLOR, 
        bd=0, width=18, pady=8, cursor="hand2",
        command= lambda: write_credentials.write(tip_actiune, entry_user.get(), entry_parola.get())
    )
    buton_confirmare.pack(pady=(30, 10))

    # Butonul de Înapoi către meniul principal
    buton_inapoi = tk.Button(
        fereastra, text="⬅ Back", 
        font=("Segoe UI", 9), 
        bg=data.BTN_BACK_COLOR, fg=data.TEXT_COLOR, 
        bd=0, width=12, pady=4, cursor="hand2",
        command=ecran_start
    )
    buton_inapoi.pack()

def ecran_start():
    curata_ecranul()

    # Logo / Titlu Bancă
    titlu = tk.Label(
        fereastra, text="Banking App", 
        font=("Segoe UI", 22, "bold"), 
        bg=data.BG_COLOR, fg=data.TEXT_COLOR
    )
    titlu.pack(pady=(60, 10))

    subtitlu = tk.Label(
        fereastra, text="Choose an option to start", 
        font=("Segoe UI", 10), 
        bg=data.BG_COLOR, fg=data.SUBTEXT_COLOR
    )
    subtitlu.pack(pady=(0, 40))

    # Butonul care te duce la Login
    btn_login = tk.Button(
        fereastra, text="LOGIN", 
        font=("Segoe UI", 12, "bold"), 
        bg=data.BTN_LOGIN_COLOR, fg=data.TEXT_COLOR, 
        bd=0, width=20, pady=10, cursor="hand2",
        command=lambda: deschide_formular("LOGIN")
    )
    btn_login.pack(pady=10)

    # Butonul care te duce la Register
    btn_register = tk.Button(
        fereastra, text="REGISTER", 
        font=("Segoe UI", 12, "bold"), 
        bg=data.BTN_REG_COLOR, fg=data.TEXT_COLOR, 
        bd=0, width=20, pady=10, cursor="hand2",
        command=lambda: deschide_formular("REGISTER"),

    )
    btn_register.pack(pady=10)


# Pornim aplicația direct în Meniul de Start
ecran_start()

fereastra.mainloop()