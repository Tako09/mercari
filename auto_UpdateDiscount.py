# このファイルは商品情報のアップデートと値下げを自動的に実行するための書き換えたソースコード
# これは手動実行用に使わないようにする
# 自動でできること
# 1. 商品情報を更新
# 2. 一定の期間が経っているものを値下げする

from tkinter import messagebox as mb
import mercari as mer
import os
import time

path = mer.df_path

def update_discount():
    # 更新と値下げを実行する関数
    if os.path.exists(path):
        print('メルカリの出品情報の更新を行います。')
        mer.execute_update()
        df = mer.get_df()
    else:
        print('商品情報が記録されたファイルがありません。')

    if '0' in str(df['no_discount'].unique()):
        num = dict(df['no_discount'].value_counts())[0]
        print("値下げ対象の商品が"+str(num)+"件あります。\n値下げを実行します")
        mer.execute_discount()
        print("プログラムを終了します。")
    else:
        print("値下げ対象の商品がありません。プログラムを終了します。")
    
    time.sleep(10)
    mer.open_excel()

update_discount()