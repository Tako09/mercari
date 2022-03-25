# mercariのスクレイピングをするプログラム
# ユーザページから商品名と商品出品日の取得をする

# ライブラリのインストール
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager # selenium chromeを最新版に合わるためのライブラリ
# from chromedriver_py import binary_path
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup as bs4
import pandas as pd
import time
import os
import traceback
import pandas as pd
from tkinter import messagebox as mb
import re
import datetime
import numpy as np

# フルパスにしておかないとexe化した後にエラーになる
# グローバル変数の定義
URL = r'https://jp.mercari.com/mypage/listings' # ここは変更必要
# 'https://jp.mercari.com/mypage/listings'
USERDATA_DIR = r'D:\python\mercari\UserData'  # カレントディレクトリの直下に作る場合 - フルパスじゃないとエラーになる
df = pd.DataFrame() # 後でほかのファイルに渡せるようにするために変数を定義しておく
old_df = pd.DataFrame() # 後でほかのファイルに渡せるようにするために変数を定義しておく
data = './data'
df_path = './data/selling_item.xlsx'
error_log_path = './error_log'
err_flg = False
backup_path = './backup'

## ドライバとログイン情報の設定関数
def get_driver(page_load_strategy='eager'):
    # driverの設定関数 - 各処理時に毎回ドライバを起動しなおす

    if os.path.exists(USERDATA_DIR):
        try:
            # ドライバのオプション
            options = webdriver.chrome.options.Options()
            options.add_argument('--user-data-dir=' + USERDATA_DIR) # どこにログインパスを格納するか決める
            options.page_load_strategy = page_load_strategy # 処理速度を左右するオプション
            options.add_argument('--disable-extensions')
            # options.add_argument('--disable-gpu')

            # google chromeを起動
            # chrome_service = service.Service(executable_path)
            driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()), # 最新のchromeを使う
                    options=options
                )
            driver.implicitly_wait(5) # errorが起きた場合に10秒後自動的に閉じるように設定
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located) # ページ上のすべての要素が読み込まれるまで待機（15秒でタイムアウト判定）
        except:        
            mb.showwarning('警告','driverの準備ができませんでした\n')
            return 0 
        return driver
    else:
        mb.showwarning('ログイン情報がありません','ログイン情報を取得させる必要があります -自動的にログインページに遷移します。')
        return login_mercari_first_time()
    
def make_dir():
    os.makedirs(USERDATA_DIR, exist_ok=True) # ログイン情報格納先
    os.makedirs(data, exist_ok=True) # 商品データ格納先
    os.makedirs(error_log_path, exist_ok=True) # エラーログ格納先
    os.makedirs(backup_path, exist_ok=True) # バックアップ格納先

def login_mercari_first_time():
    # ログイン情報の保持用操作 - 初期設定時のみ使用
    
    make_dir()
    driver = get_driver(page_load_strategy='normal')
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located) # ページ上のすべての要素が読み込まれるまで待機（15秒でタイムアウト判定）
    driver.get('https://jp.mercari.com/mypage') # メルカリのログインページへ -> 初回利用時はログイン情報を記録させるのみ
    time.sleep(300)

    return driver

## スクレイピング関数
def login_mercari(driver, url):
    # item_urlの取得用関数
    
    try:
        driver.get(url)
        time.sleep(2) # 5秒後に自動的に閉じる - 変更の必要あり
        # 「もっと見る」ボタンがあればクリック
        for i in range(100):
            try:
                click_flg = button_click(driver, 'もっと見る')
                time.sleep(3)
                if not click_flg:
                    break
            except:
                break
    except:        
        mb.showwarning('警告','EXCEPTION\n' + traceback.format_exc()
        + '\n\n' + url)
        print(url)
    
    page_source = driver.page_source
    driver.quit()
    return page_source

