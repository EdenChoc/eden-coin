import tkinter as tk
import bip39

from app.gui.signin_signup import SignInSignUpWindow
from core.security import Key
from current_user import CurrentUser
from gui.dashboard_page import DashboardWindow


class MainWindow:

    def __init__(self, window):
        self.root = window
        self.current_user = CurrentUser()


        self.signin_window = SignInSignUpWindow(self.root, on_sign_in=self.on_sign_in)
        self.dashboard_window = None


    def on_sign_in(self, seed_phrase):
        try:
            self.current_user.key = Key.from_seed_phrase(seed_phrase)
        except bip39.DecodingError:
            print("Wrong seed phrase")
            return
        self.dashboard_window = DashboardWindow(self.root, self.current_user)


def run_gui():
    window = tk.Tk()
    app = MainWindow(window)
    window.mainloop()

if __name__ == '__main__':
    run_gui()