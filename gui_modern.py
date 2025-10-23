# gui_modern.py
import customtkinter as ctk
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
from Logic import PersonalityLogic
from questions import QuestionSet

# Optional: try to import shaping libraries
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _HAS_ARABIC_LIBS = True
except Exception:
    _HAS_ARABIC_LIBS = False

# -------------------------
# تنظیم خودکار فونت: لیست اولویت‌ها
PREFERRED_FONTS = [
    "Vazirmatn", "IranSans", "IRANSans", "Tahoma", "Arial", "Helvetica"
]

def choose_font(preferred_list, default_size=14):
    available = set(tkfont.families())
    for name in preferred_list:
        if name in available:
            return (name, default_size)
    return (tkfont.nametofont("TkDefaultFont").cget("family"), default_size)

def reshape_text(text: str) -> str:
    """
    اگر arabic_reshaper و python-bidi نصب باشند:
      - متن فارسی را reshape می‌کند تا حروف به‌درستی متصل شوند
      - سپس توسط get_display جهت RTL را اصلاح می‌کند
    در غیر این‌صورت متن را بدون تغییر برمی‌گرداند (fallback).
    """
    if not _HAS_ARABIC_LIBS:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    except Exception:
        return text

# تنظیمات ظاهری کلی customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PersonalityApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(reshape_text(" Test  ✨"))
        self.geometry("720x540")
        self.resizable(False, False)

        self.font_main = choose_font(PREFERRED_FONTS, default_size=20)
        self.font_sub = choose_font(PREFERRED_FONTS, default_size=16)
        self.font_small = choose_font(PREFERRED_FONTS, default_size=13)

        self.gender = None
        self.answers = []
        self.questions = []
        self.current_index = 0

        self.create_welcome_screen()

    def create_welcome_screen(self):
        for w in self.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self, corner_radius=20)
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        title = ctk.CTkLabel(frame, text=reshape_text("به تست شخصیت‌شناسی خوش آمدید 🌟"),
                             font=self.font_main)
        title.pack(pady=28)

        subtitle = ctk.CTkLabel(frame, text=reshape_text("لطفاً جنسیت خود را انتخاب کنید:"),
                                font=self.font_sub)
        subtitle.pack(pady=12)

        gender_frame = ctk.CTkFrame(frame, fg_color="transparent")
        gender_frame.pack(pady=26)

        btn_female = ctk.CTkButton(gender_frame, text=reshape_text("👩  زن"), width=160, height=52,
                                   font=self.font_sub,
                                   command=lambda: self.start_test("زن"))
        btn_female.grid(row=0, column=0, padx=20)

        btn_male = ctk.CTkButton(gender_frame, text=reshape_text("👨  مرد"), width=160, height=52,
                                 font=self.font_sub,
                                 command=lambda: self.start_test("مرد"))
        btn_male.grid(row=0, column=1, padx=20)

    def start_test(self, gender):
        self.gender = gender
        self.qs = QuestionSet(gender)
        self.questions = self.qs.questions
        self.answers = []
        self.current_index = 0
        self.show_question()

    def show_question(self):
        for w in self.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self, corner_radius=20)
        frame.pack(expand=True, fill="both", padx=34, pady=34)

        q_text = self.questions[self.current_index]
        question_label = ctk.CTkLabel(
            frame,
            text=reshape_text(f"{self.current_index + 1}. {q_text}"),
            wraplength=640, justify="center",
            font=self.font_sub
        )
        question_label.pack(pady=36)

        # slider variable: use Tkinter IntVar for robust get/set
        self.answer_var = tk.IntVar(value=3)

        slider = ctk.CTkSlider(
            frame, from_=1, to=5, number_of_steps=4,
            variable=self.answer_var, width=460
        )
        slider.pack(pady=22)

        labels_frame = ctk.CTkFrame(frame, fg_color="transparent")
        labels_frame.pack(pady=6)
        left_label = tk.Label(labels_frame, text=reshape_text("1  =  کاملاً مخالفم"),
                              font=self.font_small)
        left_label.grid(row=0, column=0, padx=40)
        right_label = tk.Label(labels_frame, text=reshape_text("5  =  کاملاً موافقم"),
                               font=self.font_small)
        right_label.grid(row=0, column=1, padx=40)

        next_btn = ctk.CTkButton(frame, text=reshape_text("سؤال بعد ➡️"), width=220, height=52,
                                 font=self.font_sub,
                                 command=self.next_question)
        next_btn.pack(pady=38)

    def next_question(self):
        answer = self.answer_var.get()
        if answer not in [1, 2, 3, 4, 5]:
            messagebox.showwarning(reshape_text("هشدار"), reshape_text("لطفاً یک عدد بین 1 تا 5 انتخاب کنید."))
            return

        self.answers.append(answer)
        self.current_index += 1

        if self.current_index < len(self.questions):
            self.show_question()
        else:
            self.show_result()

    def show_result(self):
        for w in self.winfo_children():
            w.destroy()

        logic = PersonalityLogic(self.gender, self.answers)
        result = logic.analyze()

        frame = ctk.CTkFrame(self, corner_radius=20)
        frame.pack(expand=True, fill="both", padx=34, pady=34)

        title = ctk.CTkLabel(frame, text=reshape_text("🔮 نتیجه تست شما"), font=self.font_main)
        title.pack(pady=28)

        result_label = ctk.CTkLabel(
            frame, text=reshape_text(result), wraplength=640, justify="center",
            font=self.font_sub
        )
        result_label.pack(pady=22)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=28)

        again_btn = ctk.CTkButton(btn_frame, text=reshape_text("🔁 انجام دوباره تست"), width=220, height=48,
                                  font=self.font_sub, command=self.create_welcome_screen)
        again_btn.grid(row=0, column=0, padx=18)

        exit_btn = ctk.CTkButton(btn_frame, text=reshape_text("🚪 خروج"), width=220, height=48,
                                 font=self.font_sub, command=self.quit)
        exit_btn.grid(row=0, column=1, padx=18)

if __name__ == "__main__":
    app = PersonalityApp()
    app.mainloop()