def login_mercari_2(driver, item_urls):
    # 詳細情報取得関数

    srcs = []
    i = 0
    for url in item_urls:
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located) # ページ上のすべての要素が読み込まれるまで待機（15秒でタイムアウト判定）
            # if i == 10: # テスト用
            #    break
            # driver.get(url)
            driver.execute_script("window.open()") # 新しいタブを開く
            driver.switch_to.window(driver.window_handles[1]) # 新しいタブに切り替える
            driver.get(url)
            time.sleep(2) # 5秒後に自動的に閉じる - 変更の必要あり
            srcs.append(driver.page_source)
            driver.close()
            driver.switch_to.window(driver.window_handles[0]) # 切り替えておかないとエラーになる
            # i += 1
        except:        
            mb.showwarning('警告','EXCEPTION\n' + traceback.format_exc()
            + '\n\n' + url)
    
    driver.quit()
    return srcs

def new_items_login_mercari(driver, item_urls, length):
    # update時に新しく情報を取得する必要があるものだけを対象にする

    srcs = []
    i = 0
    for url in item_urls:
        try:
            if i >= length:
                driver.execute_script("window.open()") # 新しいタブを開く
                driver.switch_to.window(driver.window_handles[1]) # 新しいタブに切り替える
                driver.get(url)
                time.sleep(5) # 3秒後に自動的に閉じる - 変更の必要あり
                srcs.append(driver.page_source)
                driver.close()
                driver.switch_to.window(driver.window_handles[0]) # 切り替えておかないとエラーになる
            i += 1
        except:        
            mb.showwarning('警告','EXCEPTION\n' + traceback.format_exc()
            + '\n\n' + url)
            print(url)
    
    driver.quit()
    return srcs

def get_item_urls(page_source):
    # 出品アイテムの詳細ページに行くURLを取得

    soup = bs4(page_source, features='lxml')
    item_urls = []

    try:
        # a tagをまず入手
        elems = soup.find_all('a')
        # 必要なリンクのみの取得のために定義
        p = re.compile(r'/item/')
        for e in elems:
            href = e.attrs['href']
            if p.match(href):
                item_urls.append('https://jp.mercari.com' + href)
        return item_urls
    
    except Exception as e:
 
        mb.showwarning('警告','正常に処理が行われませんでした。もう一度やり直してください\nエラー理由:\n' + traceback.format_exc())
 
        return None

def get_edit_urls(item_urls):
    # 商品の編集ページに行くURLを取得
    edit_urls = [url.replace('/item/', '/sell/edit/', 1) for url in item_urls]
    return edit_urls

def find_item_info(df, srcs, item_urls):
    # 商品名を見つけるメソッド
    global err_flg
    global error_log_path
    item_names = []
    item_prices = []
    item_open_days = []
    errors = []
    i = 0

    # scrayping
    for src in srcs:
        soup = bs4(src, features='lxml')

        try:
            # find item info space
            item = soup.find('div', id='item-info')

            # find name
            mer_heading = item.find("mer-heading")
            item_names.append(str(mer_heading.attrs['title-label']))

            # find price
            mer_price = item.find('mer-price')
            item_prices.append(int(mer_price.attrs['value']))

            # find open day
            mer_text = item.find_all('mer-text')
            p = re.compile(r'.*前$')
            tmp = []
            for text in mer_text:
                if p.search(text.text):
                    tmp.append(text.text)
            item_open_days.append(str(tmp[-1])) # 最後に入った値のみ挿入。
            i += 1

        except Exception as e:
            err_flg = True
            errors.append(item_urls[i])
            print(item_urls[i])
            df.drop(index=df.index[[i]])
            pass

    if err_flg:
        # エラー処理。処理できなかった商品URLをログに抽出
        print('処理できていない商品があります。エラーログを見て存在している商品か確認してください。\n\
        保存先: ' + error_log_path)
        df_error = pd.DataFrame(data=errors, columns=['error_item_urls'])
        # get_excel(df_error, name=name, path=error_log_path, csv_needed=False)
        df_error.to_excel('error_log/error_item_log.xlsx', index=False)
        err_flg = False
            
    return item_names,item_prices,item_open_days

