import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import os
from graphviz import Digraph

# Specify the path to the Graphviz executables
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

class Table(tk.Frame,simpledialog.Dialog):
    def __init__(self, parent, rows=0, columns=0):
        tk.Frame.__init__(self, parent, bg="white", bd=2, relief=tk.SOLID)
        self.rows = rows
        self.columns = columns
        self.final_alpha = set()
        self.input_values = [[tk.StringVar() for _ in range(columns)] for _ in range(rows)]
        self.cells = [[tk.Entry(self, width=10, borderwidth=1, bg="white", font=("Helvetica", 10), textvariable=self.input_values[i][j]) for j in range(columns)] for i in range(rows)]

    def create_table(self):
        # Create the "States" cell in the first column of the first row
        states_label = tk.Label(self, text="States", bg="lightgray", font=("Helvetica", 10, "bold"))
        states_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Create cells with state names in the first column starting from the second row
        for i in range(1, self.rows):
            state_entry = tk.Entry(self, width=10, borderwidth=1, font=("Helvetica", 10, "bold"))
            state_entry.grid(row=i, column=0, sticky="nsew", padx=5, pady=5)
            if chr(64+i) == 'A':
                state_entry.insert(tk.END,chr(64+i)+" (initial)")
            else:
                state_entry.insert(tk.END, chr(64 + i))
            state_entry.config(state=tk.DISABLED)  # Disable the entry

        # Create alphabet labels in the first row starting from the second column
        for j in range(1, self.columns + 1):
            alphabet_label = tk.Label(self, text=j-1, bg="lightgray", font=("Helvetica", 10, "bold"))
            alphabet_label.grid(row=0, column=j, sticky="nsew", padx=5, pady=5)

        # Create cells in the remaining columns and rows
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                cell.grid(row=i, column=j+1, sticky="nsew", padx=5, pady=5)

        for i in range(self.rows):
            self.grid_rowconfigure(i, weight=1)

        for i in range(self.columns):
            self.grid_columnconfigure(i+1, weight=1)

        # Create a button to highlight the final state
        highlight_button = tk.Button(self, text="Highlight Final State", command=self.highlight_final_state, bg="lightgreen", font=("Helvetica", 10, "bold"))
        highlight_button.grid(row=self.rows, column=0, columnspan=self.columns+1, sticky="nsew", pady=5)

        # Create a button to print the input values
        print_button = tk.Button(self, text="Show DFA", command=self.print_input_values, bg="lightgreen", font=("Helvetica", 10, "bold"))
        print_button.grid(row=self.rows+1, column=0, columnspan=self.columns+1, sticky="nsew", pady=5)

        self.close_button = tk.Button(self, text="Show minimized DFA", command=self.close_screen, bg="lightgreen", font=("Helvetica", 10, "bold"))
        self.close_button.grid(row=self.rows+2, column=0, columnspan=self.columns+1, sticky="nsew", pady=5)
        self.close_button.config(state="disabled")

    def final_state(self):

        for i in range(1, self.rows):
            state_entry = self.grid_slaves(row=i, column=0)[0]
            if state_entry.cget("state") == "disabled" and state_entry.cget("disabledbackground") == "yellow":
                continue
            if state_entry.get() in self.final_alpha:
                state_entry.config(bg="yellow")
                state_entry.config(state=tk.DISABLED, disabledbackground="yellow")
            else:
                state_entry.config(state=tk.DISABLED)

    def set_final_state(self):
        self.final_alpha = set()
        with open("output.txt", "r") as file:
            for _ in range(2):
                line = next(file)

            for i in line:
                self.final_alpha.add(i)

    def create_mini_table(self):

        # Create the "States" cell in the first column of the first row
        states_label = tk.Label(self, text="States", bg="lightgray", font=("Helvetica", 10, "bold"))
        states_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        dot = Digraph()
        self.set_final_state()
        # Create cells with state names in the first column starting from the second row
        for i in range(1, self.rows):
            state_entry = tk.Entry(self, width=10, borderwidth=1, font=("Helvetica", 10, "bold"))
            state_entry.grid(row=i, column=0, sticky="nsew", padx=5, pady=5)
            state_entry.insert(tk.END, chr(64 + i))
            if chr(64 + i) in self.final_alpha:
                dot.node(chr(64 + i), peripheries='2')
            else:
                dot.node(chr(64 + i))
            state_entry.config(state=tk.DISABLED)  # Disable the entry


        # Create alphabet labels in the first row starting from the second column
        for j in range(1, self.columns + 1):
            alphabet_label = tk.Label(self, text=j-1, bg="lightgray", font=("Helvetica", 10, "bold"))
            alphabet_label.grid(row=0, column=j, sticky="nsew", padx=5, pady=5)

        with open("output.txt", "r") as file:
            for _ in range(2):
                next(file)  # Skip the first two lines
            for i in range (1, self.rows):
                line = next(file).strip()  # Read the next line from the file
                for j in range(len(line)):  # Iterate up to the length of the current line
                    state_entry = tk.Entry(self, width=10, borderwidth=1, bg="lightblue", font=("Helvetica", 10, "bold"))
                    state_entry.grid(row=i, column=j+1, sticky="nsew", padx=5, pady=5)
                    dot.edge(chr(64 + i), str(line[j]), label=str(j))
                    state_entry.insert(tk.END, line[j])

            dot.node('start', shape='point')
            dot.edge('start', 'A', label='Start')

        self.final_state()
        dot_file = dot.render(format='png')

        # Open the rendered image
        image = Image.open(dot_file)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        label = tk.Label(self, image=photo)
        label.image = photo  # Keep a reference to the image to prevent garbage collection
        label.grid(row=self.rows+3, column=0, columnspan=self.columns+1, sticky="nsew", padx=5, pady=5)

    def close_screen(self):

        # Save the current dimensions
        with open("output.txt", "r") as file:
            lines = file.readlines()

        # Extracting the first line
        first_line = lines[0].strip().split()
        rows, columns = map(int, first_line)

        # Create a new table next to the original table
        new_table = Table(self.master, rows + 1, columns)
        new_table.create_mini_table()
        new_table.pack(side=tk.RIGHT, expand=True, fill="both", padx=10, pady=10)

    def create_circles(self):
        dot = Digraph()
        for i in range(1, self.rows + 1):
            if chr(64 + i) in self.final_alpha:
                dot.node(chr(64 + i), peripheries='2')
            else:
                dot.node(chr(64 + i))
        dot.node('start', shape='point')

        dot.edge('start', 'A', label='start')


        for i in range(1, self.rows+1):
            for j in range(0, self.columns):
                value = self.input_values[i - 1][j].get()
                if value and value.isalnum():
                    dot.edge(chr(64 + (i-1)), value.upper(), label=str(j))

        del dot.body[self.rows-1]
        dot_file = dot.render(format='png')

        # Open the rendered image
        image = Image.open(dot_file)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        label = tk.Label(self, image=photo)
        label.image = photo  # Keep a reference to the image to prevent garbage collection
        label.grid(row=self.rows+3, column=0, columnspan=self.columns+1, sticky="nsew", padx=5, pady=5)
        
    def print_input_values(self):

        self.close_button.config(state="normal")

        # Print the number of states, number of alphabets, and final states into a file
        with open("input.txt", "w") as file:
            file.write(f"{self.rows - 1} ")  # Subtract 1 to exclude the "States" row
            file.write(f"{self.columns}\n")
            for i in range(1, self.rows):
                state_entry = self.grid_slaves(row=i, column=0)[0]
                if state_entry.cget("state") == "disabled" and state_entry.cget("disabledbackground") == "yellow":
                    if state_entry.get() == "A (initial)":
                        file.write(f"{'A'}")
                    else:
                        file.write(f"{state_entry.get()}")

            # Print the values of the transition table
            for row in self.input_values:
                for value in row:
                    file.write(value.get())
                file.write("\n")

        os.startfile(r"cFile.exe")
        self.create_circles()
      
    def highlight_final_state(self):
        final_state = simpledialog.askstring("Input", "Enter the final state:", parent=self.master)
        if final_state == 'A':
            state_entry = self.grid_slaves(row=1, column=0)[0]
            state_entry.config(bg="yellow")
            state_entry.config(state=tk.DISABLED, disabledbackground="yellow")
            self.final_alpha.add('A')
        else:
            self.final_alpha.add(final_state)
            if final_state:
                for i in range(1, self.rows):
                    state_entry = self.grid_slaves(row=i, column=0)[0]
                    if state_entry.cget("state") == "disabled" and state_entry.cget("disabledbackground") == "yellow":
                        continue
                    if state_entry.get() == final_state:
                        state_entry.config(bg="yellow")
                        state_entry.config(state=tk.DISABLED, disabledbackground="yellow")
                    else:
                        state_entry.config(state=tk.DISABLED)

