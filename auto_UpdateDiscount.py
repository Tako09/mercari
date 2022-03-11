# このファイルは商品情報のアップデートと値下げを自動的に実行するための書き換えたソースコード
# これは手動実行用に使わないようにする
# 自動でできること
# 1. 商品情報を更新
# 2. 一定の期間が経っているものを値下げする

from tkinter import messagebox as mb
import mercari as mer
import os

path = 'data\selling_item.csv'

def update_discount():
    # 更新と値下げを実行する関数

    # 更新
    if os.path.exists(path):
        print('メルカリの出品情報の更新を行います。')
        mer.execute_update()
        df = mer.get_df()
        # if mb.askokcancel("開く？", "商品情報を記録したファイルを開くますか？"):
        #     mer.open_excel()
    else:
        print('商品情報が記録されたファイルがありません。')

    # 値下げ
    if '1' in str(df['no_discount'].unique()):
        num = dict(df['no_discount'].value_counts())[0]
        print("値下げ対象の商品が"+str(num)+"件あります。\n値下げを実行します")
        mer.execute_discount()
        print("プログラムを終了します。")
    else:
        mb.showinfo("値下げ", "値下げ対象の商品がありません。プログラムを終了します。")

update_discount()