def update_items():
    # 売れた商品は除外して、出品日数の再計算をする関数
    # 増えた商品分のみ商品詳細情報を取りに行くようにしたい
    global df_path
    global df 

    if os.path.exists(df_path):
        driver = get_driver()
        page_source = login_mercari(driver, URL)
        item_urls = get_item_urls(page_source)

        tmp_df = pd.read_excel(df_path)
        tmp_df2 = pd.DataFrame({'new_item_url':item_urls})
        
        # URL: tmp_dfあり、tmp_df2なし → 商品は売れてる → 削除
        # URL: tmp_dfなし、tmp_df2あり → 新しい商品 → 情報取得必要
        # URL: 全一致 → 更新不要 
        merge_df = tmp_df.merge(tmp_df2, how='outer', left_on='item_url', right_on='new_item_url') # 外部結合を実施。左：tmp_df, 右：tmp_df2
        update_needed_itemURLs = merge_df[merge_df['item_url'].isnull()]['new_item_url'].tolist() # 追加された商品。情報の取得必要
        merge_df.dropna(subset=['item_url'], inplace=True, axis=0) # 追加する商品。またconcatで追加するため邪魔になる。
        merge_df.dropna(subset=['new_item_url'], inplace=True, axis=0) # 売れた商品なので削除。
        merge_df.drop('new_item_url', inplace=True, axis=1) # 必要ないので削除

        if len(update_needed_itemURLs) > 0:
            # 増えた分があるときのみ実行
            
            # 追加商品の情報を取得
            srcs = login_mercari_2(get_driver(), update_needed_itemURLs)
            edit_urls = get_edit_urls(update_needed_itemURLs)
            tmp = pd.DataFrame()
            item_names,item_prices,item_open_days = find_item_info(tmp, srcs,update_needed_itemURLs)

            tmp = pd.DataFrame()
            tmp['item_url'] = update_needed_itemURLs # 出品情報
            tmp['edit_url'] = edit_urls # 出品編集ページ
            tmp['name'] = item_names # 商品名
            tmp['price'] = item_prices # 値段
            tmp['past_days'] = item_open_days # 出品日
            tmp['past_days'] = tmp['past_days'].replace('  ', ' ')
            tmp['last_updated'] = pd.Series() # 初期時は空にする。
            tmp['selling_date'] = pd.Series() # 初期時は空にする。
            tmp['no_discount'] = 0 # ダミー値 - エラーになる
            tmp['changed_price'] = 0
            tmp['selling_date'] = selling_date(tmp)
            tmp['selling_date'] = pd.to_datetime(tmp['selling_date'], format='%Y-%m-%d')
            print(tmp['selling_date'])
            tmp['selling_date_is_empty'] = tmp['selling_date'].isnull().astype(int) # selling_dateがあるかどうか
            change_data_type(tmp)

            return pd.concat([merge_df,tmp], join='inner')
        
        return merge_df # 増えた分がないときはこれを返す。
    return 0

def button_click(driver, button_text):
    buttons = driver.find_elements(By.TAG_NAME, "button")
    time.sleep(1) # 探しきれずスルーする時がある
    clicked = False
    for button in buttons:
        # 指定のテキスト文字が入ってるボタンをクリックする
        # print(button.text)
        if button.text == button_text:
            button.click()
            clicked = True
            break
    return clicked
            

