
import os
import json

from tkinter import filedialog
import customtkinter as ctk
import CTkMessagebox

import pyarrow.parquet as pq
import pyarrow.orc as orc

HistoryPathConfigFile = "orc_parquet_file_viewer.json" 

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.title("ORC/Parquet 文件查看")
        self.geometry("600x200")

        # 加载历史文件路径
        self.history_file_paths = self.load_history()

        # 创建一个框架来容纳输入框和选择文件按钮
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=20, padx=20, fill="x", expand=True)

        # 创建一个组合框用于显示文件路径，并添加文字提示
        self.file_path_combobox = ctk.CTkComboBox(self.input_frame, values=self.history_file_paths[::-1], width=300)
        self.file_path_combobox.pack(side="left",  fill="x", expand=True)

        # 创建一个按钮用于打开文件浏览器
        self.select_file_button = ctk.CTkButton(self.input_frame, text="选择文件", command=self.select_file)
        self.select_file_button.pack(side="left", padx=(10, 0))

        # 创建一个按钮用于打开 ORC 文件
        self.open_orc_button = ctk.CTkButton(self, text="打开 ORC 文件", command=self.open_orc_file)
        self.open_orc_button.pack(pady=10, padx=20, side="left", fill="x", expand=True)

        # 创建一个按钮用于打开 Parquet 文件
        self.open_parquet_button = ctk.CTkButton(self, text="打开 Parquet 文件", command=self.open_parquet_file)
        self.open_parquet_button.pack(pady=10, padx=20, side="left", fill="x", expand=True)

        # 绑定窗口关闭事件以保存历史记录
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_file(self):
        # 打开文件浏览器并获取选择的文件路径
        file_path = filedialog.askopenfilename()
        if file_path:
            # 将文件路径显示在组合框中
            self.file_path_combobox.set(file_path)
            # 添加到历史记录中
            self.history_file_paths.append(file_path)
            self.file_path_combobox.configure(values=self.history_file_paths[::-1])

    def open_orc_file(self):
        file_path = self.file_path_combobox.get()
        error_message = "暂时不支持" #TODO: pyarrow 读取 orc 时区报错

        if error_message:
            CTkMessagebox.CTkMessagebox(title="错误", message=error_message, icon="cancel")

    def open_parquet_file(self):
        file_path = self.file_path_combobox.get()
        error_message = ""
        if file_path.endswith('.parquet'):
            try:
                table = pq.read_table(file_path)
                self.show_file_content(file_path, table.to_pandas().to_string())
            except Exception as e:
                error_message = f"打开 Parquet 文件时出错: {e}"
        else:
            error_message = "请选择一个有效的 Parquet 文件。"

        if error_message:
            CTkMessagebox.CTkMessagebox(title="错误", message=error_message, icon="cancel")

    def load_history(self):
        # 从 JSON 文件加载历史记录
        if os.path.exists(HistoryPathConfigFile):
            with open(HistoryPathConfigFile, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return ["/ 选择文件 / 输入文件路径"]
        return ["/ 选择文件 / 输入文件路径"]

    def show_file_content(self, file_path, content):
        # 创建一个新的 Toplevel 窗口
        top = ctk.CTkToplevel(self)
        top.title(f"文件内容 - {os.path.basename(file_path)}")
        top.geometry("800x600")

        # 创建一个 Textbox 用于显示文件内容
        textbox = ctk.CTkTextbox(top, width=780, height=580)
        textbox.pack(pady=20, padx=20, fill="both", expand=True)

        # 将文件内容插入到 Textbox 中
        textbox.insert("0.0", content)
        textbox.configure(state="disabled")  # 禁用编辑

    def save_history(self):
        # 将历史记录保存到 JSON 文件
        with open(HistoryPathConfigFile, "w", encoding="utf-8") as f:
            json.dump(self.history_file_paths, f, ensure_ascii=False, indent=4)

    def on_closing(self):
        # 保存历史记录并关闭窗口
        self.save_history()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()