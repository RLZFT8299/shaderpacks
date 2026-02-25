import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys

class PyPackagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 自动打包工具")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.create_widgets()
        self.process = None

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 选择 Python 文件
        ttk.Label(main_frame, text="Python 脚本:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.py_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.py_path_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="浏览...", command=self.browse_py).grid(row=0, column=2)

        # 选项：单文件
        self.onefile_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="生成单个 exe 文件 (--onefile)",
                        variable=self.onefile_var).grid(row=1, column=1, sticky=tk.W, pady=5)

        # 选项：无控制台
        self.windowed_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="隐藏控制台 (--windowed，适用于 GUI 程序)",
                        variable=self.windowed_var).grid(row=2, column=1, sticky=tk.W, pady=5)

        # 图标文件
        ttk.Label(main_frame, text="图标文件 (可选 .ico):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.icon_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.icon_path_var, width=50).grid(row=3, column=1, padx=5)
        ttk.Button(main_frame, text="浏览...", command=self.browse_icon).grid(row=3, column=2)

        # 额外参数
        ttk.Label(main_frame, text="额外参数 (可选):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.extra_args_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.extra_args_var, width=50).grid(row=4, column=1, padx=5)

        # 输出文件夹标签（只读）
        ttk.Label(main_frame, text="输出位置:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir_var, state='readonly', width=50).grid(row=5, column=1, padx=5)
        ttk.Button(main_frame, text="打开文件夹", command=self.open_output_dir).grid(row=5, column=2)

        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=1, pady=10)
        ttk.Button(btn_frame, text="开始打包", command=self.start_pack).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="停止打包", command=self.stop_pack).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空输出", command=self.clear_output).pack(side=tk.LEFT, padx=5)

        # 输出显示
        ttk.Label(main_frame, text="打包输出:").grid(row=7, column=0, sticky=tk.NW, pady=5)
        self.output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=15)
        self.output_text.grid(row=7, column=1, columnspan=2, pady=5)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        main_frame.columnconfigure(1, weight=1)

    def browse_py(self):
        filename = filedialog.askopenfilename(
            title="选择 Python 脚本",
            filetypes=[("Python 文件", "*.py"), ("所有文件", "*.*")]
        )
        if filename:
            self.py_path_var.set(filename)
            # 自动设置输出文件夹为脚本所在目录下的 dist
            script_dir = os.path.dirname(filename)
            self.output_dir_var.set(os.path.join(script_dir, "dist"))

    def browse_icon(self):
        filename = filedialog.askopenfilename(
            title="选择图标文件",
            filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")]
        )
        if filename:
            self.icon_path_var.set(filename)

    def open_output_dir(self):
        output_dir = self.output_dir_var.get()
        if output_dir and os.path.exists(output_dir):
            os.startfile(output_dir) if sys.platform == 'win32' else subprocess.run(['open', output_dir])
        else:
            messagebox.showinfo("提示", "输出文件夹不存在或尚未生成")

    def start_pack(self):
        py_file = self.py_path_var.get().strip()
        if not py_file:
            messagebox.showerror("错误", "请选择 Python 脚本")
            return
        if not os.path.exists(py_file):
            messagebox.showerror("错误", "Python 文件不存在")
            return

        # 构建命令
        cmd = ["pyinstaller"]
        if self.onefile_var.get():
            cmd.append("--onefile")
        if self.windowed_var.get():
            cmd.append("--windowed")
        icon_path = self.icon_path_var.get().strip()
        if icon_path:
            if os.path.exists(icon_path):
                cmd.extend(["--icon", icon_path])
            else:
                messagebox.showerror("错误", "图标文件不存在")
                return
        extra = self.extra_args_var.get().strip()
        if extra:
            # 简单分割，按空格分割参数（不够严谨，但满足多数情况）
            cmd.extend(extra.split())
        cmd.append(py_file)

        # 切换到脚本所在目录执行，避免路径问题
        work_dir = os.path.dirname(py_file)

        self.status_var.set("正在打包...")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"执行命令: {' '.join(cmd)}\n\n")

        # 在子线程中运行打包，避免阻塞 UI
        def run():
            try:
                self.process = subprocess.Popen(
                    cmd,
                    cwd=work_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                for line in self.process.stdout:
                    self.output_text.insert(tk.END, line)
                    self.output_text.see(tk.END)
                    self.root.update_idletasks()
                self.process.wait()
                if self.process.returncode == 0:
                    self.status_var.set("打包完成")
                    # 刷新输出文件夹路径
                    self.output_dir_var.set(os.path.join(work_dir, "dist"))
                    messagebox.showinfo("成功", "打包完成！")
                else:
                    self.status_var.set("打包失败")
            except Exception as e:
                self.output_text.insert(tk.END, f"\n错误: {e}\n")
                self.status_var.set("打包异常")
            finally:
                self.process = None

        threading.Thread(target=run, daemon=True).start()

    def stop_pack(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.status_var.set("已终止打包")
        else:
            messagebox.showinfo("提示", "没有正在进行的打包任务")

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)

def main():
    root = tk.Tk()
    app = PyPackagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()