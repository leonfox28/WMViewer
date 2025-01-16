import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk

class WMViewer:
    def __init__(self, root):
        self.version = "1.0.0"
        self.root = root
        self.root.title(f"WMViewer {self.version}")
        
        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="打开", command=self.load_wafer_map)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=root.quit)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)

        self.status_bar = tk.Label(self.main_frame, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.TOP, fill=tk.X, expand=tk.YES)

        self.spinbox_frame = tk.Frame(self.main_frame, height=50)
        self.spinbox_frame.pack(side=tk.TOP, fill=tk.X)

        self.draw_button = tk.Button(self.spinbox_frame, text="Refresh", command=self.display_wafer_map)
        self.draw_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.draw_button.config(state=tk.DISABLED)

        self.spinbox1_label = tk.Label(self.spinbox_frame, text="Map X")
        self.spinbox1_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.spinbox_map_x = tk.Spinbox(self.spinbox_frame, from_=0, to=10000, values=200, increment=1)
        self.spinbox_map_x.pack(side=tk.LEFT, padx=5, pady=5)

        self.spinbox2_label = tk.Label(self.spinbox_frame, text="Map Y")
        self.spinbox2_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.spinbox_map_y = tk.Spinbox(self.spinbox_frame, from_=0, to=10000, values=200, increment=1)
        self.spinbox_map_y.pack(side=tk.LEFT, padx=5, pady=5)

        self.spinbox3_label = tk.Label(self.spinbox_frame, text="DIE Width")
        self.spinbox3_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.spinbox_die_width = tk.Spinbox(self.spinbox_frame, from_=0, to=10000, values=10, increment=1)
        self.spinbox_die_width.pack(side=tk.LEFT, padx=5, pady=5)

        self.spinbox4_label = tk.Label(self.spinbox_frame, text="DIE Height")
        self.spinbox4_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.spinbox_die_height = tk.Spinbox(self.spinbox_frame, from_=0, to=10000, values=10, increment=1)
        self.spinbox_die_height.pack(side=tk.LEFT, padx=5, pady=5)

        self.color_frame = tk.Frame(self.main_frame)
        self.color_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.move)
        
        self.cv_img = None
        self.photo = None
        self.scale = 1.0
        self.data = []
        self.prefix = []
        self.bin_lines = []
        self.bin = []
        self.color_map = {}

        

    def load_wafer_map(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    self.data = []
                    self.prefix = []
                    self.bin_lines = []
                    lines = f.readlines()
                    for line in lines:
                        stripped_line = line.strip()
                        if stripped_line and stripped_line[0] == '.':
                            self.data.append(list(stripped_line))
                        elif stripped_line.startswith("Bin"):
                            self.bin_lines.append(stripped_line)
                        else:
                            self.prefix.append(stripped_line)
                    self.process_data()
            except FileNotFoundError:
                print("文件未找到")
            except Exception as e:
                print(f"读取文件出错: {e}")

    def process_data(self):
        if not self.data:
            print("Wafer map 数据为空")
            return
        
        for bin_line in self.bin_lines:
            bin_str = bin_line.split()[1]
            bin_str = bin_str.replace(":", "")
            bin_str = bin_str.replace(",", "")
            self.bin.append(bin_str)
        
        self.color_map = {}
        for i, bin_value in enumerate(self.bin):
            color = (int(np.random.choice(range(256))), int(np.random.choice(range(256))), int(np.random.choice(range(256))))
            self.color_map[bin_value] = color
        
        print(self.color_map)
        
        # self.display_prefix_text()
        self.display_color_map()
        self.display_wafer_map()
        self.update_status_bar()
        self.draw_button.config(state=tk.NORMAL)

    def display_prefix_text(self):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, '\n'.join(self.prefix))

    def display_color_map(self):
        for widget in self.color_frame.winfo_children():
            widget.destroy()
        
        for bin_value, color in self.color_map.items():
            color_label = tk.Label(self.color_frame, text=f"Bin {bin_value}", bg=self.bgr_to_hex(color))
            color_label.pack()

    def bgr_to_hex(self, bgr):
        return "#{:02x}{:02x}{:02x}".format(bgr[2], bgr[1], bgr[0])

    def update_status_bar(self):
        print(" | ".join(self.prefix))  # 添加调试信息
        self.status_bar.config(text=" | ".join(self.prefix))

    def display_wafer_map(self):
        try:
            self.draw_button.config(state=tk.DISABLED)

            map_x = int(self.spinbox_map_x.get())
            map_y = int(self.spinbox_map_y.get())
            die_width = int(self.spinbox_die_width.get())
            die_height = int(self.spinbox_die_height.get())
            print(f"Map X: {map_x}, Map Y: {map_y}, DIE Width: {die_width}, DIE Height: {die_height}")

            img_np = np.zeros((map_y * die_height, map_x * die_width, 3), dtype=np.uint8)
            img_np[:] = (255, 255, 255)

            for y, row in enumerate(self.data):
                if y >= map_y:
                    continue
                for x, value in enumerate(row):
                    if x >= map_x:
                        continue
                    elif value in self.color_map:
                        color = self.color_map[value]
                        cv2.rectangle(img_np, (x * die_width, y * die_height), ((x + 1) * die_width, (y + 1) * die_height), color, -1)
                        cv2.rectangle(img_np, (x * die_width, y * die_height), ((x + 1) * die_width, (y + 1) * die_height), (0, 0, 0), 1)

            self.cv_img = img_np
            img = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(img)

            self.canvas.config(width=img.width, height=img.height)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        except Exception as e:
            self.draw_button.config(state=tk.NORMAL)
            print(f"显示晶圆图出错: {e}")

    def zoom(self, event):
        if event.delta > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1

        new_width = int(self.cv_img.shape[1] * self.scale)
        new_height = int(self.cv_img.shape[0] * self.scale)

        resized_image = cv2.resize(self.cv_img, (new_width, new_height), interpolation=cv2.INTER_NEAREST)
        img = Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def start_move(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = WMViewer(root)
    root.mainloop()