import tkinter as tk
from tkinter import filedialog, messagebox
from svg import svg2csv
from plot import plot_csv
import os

WIDTH = 350
HEIGHT = 150
PADDING = 20
COLUMN_HEIGHT = 30

center_x = int(WIDTH / 2)


def file_select():
    filetype = [("SVG", "*.svg")]
    file_path = filedialog.askopenfilename(filetypes=filetype)
    # fileBox.delete(0, tk.END)
    # fileBox.insert(tk.END, file_path)

    return file_path


def run_convert():
    file_path = file_select()
    if not file_path:
        return

    power = float(powerBox.get())
    speed = int(speedBox.get())
    svg2csv(file_path, power, speed)

    if isPreview.get():
        csv_path = os.path.splitext(file_path)[0] + ".csv"
        plot_csv(csv_path, color="gradation")

    messagebox.showinfo("完了", "CSV変換が完了しました！")


root = tk.Tk()
root.geometry(f"{WIDTH}x{HEIGHT}")
root.title("SVG converter")

# レーザーパワーのラベル
powerLabel = tk.Label(text="レーザーパワーを入力 0.01-1.22 (W)")
powerLabel.place(x=PADDING, y=PADDING)

# レーザーパワーの入力ボックス
powerBox = tk.Entry(width=4)
powerBox.insert(tk.END, "0.5")
powerBox.place(x=280, y=PADDING)

# ステージの速度のラベル
speedLabel = tk.Label(text="ステージの速度を入力 1-5000 (μm/s)")
speedLabel.place(x=PADDING, y=PADDING + COLUMN_HEIGHT)

# ステージの速度の入力ボックス
speedBox = tk.Entry(width=4)
speedBox.insert(tk.END, "3000")
speedBox.place(x=280, y=PADDING + COLUMN_HEIGHT)
isPreview = tk.BooleanVar()

# プレビューのチェックボックス
isPreview.set(True)
isPreviewCheckbox = tk.Checkbutton(text="プレビューを表示", variable=isPreview)
isPreviewCheckbox.place(x=PADDING, y=PADDING + COLUMN_HEIGHT * 2)

# fileBox = tk.Entry(width=30)
# fileBox.place(x=PADDING, y=PADDING + COLUMN_HEIGHT * 3)

# fileButton = tk.Button(text="ファイル参照", command=file_select)
# fileButton.place(x=300, y=PADDING + COLUMN_HEIGHT * 3)

runButton = tk.Button(text="CSV変換", command=run_convert)
runButton.pack(side=tk.BOTTOM)

root.mainloop()
