import tkinter as tk
from tkinter import filedialog, messagebox, Canvas, Frame
from PIL import Image, ImageTk, ImageDraw, ImageFont
import qrcode
import os
from fpdf import FPDF
import textwrap

class StudentIDCardGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Student ID Card Generator - Two Sided")
        self.root.geometry("1000x850")
        self.root.configure(bg="#f0f8ff")

        # Variables
        self.student_photo_path = None
        self.current_id_card_front = None
        self.current_id_card_back = None
        self.current_student_data = {}

        self.setup_gui()

    def setup_gui(self):
        main_frame = tk.Frame(self.root, bg="#f0f8ff")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(main_frame, text="🎓 STUDENT ID CARD GENERATOR",
                 font=("Arial", 20, "bold"), bg="#f0f8ff", fg="#2c3e50").pack(pady=10)

        content_frame = tk.Frame(main_frame, bg="#f0f8ff")
        content_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), expand=False)

        right_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_input_form(left_frame)
        self.create_preview_area(right_frame)

    def create_input_form(self, parent):
        # Scrollable Frame
        canvas = Canvas(parent, bg="white", width=350)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = scrollable_frame

        tk.Label(frame, text="Student Information",
                 font=("Arial", 16, "bold"), bg="white", fg="#3998f8").pack(pady=10)

        # Photo
        photo_frame = tk.Frame(frame, bg="white")
        photo_frame.pack(pady=10)
        self.photo_label = tk.Label(photo_frame, text="No Photo Selected",
                                    bg="#ecf0f1", width=30, height=8,
                                    relief=tk.SUNKEN, font=("Arial", 10))
        self.photo_label.pack()
        tk.Button(photo_frame, text="📷 Upload Photo", command=self.upload_photo,
                  bg="#3498db", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5).pack(pady=5)

        # Fields
        labels = ["Full Name", "Roll No", "Branch", "College", "Address", "Mobile",
                  "Emergency No", "Date of Birth", "Blood Group", "Admitted Year"]
        self.entries = {}
        defaults = ["", "", "", "Pillai College of Engineering", "", "", "", "", "", ""]
        fields_frame = tk.Frame(frame, bg="white")
        fields_frame.pack(pady=10, fill=tk.X)
        for i, label in enumerate(labels):
            tk.Label(fields_frame, text=label + ":", bg="white", font=("Arial", 11)).grid(row=i, column=0, sticky='w', pady=3)
            e = tk.Entry(fields_frame, width=25, font=("Arial", 11))
            e.grid(row=i, column=1, pady=3, padx=5)
            e.insert(0, defaults[i])
            self.entries[label] = e

        # Buttons
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=10, fill=tk.X)
        tk.Button(btn_frame, text="🆔 Generate ID Card", command=self.generate_card,
                  bg="#27ae60", fg="white").pack(fill=tk.X, pady=3)
        tk.Button(btn_frame, text="👈 Front Side", command=lambda: self.show_preview("front"),
                  bg="#2980b9", fg="white").pack(fill=tk.X, pady=3)
        tk.Button(btn_frame, text="👉 Back Side", command=lambda: self.show_preview("back"),
                  bg="#8e44ad", fg="white").pack(fill=tk.X, pady=3)
        tk.Button(btn_frame, text="💾 Save Front PNG", command=self.save_front_png,
                  bg="#e67e22", fg="white").pack(fill=tk.X, pady=3)
        tk.Button(btn_frame, text="💾 Save Back PNG", command=self.save_back_png,
                  bg="#e67e22", fg="white").pack(fill=tk.X, pady=3)
        tk.Button(btn_frame, text="📄 Download PDF (Front+Back)", command=self.download_pdf,
                  bg="#e74c3c", fg="white").pack(fill=tk.X, pady=3)

    def create_preview_area(self, parent):
        frame = tk.Frame(parent, bg="white", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame, text="ID Card Preview", font=("Arial", 16, "bold"),
                 bg="white", fg="#34495e").pack(pady=10)
        self.preview_canvas = tk.Canvas(frame, bg="#ecf0f1", width=400, height=250,
                                        relief=tk.SUNKEN, bd=2)
        self.preview_canvas.pack(pady=10, fill=tk.BOTH, expand=True)
        self.preview_canvas.create_text(200, 125, text="Preview will appear here",
                                        font=("Arial", 12), fill="#7f8c8d", justify=tk.CENTER)

    # Photo upload
    def upload_photo(self):
        path = filedialog.askopenfilename(title="Select Photo", filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if path:
            self.student_photo_path = path
            img = Image.open(path)
            img.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(img)
            self.photo_label.configure(image=photo, text="")
            self.photo_label.image = photo

    # Generate card
    def generate_card(self):
        data = {k: e.get().strip() for k, e in self.entries.items()}
        if not all([data["Full Name"], data["Roll No"], data["Branch"]]):
            messagebox.showerror("Error", "Fill required fields!")
            return
        if not self.student_photo_path:
            messagebox.showerror("Error", "Upload a photo!")
            return
        self.current_student_data = data
        self.create_front_card(data)
        self.create_back_card(data)
        self.show_preview("front")
        messagebox.showinfo("Success", "ID Card generated!")

    # Front card
    def create_front_card(self, data):
        w, h = 400, 250
        card = Image.new("RGB", (w, h), "#fefefe")
        draw = ImageDraw.Draw(card)
        draw.rectangle([0, 0, w, 40], fill="#2c3e50")
        draw.rectangle([0, h - 30, w, h], fill="#2c3e50")
        draw.rectangle([0, 0, w - 1, h - 1], outline="#34495e", width=3)
        draw.rectangle([5, 5, w - 6, h - 6], outline="#bdc3c7", width=1)

        # Paste photo
        try:
            img = Image.open(self.student_photo_path).resize((80, 100))
            card.paste(img, (30, 60))
        except:
            pass

        # Fonts
        try:
            font_title = ImageFont.truetype("arialbd.ttf", 16)
            font_normal = ImageFont.truetype("arial.ttf", 12)
            font_small = ImageFont.truetype("arial.ttf", 10)
        except:
            font_title = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()

        draw.text((w // 2, 10), data["College"], fill="white", font=font_title, anchor="mm")
        draw.text((120, 60), f"Name: {data['Full Name']}", fill="black", font=font_normal)
        draw.text((120, 85), f"Roll No: {data['Roll No']}", fill="black", font=font_normal)
        draw.text((120, 110), f"Branch: {data['Branch']}", fill="black", font=font_normal)
        draw.text((150, h - 20), "Official Student ID", fill="white", font=font_small)

        # QR Code
        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(f"Name:{data['Full Name']}\nRoll:{data['Roll No']}\nBranch:{data['Branch']}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((70, 70))
        card.paste(qr_img, (w - 100, 150))

        self.current_id_card_front = card

    # Back card
    def create_back_card(self, data):
        w, h = 400, 250
        card = Image.new("RGB", (w, h), "#fef9e7")
        draw = ImageDraw.Draw(card)
        draw.rectangle([0, 0, w - 1, h - 1], outline="#34495e", width=3)
        draw.rectangle([5, 5, w - 6, h - 6], outline="#bdc3c7", width=1)

        try:
            font_title = ImageFont.truetype("arialbd.ttf", 14)
            font_small = ImageFont.truetype("arial.ttf", 10)
        except:
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()

        draw.text((w // 2, 20), "Student Details - Back Side", fill="#2c3e50", font=font_title, anchor="mm")

        y = 50
        for key in ["Full Name", "Roll No", "Branch", "College", "Address", "Mobile",
                    "Emergency No", "Date of Birth", "Blood Group", "Admitted Year"]:
            text = f"{key}: {data.get(key, '')}"
            lines = textwrap.wrap(text, width=40)
            for line in lines:
                draw.text((20, y), line, fill="black", font=font_small)
                y += 12

        y += 5
        instructions = ["1. Carry this ID at all times.",
                        "2. Do not lend to others.",
                        "3. Notify administration if lost."]
        for ins in instructions:
            draw.text((20, y), ins, fill="red", font=font_small)
            y += 12

        self.current_id_card_back = card

    # Preview display
    def show_preview(self, side):
        if side == "front" and self.current_id_card_front:
            self.update_preview(self.current_id_card_front)
        elif side == "back" and self.current_id_card_back:
            self.update_preview(self.current_id_card_back)

    def update_preview(self, img):
        preview_img = img.resize((380, 230))
        photo = ImageTk.PhotoImage(preview_img)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(200, 125, image=photo)
        self.preview_canvas.image = photo

    # Save PNGs
    def save_front_png(self):
        if self.current_id_card_front:
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if path:
                self.current_id_card_front.save(path)
                messagebox.showinfo("Saved", f"Front saved as {path}")

    def save_back_png(self):
        if self.current_id_card_back:
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if path:
                self.current_id_card_back.save(path)
                messagebox.showinfo("Saved", f"Back saved as {path}")

    # PDF download
    def download_pdf(self):
        if not (self.current_id_card_front and self.current_id_card_back):
            self.generate_card()
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            pdf = FPDF()
            tmp_front = "tmp_front.png"
            tmp_back = "tmp_back.png"
            self.current_id_card_front.save(tmp_front)
            self.current_id_card_back.save(tmp_back)
            pdf.add_page()
            pdf.image(tmp_front, x=10, y=10, w=190)
            pdf.add_page()
            pdf.image(tmp_back, x=10, y=10, w=190)
            pdf.output(path)
            os.remove(tmp_front)
            os.remove(tmp_back)
            messagebox.showinfo("Saved", f"PDF downloaded as {path}")

def main():
    root = tk.Tk()
    app = StudentIDCardGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
