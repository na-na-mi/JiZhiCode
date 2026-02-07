import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import os
import io
import threading

# 设置外观
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# 继承 TkinterDnD.DnDWrapper 让窗口支持拖拽
class ExamPhotoTool(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()

        # 初始化拖拽功能
        self.TkdndVersion = TkinterDnD._require(self)

        # 窗口设置
        self.title("考公/报名证件照一键通")
        self.geometry("600x580")
        self.resizable(False, False)

        # 预设数据
        self.PRESETS = {
            "自定义模式 (手动输入)": {"w": 0, "h": 0, "kb": 200},
            "国考/省考 (35x45mm)": {"w": 413, "h": 531, "kb": 100},
            "研究生报名 (学信网)": {"w": 480, "h": 640, "kb": 50},
            "教师资格证": {"w": 295, "h": 413, "kb": 190},
            "会计/二建/软考": {"w": 295, "h": 413, "kb": 50},
            "一寸 (25x35mm)": {"w": 295, "h": 413, "kb": 100},
            "二寸 (35x49mm)": {"w": 413, "h": 579, "kb": 200},
            "小二寸 (35x45mm)": {"w": 413, "h": 531, "kb": 200},
        }

        self.file_path = None
        self.setup_ui()

        # 注册全窗口拖拽
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event)

    def setup_ui(self):
        # Header
        self.frame_header = ctk.CTkFrame(self, fg_color="#1f6aa5", corner_radius=0)
        self.frame_header.pack(fill="x")
        ctk.CTkLabel(self.frame_header, text="📷 证件照一键过审助手", font=("Microsoft YaHei", 20, "bold"),
                     text_color="white").pack(pady=15)

        # 1. 预设与参数设置区
        self.frame_settings = ctk.CTkFrame(self)
        self.frame_settings.pack(pady=15, padx=20, fill="x")

        ctk.CTkLabel(self.frame_settings, text="第一步：设置参数", font=("Microsoft YaHei", 14, "bold")).pack(anchor="w",
                                                                                                             padx=10,
                                                                                                             pady=(10,
                                                                                                                   5))

        # 预设下拉框
        self.preset_var = ctk.StringVar(value="国考/省考 (35x45mm)")
        self.combo_preset = ctk.CTkComboBox(self.frame_settings, values=list(self.PRESETS.keys()),
                                            command=self.on_preset_change, width=300, state="readonly")
        self.combo_preset.pack(pady=5)

        # 参数输入框 (网格布局)
        self.grid_frame = ctk.CTkFrame(self.frame_settings, fg_color="transparent")
        self.grid_frame.pack(pady=10)

        # 宽度
        ctk.CTkLabel(self.grid_frame, text="宽度(px):").grid(row=0, column=0, padx=5)
        self.entry_w = ctk.CTkEntry(self.grid_frame, width=80)
        self.entry_w.grid(row=0, column=1, padx=5)

        # 高度
        ctk.CTkLabel(self.grid_frame, text="高度(px):").grid(row=0, column=2, padx=5)
        self.entry_h = ctk.CTkEntry(self.grid_frame, width=80)
        self.entry_h.grid(row=0, column=3, padx=5)

        # 大小限制
        ctk.CTkLabel(self.grid_frame, text="限制(KB):").grid(row=0, column=4, padx=5)
        self.entry_kb = ctk.CTkEntry(self.grid_frame, width=80, text_color="red")
        self.entry_kb.grid(row=0, column=5, padx=5)

        # 初始化参数状态
        self.on_preset_change("国考/省考 (35x45mm)")

        # 2. 文件操作区 (拖拽区)
        self.frame_op = ctk.CTkFrame(self)
        self.frame_op.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.frame_op, text="第二步：上传照片", font=("Microsoft YaHei", 14, "bold")).pack(anchor="w",
                                                                                                       padx=10,
                                                                                                       pady=(10, 5))

        # 这是一个巨大的按钮，也可以当做拖拽指示区
        self.btn_select = ctk.CTkButton(self.frame_op, text="📂 点击选择 / 或将照片拖入此处",
                                        command=self.select_image,
                                        height=100,
                                        fg_color="#333333",
                                        hover_color="#444444",
                                        font=("Microsoft YaHei", 16))
        self.btn_select.pack(pady=10, padx=20, fill="x")

        self.lbl_file_info = ctk.CTkLabel(self.frame_op, text="支持 JPG / PNG / 任意尺寸", text_color="gray")
        self.lbl_file_info.pack()

        # 3. 执行按钮
        self.btn_run = ctk.CTkButton(self, text="🚀 一键生成过审照",
                                     command=self.process_image,
                                     height=50,
                                     font=("Microsoft YaHei", 18, "bold"),
                                     fg_color="#28a745", hover_color="#218838",
                                     state="disabled")
        self.btn_run.pack(pady=20, padx=40, fill="x")

    def on_preset_change(self, choice):
        """当下拉菜单变化时，联动修改输入框"""
        data = self.PRESETS[choice]

        # 先清空
        self.entry_w.delete(0, "end")
        self.entry_h.delete(0, "end")
        self.entry_kb.delete(0, "end")

        # 填充新值
        self.entry_w.insert(0, str(data['w']))
        self.entry_h.insert(0, str(data['h']))
        self.entry_kb.insert(0, str(data['kb']))

        # 如果是自定义模式，允许编辑；否则锁定输入框
        if "自定义" in choice:
            self.entry_w.configure(state="normal")
            self.entry_h.configure(state="normal")
            self.entry_kb.configure(state="normal")
        else:
            self.entry_w.configure(state="disabled")
            self.entry_h.configure(state="disabled")
            self.entry_kb.configure(state="disabled")

    def drop_event(self, event):
        """处理拖拽事件"""
        file_path = event.data
        # Windows 拖拽路径包含大括号的处理 {C:/Path/To/File.jpg}
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]

        self.load_file(file_path)

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("图片文件", "*.jpg;*.jpeg;*.png")])
        if path:
            self.load_file(path)

    def load_file(self, path):
        if not os.path.isfile(path): return

        # 简单检查扩展名
        valid_ext = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
        if not any(path.lower().endswith(ext) for ext in valid_ext):
            messagebox.showerror("错误", "不支持的文件格式")
            return

        self.file_path = path
        size_kb = os.path.getsize(path) / 1024
        try:
            img = Image.open(path)
            self.lbl_file_info.configure(
                text=f"已加载: {os.path.basename(path)} | {int(size_kb)}KB | {img.size[0]}x{img.size[1]}")
            self.btn_run.configure(state="normal")
            self.btn_select.configure(text="✅ 照片已就绪 (可拖入新图替换)", fg_color="#1f6aa5")
        except:
            messagebox.showerror("错误", "无法读取该图片")

    def process_image(self):
        if not self.file_path: return

        # 获取参数 (从输入框获取，这样无论是预设还是自定义都兼容)
        try:
            target_w = int(self.entry_w.get())
            target_h = int(self.entry_h.get())
            target_kb = int(self.entry_kb.get())
        except ValueError:
            messagebox.showerror("错误", "参数必须是整数！")
            return

        self.btn_run.configure(text="⏳ 处理中...", state="disabled")
        self.update()

        # 开个线程防止界面卡死
        threading.Thread(target=self._run_compression_thread, args=(target_w, target_h, target_kb)).start()

    def _run_compression_thread(self, target_w, target_h, target_kb):
        try:
            img = Image.open(self.file_path)

            # 1. 转 RGB
            if img.mode != "RGB":
                img = img.convert("RGB")

            # 2. 修改分辨率 (如果设置了)
            if target_w > 0 and target_h > 0:
                img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # 3. 压缩算法
            safe_target_kb = target_kb * 0.95
            target_bytes = safe_target_kb * 1024
            result_bytes = None

            min_q, max_q = 10, 95

            for _ in range(8):
                mid_q = (min_q + max_q) // 2
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=mid_q, dpi=(300, 300))
                size = buffer.tell()

                if size <= target_bytes:
                    result_bytes = buffer.getvalue()
                    min_q = mid_q + 1
                else:
                    max_q = mid_q - 1

            if result_bytes is None:
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=10, dpi=(300, 300))
                result_bytes = buffer.getvalue()

            # 4. 保存对话框 (要在主线程调用)
            self.after(0, lambda: self._save_file(result_bytes))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("失败", str(e)))
            self.after(0, lambda: self.btn_run.configure(text="🚀 一键生成过审照", state="normal"))

    def _save_file(self, data):
        # 恢复按钮
        self.btn_run.configure(text="🚀 一键生成过审照", state="normal")

        save_name = f"过审_{os.path.basename(self.file_path).split('.')[0]}.jpg"
        save_path = filedialog.asksaveasfilename(initialfile=save_name, filetypes=[("JPG", "*.jpg")])

        if save_path:
            with open(save_path, "wb") as f:
                f.write(data)
            final_kb = len(data) / 1024
            messagebox.showinfo("成功", f"✅ 搞定！\n最终大小：{final_kb:.2f} KB")


if __name__ == "__main__":
    app = ExamPhotoTool()
    app.mainloop()