def change_mercari_price(driver):
    # 一定の日にちが立った商品をまとめて値下げをする
    # mercariのwebサイト変更のため、一時的に無駄な動きをふやしている
    global df
    global old_df
    global err_flg
    global error_log_path
    errors = []
    description = []
    err_flg = False

    old_df = pd.read_excel(df_path) # バグ対処用

    time.sleep(1)
    for i,val in enumerate(df.values):
        try:
            if val[8]:
                print('メルカリの値段を変更')
                print(val[1])
                driver.execute_script("window.open()") # 新しいタブを開く
                driver.switch_to.window(driver.window_handles[1]) # 新しいタブに切り替える
                driver.get(val[1])
                time.sleep(3)
                WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located) # ページ上のすべての要素が読み込まれるまで待機（3秒でタイムアウト判定）
                ele1 = driver.find_element(By.NAME,"price")
                time.sleep(0.5)
                # ele2 = driver.find_element(By.XPATH, '//*[@id="main"]/form/div[2]/mer-button[1]/button') # 動くけど挙動がおかしい
                ele2 = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"][data-testid="edit-button"][data-location="sell_edit:sell_form:button:edit"]') # 動くけど挙動がおかしいけど、出品停止に対応できる
                time.sleep(0.5)
                ele3 = driver.find_element(By.CSS_SELECTOR, 'textarea[class="input-node"][name="description"]') # xpathより各編集画面の微細な変化に強いはず
                time.sleep(0.5)
                
                # 値段の変更
                ele1.send_keys(Keys.CONTROL + "a")
                ele1.send_keys(Keys.DELETE)
                ele1.send_keys(str(val[3]))
                
                #time.sleep(10000)
                
                ele2.click()
                # button_click(driver, '変更する') 同じく挙動がおかしい。ボタンは押せる変化に一番強い
                time.sleep(1)
                try: # 暫定的な処理 - 値段変更後にクリックすると説明欄に飛ぶ現象がある。
                    ele3.send_keys(Keys.ENTER)
                    ele3.send_keys(Keys.BACK_SPACE)
                    ele2.click()
                    time.sleep(1)
                except:
                    err_flg = True 
                    errors.append(val[1])
                    description.append('webサイト変更のためのバグなし')
                    pass
                
                try: # 暫定的な処理 - 変更ボタンクリック後警告メッセージが出る場合がある。
                    driver.find_element(By.XPATH,'/html/body/mer-modal/div[2]/mer-button[2]/button').click()
                    time.sleep(0.5)
                    # /html/body/mer-modal/div[2]/mer-button[2]/button
                    # '''type="button", data-location="sell_edit:sell_form:button:confirm"
                    # text=このまま変更を確定する'''
                except:
                    err_flg = True 
                    errors.append(val[1])
                    description.append('警告文の表示なし')
                    pass
                
                driver.close() # 現在開いてるタブを閉じる
                time.sleep(0.5)
                driver.switch_to.window(driver.window_handles[0]) # 切り替えておかないとエラーになる
        except: # errorが出てもうごくようにする。 
            err_flg = True 
            errors.append(val[1])
            description.append('値下げの失敗')
            df['no_discount'][i] = False # フラグを戻す
            df['price'][i] = old_df['price'][i] # 変更前の値段に戻す
            df['selling_date'][i] = old_df['selling_date'][i] # 変更前の値段に戻す
            print(
            'EXCEPTION\n' + traceback.format_exc()
            + '\n\n' +val[1])
            driver.close() # 現在開いてるタブを閉じる
            time.sleep(0.5)
            driver.switch_to.window(driver.window_handles[0]) # 切り替えておかないとエラーになる
            pass
    driver.quit()
    if err_flg:
        # エラー処理。処理できなかった商品URLをログに抽出
        print('処理が異常終了した商品があります。ログを確認してください。\n\
        保存先: ' + error_log_path)

        df_error = pd.DataFrame()
        df_error['errors'] = errors
        df_error['descriptions'] = description 
        df_error.to_excel('error_log/discount_failed_log.xlsx', index=False)
        err_flg = False
    df['changed_price'] = 0 # 値段の変更が完了後はすべてのフラグをfalseに変えておく