class CustomDialog(simpledialog.Dialog):
    
    def body(self, master):
        # Set background color and padding for the dialog
        master.configure(bg="#c7c2c7")
        master.grid_rowconfigure(2, minsize=20)
        
        # Create labels and entries for number of states and alphabets
        tk.Label(master, text="Enter number of states:", font=("Arial", 10, "bold"), bg="#c7c2c7", fg="#333").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(master, text="Enter number of alphabets:", font=("Arial", 10, "bold"), bg="#c7c2c7", fg="#333").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.num_states_entry = tk.Entry(master, font=("Arial", 10), bg="#fff", bd=2, relief=tk.GROOVE)
        self.num_states_entry.grid(row=0, column=1, padx=10, pady=5)
        
        self.num_alphabets_entry = tk.Entry(master, font=("Arial", 10), bg="#fff", bd=2, relief=tk.GROOVE)
        self.num_alphabets_entry.grid(row=1, column=1, padx=10, pady=5)
        self.credits()

    def apply(self):
        
        self.num_states = int(self.num_states_entry.get())
        self.num_alphabets = int(self.num_alphabets_entry.get())

    def buttonbox(self):
        # Override the buttonbox method to customize the OK and Cancel buttons
        
        box = tk.Frame(self)

        # Create the OK button with a custom style
        w = tk.Button(box, text="okay!!", width=7, bg="#5ffa7a", fg="black", font=("Arial", 10, "bold"), bd=2, relief=tk.FLAT, command=self.ok, padx=5, pady=5)
        w.pack(side="left", padx=5, pady=5)

        # Create the Cancel button with a custom style
        w = tk.Button(box, text="cancel :(", width=7, bg="#fa5f5f", fg="black", font=("Arial", 10, "bold"), bd=2, relief=tk.FLAT, command=self.cancel, padx=5, pady=5)
        w.pack(side="left", padx=5, pady=5)

        box.pack()

    def credits(self):
        # Create a frame for the credits
        credits_frame = tk.Frame(self, bg="lightblue")
        credits_frame.pack(side="bottom", fill="x", pady=8)

        # Display the credits in the frame with centered text
        credits_label = tk.Label(credits_frame, text="Designed by: Asim, Arham, Waniya", font=("Arial", 10,"bold"), bg="lightblue", fg="#333", anchor="center")
        credits_label.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        # Add padding on the right side for spacing
        spacer = tk.Label(credits_frame, text="", bg="lightblue")
        spacer.pack(side="right", fill="x", padx=5, pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    root.title("DFA MINIMIZATION")
    
    # Get number of states and alphabets from user
    dialog = CustomDialog(root)

    # Retrieve the values entered in the dialog
    num_states = dialog.num_states
    num_alphabets = dialog.num_alphabets
    
    if num_states and num_alphabets:
        root.deiconify()  
        table = Table(root, num_states+1, num_alphabets)  # Add 1 to include the "States" row
        table.create_table()
        table.pack(side=tk.LEFT, expand=True, fill="both", padx=10, pady=10)
        root.mainloop()
