import customtkinter as ctk
import threading
import time
import sys

class NotificationSoul:
    """
    The 'Visual Awareness' of NIA's Safety System.
    Shows non-blocking alerts and confirmation prompts.
    """
    def __init__(self):
        self.root = None
        
    def show_alert(self, title: str, message: str, color="#a855f7", duration=5):
        """Shows a temporary, non-interactive toast notification."""
        def _run():
            ctk.set_appearance_mode("dark")
            self.root = ctk.CTk()
            self.root.title("NIA OS System Alert")
            self.root.geometry("400x120+20+20") # Top-left safe zone
            self.root.attributes("-topmost", True)
            self.root.overrideredirect(True) # Frameless
            self.root.configure(fg_color="#0a0a0a")

            # Border/Glow effect
            frame = ctk.CTkFrame(self.root, fg_color="#0a0a0a", border_width=2, border_color=color, corner_radius=15)
            frame.pack(fill="both", expand=True, padx=5, pady=5)

            title_label = ctk.CTkLabel(frame, text=title.upper(), font=("Orbitron", 10, "bold"), text_color=color)
            title_label.pack(pady=(15, 5))

            msg_label = ctk.CTkLabel(frame, text=message, font=("Inter", 13), text_color="#d1d1d1", wraplength=350)
            msg_label.pack(pady=5)

            # Auto-close
            threading.Timer(duration, lambda: self.root.destroy()).start()
            self.root.mainloop()

        threading.Thread(target=_run, daemon=True).start()

    def show_confirmation_prompt(self, question: str):
        """
        Shows a persistent popup for 'Moderate/Critical' tasks.
        Wait for Voice mode (external) to confirm.
        """
        def _run():
            ctk.set_appearance_mode("dark")
            app = ctk.CTk()
            app.title("NIA SOVEREIGN CONFIRMATION")
            # Center screen
            screen_w = app.winfo_screenwidth()
            screen_h = app.winfo_screenheight()
            w, h = 500, 180
            app.geometry(f"{w}x{h}+{int((screen_w-w)/2)}+{int((screen_h-h)/2)}")
            app.attributes("-topmost", True)
            app.overrideredirect(True)
            app.configure(fg_color="#0a0a0a")

            frame = ctk.CTkFrame(app, fg_color="#0a0a0a", border_width=2, border_color="#f59e0b", corner_radius=20)
            frame.pack(fill="both", expand=True, padx=10, pady=10)

            ctk.CTkLabel(frame, text="CRITICAL ACTION REQUESTED", font=("Orbitron", 11, "bold"), text_color="#f59e0b").pack(pady=(20, 10))
            ctk.CTkLabel(frame, text=question, font=("Inter", 16), text_color="white", wraplength=450).pack(pady=10)
            
            ctk.CTkLabel(frame, text="[ LISTENING FOR VOICE CONFIRMATION... ]", font=("Inter", 10), text_color="#737373").pack(pady=10)

            # Pulse effect simulated by changing border color? 
            # (Just a static high-contrast UI for now)
            
            # This popup will be destroyed externally by the chat core when confirmation is received
            # Or we add a safety timeout?
            threading.Timer(30, lambda: app.destroy()).start()
            app.mainloop()

        threading.Thread(target=_run, daemon=True).start()

if __name__ == "__main__":
    notifier = NotificationSoul()
    notifier.show_alert("Hardware Sync", "Volume set to 25% for Boss.")
    time.sleep(2)
    notifier.show_confirmation_prompt("Do you really want me to Shut Down your device, Boss?")