def apply_discount(All='Y'): # 変更必要
    # 期日過ぎているのを一括で値下げ
    global df
    global old_df
    All = All.upper()
    new_price = []
    changed = []
    selling_date = []

    # 選べるようにしたいならまたここを変える
    if All == 'Y':
        # 1週間たっているitemすべて値引き
        for i,val in enumerate(df.values):
            if val[7]:
                new_price.append(int(val[3]))
                changed.append(int(0))
                selling_date.append(val[6])
            else:
                if val[3] >= 2000: # 2000円以上→200円引き
                    val[3] = val[3] - int(200)
                elif 1000 <= val[3] < 2000: # 1000円以上2000円以下→100円引き
                    val[3] = val[3] - int(100)
                elif 1000 > val[3]: # その他10円引き
                    val[3] = val[3] - int(10)
                if val[3] <= 300: # 300円以下の時は値段を1500円に戻す
                    val[3] = 1500
                new_price.append(int(val[3]))
                changed.append(int(1))
                selling_date.append(datetime.date.today())
                print('値段変更')
                print(val[1])
                
    return new_price,changed,selling_date # 新しい値段、変更フラグ、販売日を返す

def discount_needed(df):
    # 値下げが必要かのフラグを付与する関数
    df['selling_date_is_empty'] = df['selling_date'].isnull().astype(int) # selling_dateがあるかどうか
    df['last_updated'] = pd.to_datetime(df['last_updated'], format='%Y-%m-%d')
    df['selling_date'] = pd.to_datetime(df['selling_date'], format='%Y-%m-%d')
    tmp = []
    try:
        for i,val in enumerate(df.values):
            if val[9]: # datetimeの出品日がない場合はスクレイピングで取得したものを使用する:
                if re.match('[1-4] 日前|[1-4]日前|.*秒前|.*分前|.*時間前|.*時前',str(val[4])):
                    tmp.append(int(1))
                else:
                    tmp.append(int(0))
            else:
                tmp.append(int(val[6] >= val[5] - datetime.timedelta(days=4)))
                # 修正必要
        return tmp
    except:
        mb.showwarning('警告',
        'EXCEPTION\n' + traceback.format_exc()
        + '\n\n' + str(val[1])
        )

def get_df():
    return df

def open_excel(path='data\selling_item.xlsx'):
    # excelを開く
    import subprocess
    subprocess.Popen(['start',path], shell=True)

def get_excel(df, name='selling_item', path='data', csv_needed=True):
    df.to_excel(path+'/'+name+'.xlsx', index=False)

def selling_date(df):
    # 5日以上たっているものは値下げされる前提なので特に付与しない
    tmp = []
    for i,val in enumerate(df.values):
        val[4] = str(val[4])
        try:
            p = re.compile(r'.*秒前|.*分前|.*時間前|.*時前')
            if p.match(val[4]):
                tmp.append(datetime.date.today())
            elif re.match('1日前', val[4]) or re.match('1 日前', val[4]):
                tmp.append(datetime.date.today() - datetime.timedelta(days=1))
            elif re.match('2日前', val[4]) or re.match('2 日前', val[4]):
                tmp.append(datetime.date.today() - datetime.timedelta(days=2))
            elif re.match('3日前',val[4]) or re.match('3 日前',val[4]):
                tmp.append(datetime.date.today() - datetime.timedelta(days=3))
            elif re.match('4日前',val[4]) or re.match('4 日前',val[4]):
                tmp.append(datetime.date.today() - datetime.timedelta(days=4))
            else:
                tmp.append(None)
        except:
            tmp.append(None)
    return tmp

