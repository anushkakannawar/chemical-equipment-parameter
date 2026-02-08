import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class ChartManager:
    def __init__(self, master):
        self.master = master
        self.figure = None
        self.canvas = None
        self._init_figure()

    def _init_figure(self):
        # Create a figure with 2 subplots once
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4), dpi=100)
        self.figure.patch.set_facecolor('#f0f2f5')
        self.figure.tight_layout()

        # Embed in Tkinter once
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def render_charts(self, summary_data):
        if not summary_data:
            return

        # Clear axes instead of destroying figure
        self.ax1.clear()
        self.ax2.clear()

        # 1. Pie Chart - Distribution
        type_dist = summary_data.get('type_distribution', {})
        labels = list(type_dist.keys())
        sizes = list(type_dist.values())
        
        if sizes:
            self.ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            self.ax1.axis('equal')
            self.ax1.set_title('Equipment Type Distribution')
        else:
            self.ax1.text(0.5, 0.5, 'No Data', ha='center')

        # 2. Bar Chart - Averages
        params = ['Flowrate', 'Pressure', 'Temperature']
        avgs = [
            summary_data.get('avg_flowrate', 0),
            summary_data.get('avg_pressure', 0),
            summary_data.get('avg_temperature', 0)
        ]

        self.ax2.bar(params, avgs, color=['#36a2eb', '#ff6384', '#ffcd56'])
        self.ax2.set_title('Average Parameters')
        self.ax2.set_ylabel('Value')

        # Redraw
        self.canvas.draw()

    def clear(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.figure)
