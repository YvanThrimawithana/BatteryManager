import psutil
import tkinter as tk
from tkinter import ttk
import threading
import time
import pystray
from pystray import MenuItem as item
from PIL import Image
import winsound
import json
import os

class BatteryApp:
    SETTINGS_FILE = "settings.json"

    def __init__(self, root):
        self.root = root
        self.root.title("Battery Monitor")
        self.root.geometry("300x300")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Initialize user-defined thresholds
        self.max_charge = tk.IntVar(value=85)
        self.min_charge = tk.IntVar(value=20)

        # Initialize error message variable
        self.error_message = tk.StringVar()

        # Load settings if available
        self.load_settings()

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0", foreground="#333")
        self.style.configure("TButton", font=("Helvetica", 12), padding=5)

        # Set background color
        self.root.configure(bg="#f0f0f0")
        self.root.iconphoto(True, tk.PhotoImage(file="app_icon.png"))

        # Battery Percentage Label
        self.percent_label = ttk.Label(root, text="Battery: --%", font=("Helvetica", 15, "bold"))
        self.percent_label.pack(pady=15)

        # Max Charge Entry
        self.create_entry_section("Max Charge (%):", self.max_charge).pack(pady=5)

        # Min Charge Entry
        self.create_entry_section("Min Charge (%):", self.min_charge).pack(pady=5)

        # Save Button
        save_button = ttk.Button(root, text="Save Settings", command=self.save_settings)
        save_button.pack(pady=10)

        # Error Message Label
        self.error_label = ttk.Label(root, textvariable=self.error_message, font=("Helvetica", 10), foreground="red", background="#f0f0f0")
        self.error_label.pack(pady=5)

        # Update battery status
        self.update_battery_status()

        # Start the battery monitoring thread
        self.monitor_thread = threading.Thread(target=self.battery_monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        # Setup system tray icon
        self.icon = self.create_tray_icon()
        self.icon.run_detached()

    def create_entry_section(self, label_text, var):
        frame = ttk.Frame(self.root, padding=5)
        frame.configure(style="TFrame")

        label = ttk.Label(frame, text=label_text)
        label.pack(side=tk.LEFT, padx=5)

        entry = tk.Entry(frame, textvariable=var, width=6, font=("Helvetica", 12))  # Using tk.Entry with font size 12
        entry.pack(side=tk.LEFT, padx=5)

        return frame

    def save_settings(self):
        try:
            max_value = int(self.max_charge.get())
            min_value = int(self.min_charge.get())
            if 0 <= min_value < max_value <= 100:
                settings = {
                    "max_charge": max_value,
                    "min_charge": min_value
                }
                with open(self.SETTINGS_FILE, 'w') as file:
                    json.dump(settings, file)
                print(f"Settings saved. Max charge: {max_value}%, Min charge: {min_value}%")
                self.error_message.set("")  # Clear any previous error message
            else:
                self.error_message.set("Invalid settings. Ensure min charge is less than max charge and both are between 0 and 100.")
        except ValueError:
            self.error_message.set("Invalid input. Please enter integer values.")

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, 'r') as file:
                settings = json.load(file)
                self.max_charge.set(settings.get("max_charge", 85))
                self.min_charge.set(settings.get("min_charge", 20))

    def update_battery_status(self):
        battery = psutil.sensors_battery()
        percent = battery.percent
        self.percent_label.config(text=f"Battery: {percent}%")
        self.root.after(10000, self.update_battery_status)  # Update every 10 seconds

    def battery_monitor(self):
        while True:
            battery = psutil.sensors_battery()
            percent = battery.percent
            power_plugged = battery.power_plugged
            max_value = self.max_charge.get()
            min_value = self.min_charge.get()

            # Print debug information
            print(f"Battery Percent: {percent}, Power Plugged: {power_plugged}, Max: {max_value}, Min: {min_value}")

            if power_plugged:
                # Battery is charging
                if percent >= max_value:
                    print(f"Charging notification triggered: Battery at {percent}%, Max threshold {max_value}%")
                    self.show_popup(f"Battery level is {percent}%. Unplug your charger!")
            else:
                # Battery is not charging
                if percent <= min_value:
                    print(f"Discharging notification triggered: Battery at {percent}%, Min threshold {min_value}%")
                    self.show_popup(f"Battery level is {percent}%. Plug in your charger!")

            time.sleep(60)  # Check battery status every 60 seconds

    def show_popup(self, message):
        # Print debug information for popup
        print(f"Showing popup with message: {message}")
        
        # Play notification sound
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        
        # Create and display popup
        popup = tk.Toplevel(self.root)
        popup.geometry("300x80")  # Smaller popup size
        popup.overrideredirect(1)  # Remove window borders
        popup.attributes("-topmost", True)  # Keep the popup on top
        popup.configure(bg="#ffffff")
        
        # Place the popup in the top-left corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        popup_x = 0
        popup_y = 0
        popup.geometry(f"300x80+{popup_x}+{popup_y}")

        label = tk.Label(popup, text=message, font=("Helvetica", 10), bg="#ffffff", fg="#333")
        label.pack(expand=True)

        # Add fade-in effect
        self.fade_in(popup)

        popup.after(10000, popup.destroy)

    def fade_in(self, widget, alpha=0.1):
        # Simple fade-in effect
        widget.attributes("-alpha", alpha)
        if alpha < 1.0:
            alpha += 0.05
            widget.after(50, lambda: self.fade_in(widget, alpha))
        else:
            widget.attributes("-alpha", 1.0)

    def hide_window(self):
        self.root.withdraw()  # Hide the main window

    def on_quit(self, icon, item):
        self.icon.stop()
        self.root.quit()
        self.root.destroy()  # Ensures the application is completely terminated

    def show_window(self, icon, item):
        self.root.deiconify()

    def create_tray_icon(self):
        # Load the tray icon
        icon_image = Image.open("tray_icon.ico")
        
        # Add tray icon with a menu
        menu = (
            item('Show', self.show_window),
            item('Quit', self.on_quit)
        )
        icon = pystray.Icon("Battery Monitor", icon_image, "Battery Monitor", menu)
        return icon

if __name__ == "__main__":
    root = tk.Tk()
    app = BatteryApp(root)
    root.mainloop()