def change_data_type(df):
    # 型を一定にするための関数
    df['item_url'] = df['item_url'].astype(str)
    df['edit_url'] = df['edit_url'].astype(str)
    df['name'] = df['name'].astype(str)
    df['price'] = df['price'].astype(int) # 値段
    df['past_days'] = df['past_days'].astype(str)
    df['last_updated'] = pd.to_datetime(df['last_updated'], format='%Y-%m-%d')
    df['selling_date'] = pd.to_datetime(df['selling_date'], format='%Y-%m-%d')
    df['no_discount'] = df['no_discount'].astype(int)
    df['changed_price'] = df['changed_price'].astype(int)
    df['selling_date_is_empty'] = df['selling_date_is_empty'].astype(int) # selling_dateがあるかどうか

def get_item_info():
    # item情報をとるための関数をすべてじっこうする
    # 初期実行時のみ使用
    global df
    global df_path
    make_dir()

    # 各itemのurlの取得
    print('各商品の詳細情報のurlを取得中！')
    driver = get_driver()
    page_source = login_mercari(driver, URL)
    item_urls = get_item_urls(page_source)
    edit_urls = get_edit_urls(item_urls)
    print('商品数: ', str(len(item_urls)))
    # return item_urls

    # 詳細情報の取得
    driver = get_driver()
    srcs = login_mercari_2(driver, item_urls)
    print('item info done')

    df['item_url'] = item_urls # 出品情報
    df['edit_url'] = edit_urls # 出品編集ページ

    # return srcs
    item_names, item_prices, item_open_days = find_item_info(df, srcs,item_urls)
    df['name'] = item_names # 商品名
    df['price'] = item_prices # 値段
    df['past_days'] = item_open_days # 出品日
    df['last_updated'] = datetime.date.today() # 更新日
    df['last_updated'] = pd.to_datetime(df['last_updated'], format='%Y-%m-%d')
    df['past_days'] = df['past_days'].replace('  ', ' ')
    df['selling_date'] = pd.Series() # 初期時は空にする。
    df['no_discount'] = pd.Series() # 初期時は空にする。
    df['changed_price'] = 0
    df['selling_date'] = selling_date(df)
    df['selling_date'] = pd.to_datetime(df['selling_date'], format='%Y-%m-%d')
    df['selling_date_is_empty'] = df['selling_date'].isnull().astype(int) # selling_dateがあるかどうか
    df['no_discount'] = discount_needed(df)
    
    change_data_type(df)
    
    get_excel(df)

def execute_discount():
    # 値下げを実行するための関数
    global df_path
    global df
    global old_df
    df = pd.read_excel(df_path) # でーたを読み込み
    old_df = pd.read_excel(df_path) # バグ対処用
    change_data_type(df)
    make_dir()

    new_price,changed,sell_date = apply_discount(All='Y')
    df['price'] = new_price
    df['changed_price'] = changed
    df['selling_date'] = sell_date
    df['selling_date'] = pd.to_datetime(df['selling_date'], format='%Y-%m-%d')
    df['selling_date_is_empty'] = df['selling_date'].isnull().astype(int) # selling_dateがあるかどうか
    df['no_discount'] = True
    
    change_mercari_price(get_driver())
    change_data_type(df)
    
    get_excel(df)
    get_excel(old_df, name='selling_item', path=backup_path, csv_needed=False)

def execute_update():
    # update時はこれを参照
    global df
    global old_df
    old_df = pd.read_excel(df_path) # バグ対処用
    # get_excel(old_df, name='backup_selling_item', path=backup_path)
    get_excel(old_df, name='selling_item', path=backup_path)
    df = df.iloc[0:0]
    df = update_items()
    
    # df['selling_date'] = pd.to_datetime(df['selling_date'], format='%Y-%m-%d')
    df['selling_date_is_empty'] = df['selling_date'].isnull().astype(int) # selling_dateがあるかどうか
    df['last_updated'] = datetime.date.today() # 更新日
    df['last_updated'] = pd.to_datetime(df['last_updated'], format='%Y-%m-%d')
    df['no_discount'] = discount_needed(df)
    
    change_data_type(df)
    make_dir()
    get_excel(df)
    
# login_mercari_first_time()