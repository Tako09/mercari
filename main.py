# main program
from tkinter.constants import TRUE
from tkinter import messagebox as mb
from gui import GUI
import mercari as mer
import pandas as pd
import os
import numpy as np

uf = GUI('MERCARI DISCOUNT')
already_gained = 0
csv = 'C:\python\mercari\data\selling_item.csv'

def first_time_login():
    global uf
    if already_gained < 1 and not os.path.exists(csv):
        mb.showwarning('注意','ブラウザは自分で閉じてください\nアプリは自動的におちます。')
        mer.login_mercari_first_time()
        uf.destroy(10000)
    else:
        mb.showinfo('不要です','登録済です。')
        if mb.askokcancel("開く？", "商品情報を記録したファイルを開くますか？"):
            mer.open_excel()

def gain_info():
    global already_gained
    if already_gained < 1 and not os.path.exists(csv):
        mb.showinfo('安心して','ブラウザは自動的に閉じられます')
        mer.get_item_info()
        mb.showinfo('DONE','完了しました')
        already_gained += 1
    else:
        mb.showinfo('不要です','情報は最新の状態です。')

    if mb.askokcancel("開く？", "商品情報を記録したファイルを開くますか？"):
            mer.open_excel()

def update_item():
    global already_gained
    if already_gained < 1:
        if os.path.exists(csv):
            mb.showinfo('安心して','ブラウザは自動的に閉じられます')
            mer.execute_update()
            mb.showinfo('DONE','完了しました')
            already_gained += 1
            if mb.askokcancel("開く？", "商品情報を記録したファイルを開くますか？"):
                mer.open_excel()
        else:
            mb.showinfo('無理です','更新するためのファイルがありません。')
    else:
        mb.showinfo('不要です','情報は最新の状態です。')
        if mb.askokcancel("開く？", "商品情報を記録したファイルを開くますか？"):
            mer.open_excel()


def discount_item():
    global already_gained
    if already_gained >= 0:
        mb.showinfo('安心して','ブラウザは自動的に閉じられます')
        mer.execute_discount()
        mb.showinfo('DONE','完了しました！')
        if mb.askokcancel("開く？", "商品情報を記録したファイルを開くますか？"):
            mer.open_excel()
    else:
        mb.showinfo('注意','商品情報を最新の状態にしてください！')

# frame1 = uf.frame()
frame = uf.create_canvas()
uf.label(frame, text='初回時の操作:', side='left', grid=True, column=0, row=1, pady=0)
uf.button(frame, side='left', command=first_time_login, text='初回ログイン', row=1, column=1, pady=25, padx=20, grid=TRUE)
uf.button(frame, side='left', command=gain_info, text='初回商品情報の取得', row=1, column=3, pady=25, padx=20, grid=TRUE)
uf.label(frame, text='2回目以降の操作:', side='left', grid=True, column=0, row=3, pady=0)
uf.button(frame, side='left', command=update_item, text='商品情報の更新', row=3, column=1, pady=0, padx=20, grid=TRUE)
uf.button(frame, side='left', command=discount_item, text='商品の値下げ', row=3, column=3, pady=0, padx=20, grid=TRUE)
uf.end()

# 自動実行の手引き
# 初期設定済が前提条件
# 更新＆値下げ用のpyファイルを作る(exeしたほうが設定楽かも)
# 毎日起動させる
# 更新はログイン時強制的に行う、ロジックに従い値下げ必要なものがあるときメッセージをだす
# 値下げをしたいと出たとき値下げをおこなう
# 失敗しているか見たいから、バックアップをとるようにする(既存ファイルを退避)
# 完了と同時にエクセルを開くようにしておく
