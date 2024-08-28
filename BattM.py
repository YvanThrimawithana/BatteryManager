import psutil
import tkinter as tk
from tkinter import ttk
import threading
import time
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import winsound  # For playing notification sound

class BatteryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Battery Monitor")
        self.root.geometry("300x150")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Battery Percentage Label
        self.percent_label = ttk.Label(root, text="Battery: --%", font=("Arial", 14))
        self.percent_label.pack(pady=20)
        
        # Update battery status
        self.update_battery_status()

        # Start the battery monitoring thread
        self.monitor_thread = threading.Thread(target=self.battery_monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        # Setup system tray icon
        self.icon = self.create_tray_icon()
        self.icon.run_detached()

    def update_battery_status(self):
        battery = psutil.sensors_battery()
        percent = battery.percent
        self.percent_label.config(text=f"Battery: {percent}%")
        self.root.after(10000, self.update_battery_status)  # Update every 10 seconds

    def battery_monitor(self):
        self.show_popup()
        while True:
            battery = psutil.sensors_battery()
            percent = battery.percent
            if percent >= 85:
                self.show_popup()
            time.sleep(60)  # Check battery status every 60 seconds

    def show_popup(self):
        # Play notification sound
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        
        # Create and display popup
        popup = tk.Toplevel(self.root)
        popup.geometry("300x100+10+10")  # Position the popup in the bottom left corner
        popup.overrideredirect(1)  # Remove window borders
        popup.attributes("-topmost", True)  # Keep the popup on top

        label = tk.Label(popup, text="Battery level is 85% or above!", font=("Arial", 12))
        label.pack(expand=True)

        popup.after(5000, popup.destroy)  # Auto-close popup after 5 seconds

    def hide_window(self):
        self.root.withdraw()  # Hide the main window

    def on_quit(self, icon, item):
        self.icon.stop()
        self.root.quit()

    def show_window(self, icon, item):
        self.root.deiconify()

    def create_tray_icon(self):
        # Create a blank icon
        image = Image.new("RGB", (64, 64), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 63, 63), fill="black")

        # Add tray icon with a menu
        menu = (
            item('Show', self.show_window),
            item('Quit', self.on_quit)
        )
        icon = pystray.Icon("Battery Monitor", image, "Battery Monitor", menu)
        return icon

if __name__ == "__main__":
    root = tk.Tk()
    app = BatteryApp(root)
    root.mainloop()
