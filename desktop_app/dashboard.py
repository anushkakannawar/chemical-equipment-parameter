import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from api_client import client
from charts import ChartManager
import threading

class Dashboard(tk.Frame):
    def __init__(self, master, on_logout):
        super().__init__(master)
        self.master = master
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)
        
        self.current_summary = None
        self.create_widgets()
        self.load_initial_data()

    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#001529", height=60)
        header.pack(fill="x", side="top")
        
        tk.Label(header, text="Chemical Equipment Visualizer", bg="#001529", fg="white", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=10)
        
        tk.Button(header, text="Logout", command=self.logout, bg="#ff4d4f", fg="white", bd=0, padx=10).pack(side="right", padx=20, pady=10)

        # Main Layout
        content = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        content.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(content, bg="#ffffff", width=250)
        content.add(sidebar, minsize=200)

        # Upload Section
        tk.Button(sidebar, text="Upload CSV File", command=self.upload_file, bg="#1890ff", fg="white", pady=5).pack(fill="x", padx=10, pady=10)

        # History Section
        tk.Label(sidebar, text="History (Last 5)", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.history_listbox = tk.Listbox(sidebar, bd=0, highlightthickness=0, bg="#fafafa", selectmode="single")
        self.history_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)

        # Main Content Area
        main_area = tk.Frame(content, bg="#f0f2f5")
        content.add(main_area)

        # Stats Row
        self.stats_frame = tk.Frame(main_area, bg="#f0f2f5")
        self.stats_frame.pack(fill="x", padx=20, pady=20)
        
        self.stat_labels = {}
        for idx, title in enumerate(["Avg Flowrate", "Avg Pressure", "Avg Temperature"]):
            card = tk.Frame(self.stats_frame, bg="white", padx=15, pady=15)
            card.grid(row=0, column=idx, padx=10, sticky="ew")
            tk.Label(card, text=title, bg="white", fg="#8c8c8c").pack(anchor="w")
            val_label = tk.Label(card, text="--", bg="white", font=("Arial", 18, "bold"))
            val_label.pack(anchor="w")
            self.stat_labels[title] = val_label
            
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)
        self.stats_frame.grid_columnconfigure(2, weight=1)

        # Charts Area
        self.charts_frame = tk.Frame(main_area, bg="white", height=300)
        self.charts_frame.pack(fill="x",  padx=20, pady=(0, 20))
        # Prevent frame from collapsing
        self.charts_frame.pack_propagate(False) 
        
        self.chart_manager = ChartManager(self.charts_frame)

        # Data Table Area
        table_frame = tk.Frame(main_area, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tk.Label(table_frame, text="Equipment Data", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=10)

        # Treeview Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        # Treeview
        columns = ("Name", "Type", "Flowrate", "Pressure", "Temperature")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # Actions (Download PDF)
        self.download_btn = tk.Button(header, text="Download Report", command=self.download_report, bg="#52c41a", fg="white", bd=0, padx=10)
        # Packed later when data available

    def logout(self):
        self.on_logout()

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        # Thread the upload
        threading.Thread(target=self._upload_file_thread, args=(file_path,), daemon=True).start()

    def _upload_file_thread(self, file_path):
        success, result = client.upload_file(file_path)
        self.master.after(0, self._handle_upload_result, success, result)

    def _handle_upload_result(self, success, result):
        if success:
            messagebox.showinfo("Success", "File uploaded successfully!")
            self.load_initial_data()
        else:
            messagebox.showerror("Error", f"Upload failed: {result}")

    def load_initial_data(self):
        # Run in thread to avoid UI freeze
        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        summary = client.get_summary()
        history = client.get_history()
        
        self.master.after(0, self._update_ui, summary, history)

    def _update_ui(self, summary, history):
        # Update History List
        self.history_items = history  # Store full objects
        self.history_listbox.delete(0, tk.END)
        for item in history:
            self.history_listbox.insert(tk.END, f"{item['filename']} ({item['upload_date'][:10]})")

        # Update Dashboard
        if summary:
            self.update_dashboard_view(summary)

    def update_dashboard_view(self, summary):
        self.current_summary = summary
        
        # Update Stats
        self.stat_labels["Avg Flowrate"].config(text=f"{summary.get('avg_flowrate', 0):.2f}")
        self.stat_labels["Avg Pressure"].config(text=f"{summary.get('avg_pressure', 0):.2f}")
        self.stat_labels["Avg Temperature"].config(text=f"{summary.get('avg_temperature', 0):.2f}")

        # Update Charts
        self.chart_manager.render_charts(summary)

        # Update Table
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configure tags for striping
        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('even', background='#f9f9f9')

        # Populate new data
        if 'data' in summary:
            for idx, item in enumerate(summary['data']):
                tag = 'even' if idx % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=(
                    item.get('Equipment Name', ''),
                    item.get('Type', ''),
                    item.get('Flowrate', ''),
                    item.get('Pressure', ''),
                    item.get('Temperature', '')
                ), tags=(tag,))

        # Show Download Button
        self.download_btn.pack(side="right", padx=10, pady=10)

    def on_history_select(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            item = self.history_items[index]
            # Ideally fetch full summary by ID if needed, 
            # but usually history items might have summary attached or call GET
            # For now update view directly assuming structure match
            self.update_dashboard_view(item)

    def download_report(self):
        if not self.current_summary:
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                 initialfile=f"report_{self.current_summary['filename']}.pdf",
                                                 filetypes=[("PDF Files", "*.pdf")])
        if not save_path:
            return

        success, msg = client.download_report(self.current_summary['id'], save_path)
        if success:
            messagebox.showinfo("Success", "Report downloaded successfully!")
        else:
            messagebox.showerror("Error", f"Download failed: {msg}")
