import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from zipfile import ZipFile


class DragDropEntry(tk.Entry):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(bg="white")  # Set default background color

    def set_files(self, file_paths):
        self.delete(0, tk.END)
        self.insert(tk.END, "\n".join(file_paths))


class DataInputTool(tk.Frame):
    background_color = "#3b5998"
    label_color = "#ffffff"
    entry_background_color = "#ffffff"
    entry_foreground_color = "#000000"
    button_background_color = "#1877f2"
    button_foreground_color = "#ffffff"

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(expand=True, fill='both')

        # GUI setup
        self.configure(bg=self.background_color)

        # Model name input
        tk.Label(self, text="Model Name:", bg=self.background_color, fg=self.label_color,
                 font=("Helvetica", 12)).grid(row=0, column=0, pady=(20, 10), padx=(10, 5), sticky="e")
        self.model_entry = tk.Entry(self, width=30, bg=self.entry_background_color, fg=self.entry_foreground_color,
                                    font=("Helvetica", 12))
        self.model_entry.grid(row=0, column=1, pady=(20, 10), padx=(5, 10), sticky="w")

        # Zip files input with drag and drop support
        self.zip_entry = DragDropEntry(self, width=50, bg=self.entry_background_color, fg=self.entry_foreground_color,
                                       font=("Helvetica", 12))
        self.zip_entry.grid(row=1, column=0, columnspan=2, pady=(10, 10), padx=10)

        # Browse button
        self.browse_button = tk.Button(self, text="Browse", command=self.browse_files,
                                       bg=self.button_background_color, fg=self.button_foreground_color,
                                       font=("Helvetica", 12))
        self.browse_button.grid(row=1, column=2, pady=(10, 10), padx=(0, 10))

        # Start processing button
        self.start_button = tk.Button(self, text="Start Processing", command=self.start_processing,
                                      bg=self.button_background_color, fg=self.button_foreground_color,
                                      font=("Helvetica", 12))
        self.start_button.grid(row=2, column=0, columnspan=3, pady=(20, 20))

    def browse_files(self):
        file_paths = filedialog.askopenfilenames(initialdir="/", title="Select zip files",
                                                 filetypes=(("Zip files", "*.zip"), ("All files", "*.*")))
        if file_paths:
            self.zip_entry.set_files(file_paths)

    def start_processing(self):
        model_name = self.model_entry.get().strip()
        zip_files = self.zip_entry.get().strip().split('\n')  # Split paths by newline

        if not model_name:
            messagebox.showerror("Error", "Please enter a model name.")
            return

        if not zip_files:
            messagebox.showerror("Error", "Please select at least one zip file.")
            return

        try:
            # Create 'res' directory if it doesn't exist
            res_directory = os.path.join(os.getcwd(), "res")
            os.makedirs(res_directory, exist_ok=True)

            for zip_path in zip_files:
                if os.path.exists(zip_path):
                    # Extract zip files and organize data
                    self.extract_and_organize_zip(zip_path, res_directory, model_name)
                else:
                    messagebox.showwarning("Warning", f"File not found: {zip_path}")

            messagebox.showinfo("Success", f"Data organized successfully for model '{model_name}'.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    @staticmethod
    def extract_and_organize_zip(zip_path, destination_folder, model_name):
        with ZipFile(zip_path, 'r') as zip_ref:
            # Extract contents of the zip file
            extract_path = os.path.join(destination_folder, "Extracted")
            os.makedirs(extract_path, exist_ok=True)
            zip_ref.extractall(extract_path)

            # Organize extracted data
            DataInputTool.organize_data(extract_path, destination_folder, model_name)

    @staticmethod
    def organize_data(extract_path, destination_folder, model_name):
        for folder_name in os.listdir(extract_path):
            folder_path = os.path.join(extract_path, folder_name)

            if os.path.isdir(folder_path):
                # Create model-specific directory
                model_dir = os.path.join(destination_folder, model_name)
                os.makedirs(model_dir, exist_ok=True)

                # Create folder-specific directories
                folder_dir = os.path.join(model_dir, folder_name)
                train_dir = os.path.join(folder_dir, "train")
                test_dir = os.path.join(folder_dir, "test")
                os.makedirs(train_dir, exist_ok=True)
                os.makedirs(test_dir, exist_ok=True)

                # Split files into train and test sets
                files = os.listdir(folder_path)
                num_train = int(0.8 * len(files))  # 80% for training
                train_files = files[:num_train]
                test_files = files[num_train:]

                # Copy files to respective directories
                for file in train_files:
                    shutil.copy(os.path.join(folder_path, file), os.path.join(train_dir, file))
                for file in test_files:
                    shutil.copy(os.path.join(folder_path, file), os.path.join(test_dir, file))


# Create the main window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Data Input Tool")
    app = DataInputTool(root)
    root.mainloop()
