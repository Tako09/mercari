'''
    This is Class to create GUI
'''

import tkinter as tk
from tkinter import messagebox
import os
# https://teratail.com/questions/88956

class GUI:
    def __init__(self, title,):
        # Make base
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry('500x150')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def frame(self):
        # create frame
        return tk.Frame(self.root)

    def child_frame(self, frame):
        # create frame
        return tk.Frame(frame)
    
    def create_canvas(self):
        # スクロール可能なcanvasを生成
        self.canvas = tk.Canvas(self.root)
        # Scrollbarを生成してcanvas上に配置
        self.scrollbar = tk.Scrollbar(self.canvas) # scrollbarの設定
        self.scrollbar.pack(side='right', fill='y')
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        #スクロール範囲を設定
        self.canvas.config(scrollregion=(0, 0, 150, 300))
        self.canvas.pack(fill='both', expand=True)

        # framを載せる
        self.frame1 = tk.Frame(self.canvas, bd=5)
        self.canvas.create_window((0, 0), window=self.frame1, anchor=tk.NW)

        # マウスのホイールで画面移動できるようにする
        self.canvas.bind("<MouseWheel>", self.mouse_scroll) 

        return self.frame1
    
    def mouse_scroll(self, event):
        # マウスホイールの操作を検知した時にどう動くかを決める
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')

    def label(self, frame, text='text', side='TOP', grid=False, column=0, row=0, pady=1):
        # create a label
        lb = tk.Label(frame, text=text)
        if grid:
            self.grid(lb, column, row, pady=pady)
        else:
            self.pack(lb, side)

    def text(self, frame, height=1, width=140, side='TOP', fg='black', state='normal', grid=False, column=0, row=0, pady=1):
        # create text box
        tx = tk.Text(frame, height=height, width=width, fg=fg)
        tx.config(state=state)
        if grid:
            self.grid(tx, column, row, pady=pady)
        else:
            self.pack(tx, side)
        return tx

    def func():
        pass

    def button(self, frame, command=func, text='text', side='TOP', grid=False, column=0, row=0, pady=1, padx=1):
        # create button
        btn = tk.Button(frame, text=text, command=command)
        if grid:
            self.grid(btn, column, row, pady=pady, padx=padx)
        else:
            self.pack(btn, side=side)
        return btn

    def pack(self, smt, side='TOP'):
        # pack label, text box, button
        if side.upper() == 'TOP':
            smt.pack()
        elif side.upper() == 'LEFT':
            smt.pack(side=tk.LEFT, anchor=tk.CENTER)

    def grid(self, smt, column, row, pady=1, padx=1):
        smt.grid(column=column, row=row, sticky=tk.N+tk.S, pady=pady, padx=padx)

    def delete_frame(self, frame):
       frame.destroy()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def message(self, text):
        messagebox.showinfo('結果', text)

    def destroy(self, ms):
        self.root.after(ms, lambda: self.root.destroy())

    def end(self):
        self.root.mainloop()

    
