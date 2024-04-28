import tkinter as tk
from typing import Callable

from core.security import Key, key_to_string

class SignInFrame:
    def __init__(self, window, pack_args={}, on_sign_in: Callable = None):
        self.on_sign_in = on_sign_in

        self.frame = tk.Frame(window, borderwidth=2, background='#f0f0f0')
        self.frame.pack(**pack_args, padx=10, pady=10)

        self.label = tk.Label(self.frame, text="Sign In", font=("Arial", 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.input = tk.Entry(self.frame, width=50, font=("Arial", 12), borderwidth=1, relief="solid", insertbackground='#333')
        self.submit_btn = tk.Button(self.frame, text="Sign In", font=("Arial", 12, 'bold'), bg='#4CAF50', fg='white', cursor="hand2", command=self.on_click)

        self.label.pack(pady=(0,10))
        self.input.pack(pady=(0,10))
        self.submit_btn.pack(pady=(0,10))

    def on_click(self):
        if self.on_sign_in:
            self.on_sign_in(self.input.get())

class SignUpFrame:
    def __init__(self, window, pack_args={}):
        self.frame = tk.Frame(window, borderwidth=2, background='#f0f0f0')
        self.frame.pack(**pack_args, padx=10, pady=10)

        self.sign_up_btn = tk.Button(self.frame, text="Sign Up", font=("Arial", 12, 'bold'), bg='#2196F3', fg='white', cursor="hand2", command=self.on_click)
        self.sign_up_btn.pack(pady=(0,10))
        self.seed_phrase_var = tk.StringVar(window, "")
        self.label = tk.Entry(self.frame, textvariable=self.seed_phrase_var, state="readonly", width=50, font=("Arial", 12), borderwidth=1, relief="solid")
        self.label.pack()

    def on_click(self):
        key = Key()
        # Assuming print statements are for debugging; you might want to handle this differently in production.
        print("Generated key")
        print("Seed phrase:", key.get_seed_phrase())
        print("Public key:", key_to_string(key.public_key))
        self.seed_phrase_var.set(key.get_seed_phrase())

class SignInSignUpWindow(tk.Toplevel):
    def __init__(self, window, on_sign_in=None):
        super().__init__(window)
        self.title("Sign In / Sign Up")
        self.geometry("500x300") # Adjust size as needed
        self.configure(bg='#f0f0f0')

        self.signin_frame = SignInFrame(self, on_sign_in=on_sign_in)
        tk.Label(self, text="--- OR ---", bg='#f0f0f0', fg='#666').pack(pady=(20,20))
        self.signup_frame = SignUpFrame(self)
