import tkinter as tk
from auth import AuthScreen
from dashboard import Dashboard

class DesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chemical Equipment Parameter Visualizer")
        self.geometry("1000x700")
        self.state('zoomed') # Start maximized

        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = AuthScreen(self, on_login_success=self.show_dashboard)

    def show_dashboard(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = Dashboard(self, on_logout=self.show_login)

if __name__ == "__main__":
    app = DesktopApp()
    app.mainloop()
