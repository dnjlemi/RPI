import tkinter as tk

class SimpleGUI:
    def __init__(self, master):
        self.master = master
        master.title("Simple GUI")

        # Set the size of the window to fit the 3.5-inch screen
        master.geometry("480x320")

        # Create a label
        self.label = tk.Label(master, text="Hello, Raspberry Pi!")
        self.label.pack(pady=20)

        # Create an exit button
        self.exit_button = tk.Button(master, text="Exit", command=master.destroy)
        self.exit_button.pack()

if __name__ == "__main__":
    root = tk.Tk()
    gui = SimpleGUI(root)
    root.mainloop()
