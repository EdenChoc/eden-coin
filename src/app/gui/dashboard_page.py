import tkinter as tk
from tkinter import ttk  # Import ttk module for the Combobox
from tkinter import messagebox

from blockchain_communication import get_world_state, post_instruction



def transfer_money():
    messagebox.showinfo("Transfer Money", "Transfer money action selected")

def add_function():
    messagebox.showinfo("Add Function", "Add function to blockchain system selected")



class DashboardWindow(tk.Toplevel):
    def __init__(self, root, current_user):

        self.current_user = current_user
        self.contract_params: dict[str, tk.StringVar] = {}

        root.title("Blockchain System Main Interface")

        # Set the window size
        root.geometry("500x550") # Increased height to accommodate the lowered button

        # Set a background color for the window
        root.configure(background='#f0f0f0')

        # Add a title label with a larger font and different color
        title_label = tk.Label(root, text="Welcome to EdenCoin", font=("Helvetica", 24, "bold"), bg='#f0f0f0', fg='#333')
        title_label.pack(side="top", pady=(30, 20))


        # Create a frame for buttons, the dropdown, and labels to align them on the left with a specific background color
        self.contracts_frame = tk.Frame(root, bg='#f0f0f0')

        # Create a button for viewing financial savings and add it to the frame with adjusted styling and increased spacing (lowered)
        savings_button_style = {'font': ("Helvetica", 12), 'bg': 'white', 'fg': '#333', 'padx': 10, 'pady': 4, 'activebackground': '#ddd'}
        view_savings_button = tk.Button(self.contracts_frame, text="View Your Financial Savings", command=self.view_savings, **savings_button_style)
        view_savings_button.pack(pady=30) # Significantly increased space above this button


        # Add a label for "All Contracts" above the dropdown
        contracts_label = tk.Label(self.contracts_frame, text="Execute contract:", bg='#f0f0f0', fg='#333', font=("Helvetica", 16))
        contracts_label.pack(anchor="nw")

        exec_contract_btn = tk.Button(self.contracts_frame, text="Execute contract", command=self.on_exec_contract)
        # Create a dropdown for "All Contracts"
        self.contract_name = tk.StringVar() # Variable to hold the selection
        self.contract_name.trace_add("write", self.on_contract_selected)
        self.contracts_dropdown = ttk.Combobox(self.contracts_frame, textvariable=self.contract_name, state="readonly", width=18, font=("Helvetica", 14))
        self.contracts_dropdown['values'] = self.get_contracts()
        self.contracts_dropdown.pack(anchor="nw", pady=(0, 20))  # Adjust spacing accordingly

        self.params_frame = tk.Frame(self.contracts_frame)
        self.contracts_frame.pack(pady=10)
        self.params_frame.pack(pady=10)
        exec_contract_btn.pack(pady=10)



    def on_exec_contract(self):
        success = post_instruction(
            id_program=self.contract_name.get(),
            executor=self.current_user.get_pubkey(),
            params={param: param_var.get() for param, param_var in self.contract_params.items()},
            current_user= self.current_user
        )
        if success:
            messagebox.showinfo("Execute contract", f"Successfully executed contract {self.contract_name.get()}")
            self.contracts_dropdown['values'] = self.get_contracts()
        else:
            messagebox.showinfo("Execute contract", f"Failed execution of contract {self.contract_name.get()}")


    def on_contract_selected(self, var, index, mode):
        # Get contract in WS and retrieve its parameters
        contract_name = self.contract_name.get()
        world_state = get_world_state()
        contract = world_state.contracts[contract_name]
        params = contract.get_contract_params()

        # Purge frame
        for widget in self.params_frame.winfo_children():
            widget.destroy()

        self.contract_params = {}

        # Create widgets
        for param in params:
            param_frame = tk.Frame(self.params_frame)
            param_var = tk.StringVar()
            self.contract_params[param] = param_var
            tk.Label(param_frame, text=param).pack()
            tk.Entry(param_frame, textvariable=param_var, width=30).pack(side="right")
            param_frame.pack(side="bottom")


    def view_savings(self):
        world_state = get_world_state()
        balance = world_state.get_account_balance(self.current_user.get_pubkey())
        messagebox.showinfo("Savings", f"Your have {balance} coins")

    def get_contracts(self):
        world_state = get_world_state()
        return list(world_state.contracts.keys())



if __name__ == '__main__':
    root = tk.Tk()
    window = DashboardWindow(root)
    root.mainloop()
