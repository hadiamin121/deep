import hashlib
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window

# تابع اصلی منطق شما، بدون تغییر
def parse_amx(amx_string):
    if amx_string.startswith("amx "):
        amx_string = amx_string[4:]
    splited = amx_string.split(":")
    base_string = (
        splited[0]
        + "A85D4ECE998948D0AA0B792A919985581049EF42C5524C87BCA0E9A"
        + splited[2]
    )
    target_md5 = splited[3]
    return base_string, target_md5

def brute_force(base_string, target_md5, progress_callback=None):
    """تابع brute-force با قابلیت به‌روزرسانی پیشرفت"""
    # بررسی NULL
    if target_md5 == hashlib.md5(base_string.encode('utf-8')).hexdigest():
        return "There is not pin: NULL", True

    for i in range(1000000):
        suffix = f"{i:06d}"
        full_string = base_string + suffix
        md5_hash = hashlib.md5(full_string.encode('utf-8')).hexdigest()
        if md5_hash == target_md5:
            result = f"Found!\nNumber: {suffix}\nFull string: {full_string}\nMD5: {md5_hash}"
            return result, True
        # هر 10000 بار یک بار به‌روزرسانی UI (برای عملکرد بهتر)
        if progress_callback and i % 10000 == 0:
            progress_callback(i)
    return "No match found from 000000 to 999999.", False

class BruteForceApp(App):
    def build(self):
        Window.size = (400, 600)  # اندازه پنجره (برای دسکتاپ)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        layout.add_widget(Label(text="Enter base string or AMX format:", size_hint_y=0.08))
        
        self.input_field = TextInput(
            hint_text="e.g., amx abc:def:xyz or plain base string",
            multiline=False,
            size_hint_y=0.15
        )
        layout.add_widget(self.input_field)

        self.start_btn = Button(text="Start Brute Force", size_hint_y=0.12)
        self.start_btn.bind(on_press=self.start_brute_force)
        layout.add_widget(self.start_btn)

        self.progress_label = Label(text="Ready", size_hint_y=0.1)
        layout.add_widget(self.progress_label)

        self.result_label = Label(
            text="Results will appear here",
            size_hint_y=0.55,
            halign='left',
            valign='top'
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        layout.add_widget(self.result_label)

        return layout

    def start_brute_force(self, instance):
        user_input = self.input_field.text.strip()
        if not user_input:
            self.result_label.text = "Please enter a string."
            return

        # تشخیص فرمت: آیا 4 بخش جدا شده با : دارد؟
        parts = user_input.split(":")
        if len(parts) == 4:
            try:
                base_string, target_md5 = parse_amx(user_input)
            except Exception as e:
                self.result_label.text = f"Parse error: {e}"
                return
        else:
            # فرض می‌کنیم کاربر فقط رشته پایه را وارد کرده و MD5 هدف را نمی‌داند
            # این حالت در اسکریپت اصلی شما ناقص بود (target_md5 نامشخص)
            self.result_label.text = "Please enter in AMX format (4 parts separated by ':') so the target MD5 is known."
            return

        self.start_btn.disabled = True
        self.progress_label.text = "Searching..."
        self.result_label.text = ""

        # تعریف callback برای به‌روزرسانی UI
        def update_progress(i):
            self.progress_label.text = f"Searching: {i:06d}"

        # اجرای brute-force در thread جداگانه تا UI هنگ نکند
        import threading
        def run():
            result, found = brute_force(base_string, target_md5, update_progress)
            def finish(dt):
                self.result_label.text = result
                self.progress_label.text = "Done" if found else "Finished (no match)"
                self.start_btn.disabled = False
            Clock.schedule_once(finish, 0)

        threading.Thread(target=run, daemon=True).start()

if __name__ == '__main__':
    BruteForceApp().run()
