import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

class CorrosionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Okro Leaf Extract - Basic Media Corrosion Recommendations")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        # Title
        title_label = ttk.Label(root, text="Corrosion Inhibition Recommendations",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        subtitle_label = ttk.Label(root, text="Basic Media (NaOH) - Okro Leaf Extract",
                                  font=("Arial", 12))
        subtitle_label.pack(pady=5)

        # Input frame
        input_frame = ttk.LabelFrame(root, text="Input Parameters", padding=10)
        input_frame.pack(pady=10, padx=20, fill="x")

        # NaOH input
        ttk.Label(input_frame, text="NaOH Concentration (M):").grid(row=0, column=0, sticky="w", pady=5)
        self.naoh_var = tk.DoubleVar(value=1.5)
        naoh_spin = tk.Spinbox(input_frame, from_=0.5, to=3.0, increment=0.1,
                              textvariable=self.naoh_var, width=10)
        naoh_spin.grid(row=0, column=1, padx=10, pady=5)

        # Inhibitor input
        ttk.Label(input_frame, text="Inhibitor Concentration (ppm):").grid(row=1, column=0, sticky="w", pady=5)
        self.inhibitor_var = tk.IntVar(value=150)
        inhibitor_spin = tk.Spinbox(input_frame, from_=10, to=500, increment=25,
                                   textvariable=self.inhibitor_var, width=10)
        inhibitor_spin.grid(row=1, column=1, padx=10, pady=5)

        # Temperature input
        ttk.Label(input_frame, text="Temperature (°C):").grid(row=2, column=0, sticky="w", pady=5)
        self.temp_var = tk.IntVar(value=45)
        temp_spin = tk.Spinbox(input_frame, from_=20, to=100, increment=5,
                              textvariable=self.temp_var, width=10)
        temp_spin.grid(row=2, column=1, padx=10, pady=5)

        # Button
        self.recommend_btn = ttk.Button(root, text="Get Recommendation",
                                       command=self.get_recommendation)
        self.recommend_btn.pack(pady=20)

        # Results frame
        results_frame = ttk.LabelFrame(root, text="Recommendation Results", padding=10)
        results_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Results text area
        self.results_text = tk.Text(results_frame, height=15, width=50, wrap=tk.WORD,
                                   font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Enter parameters and click 'Get Recommendation'")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(fill="x", side="bottom")

        # Initial message
        self.display_initial_message()

    def get_recommendation(self):
        try:
            naoh = self.naoh_var.get()
            inhibitor = self.inhibitor_var.get()
            temp = self.temp_var.get()

            # Input validation
            if not (0.5 <= naoh <= 3.0):
                messagebox.showerror("Input Error", "NaOH concentration must be between 0.5 and 3.0 M")
                return
            if not (10 <= inhibitor <= 500):
                messagebox.showerror("Input Error", "Inhibitor concentration must be between 10 and 500 ppm")
                return
            if not (20 <= temp <= 100):
                messagebox.showerror("Input Error", "Temperature must be between 20 and 100 °C")
                return

            # Get recommendation
            recommended_ppm, risk_status, color = self.calculate_recommendation(naoh, inhibitor, temp)

            # Display results
            self.display_results(naoh, inhibitor, temp, recommended_ppm, risk_status)

            self.status_var.set("Recommendation generated successfully")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error generating recommendation")

    def calculate_recommendation(self, naoh, inhibitor, temp):
        """Calculate recommendation based on EDA patterns"""
        # Base recommendations by temperature
        if temp < 40:
            recommended_ppm = 125
        elif temp <= 50:
            recommended_ppm = 200
        else:  # temp > 50
            recommended_ppm = 200

        # Adjust for high NaOH concentration
        if naoh > 2.0:
            recommended_ppm = int(recommended_ppm * 1.5)

        # Risk assessment
        if inhibitor >= recommended_ppm and temp <= 45:
            risk_status = "SAFE"
            color = "green"
        elif inhibitor >= recommended_ppm * 0.75:
            risk_status = "MODERATE RISK"
            color = "orange"
        else:
            risk_status = "HIGH RISK"
            color = "red"

        return recommended_ppm, risk_status, color

    def display_results(self, naoh, inhibitor, temp, recommended_ppm, risk_status):
        self.results_text.delete(1.0, tk.END)

        # Color mapping for text
        color_tags = {
            "SAFE": "green",
            "MODERATE RISK": "orange",
            "HIGH RISK": "red"
        }

        self.results_text.tag_configure("green", foreground="green")
        self.results_text.tag_configure("orange", foreground="orange")
        self.results_text.tag_configure("red", foreground="red")
        self.results_text.tag_configure("bold", font=("Consolas", 10, "bold"))

        # Header
        self.results_text.insert(tk.END, "=== CORROSION RECOMMENDATION ===\n\n", "bold")

        # Input summary
        self.results_text.insert(tk.END, f"Input Parameters:\n")
        self.results_text.insert(tk.END, f"• NaOH Concentration: {naoh} M\n")
        self.results_text.insert(tk.END, f"• Inhibitor Concentration: {inhibitor} ppm\n")
        self.results_text.insert(tk.END, f"• Temperature: {temp} °C\n\n")

        # Recommendation
        self.results_text.insert(tk.END, f"Recommended Inhibitor Dose: {recommended_ppm} ppm\n")
        self.results_text.insert(tk.END, f"Risk Assessment: {risk_status}\n\n", color_tags.get(risk_status, "black"))

        # Additional guidance
        if inhibitor < recommended_ppm:
            shortfall = recommended_ppm - inhibitor
            self.results_text.insert(tk.END, f"💡 Consider increasing inhibitor by {shortfall} ppm for better protection\n")
        else:
            self.results_text.insert(tk.END, "✅ Current dose meets or exceeds recommendation\n")

        if naoh > 2.0:
            self.results_text.insert(tk.END, "⚠️ High NaOH concentration detected - increased inhibitor dose advised\n")

        if temp > 50:
            self.results_text.insert(tk.END, "⚠️ High temperature - monitor corrosion closely\n")

        # Footer
        self.results_text.insert(tk.END, "\n" + "="*50 + "\n", "bold")
        self.results_text.insert(tk.END, "Based on experimental data analysis of Okro leaf extract\n")
        self.results_text.insert(tk.END, "in basic media corrosion inhibition studies.")

    def display_initial_message(self):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Welcome to the Corrosion Inhibition Recommendation Tool!\n\n")
        self.results_text.insert(tk.END, "This tool provides engineering recommendations for using\n")
        self.results_text.insert(tk.END, "Okro leaf extract as a corrosion inhibitor in basic (NaOH) media.\n\n")
        self.results_text.insert(tk.END, "Recommendations are based on experimental data analysis patterns.\n\n")
        self.results_text.insert(tk.END, "Enter your parameters above and click 'Get Recommendation' to begin.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CorrosionGUI(root)
    root.mainloop()
