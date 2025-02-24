import sqlite3

# データベースに接続（なければ作成される）
conn = sqlite3.connect('vegetable_app2.db')
cursor = conn.cursor()

# ORDERS テーブルを作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS ORDERS (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    employee_id TEXT NOT NULL, 
    name TEXT NOT NULL, 
    vegetable_id INTEGER NOT NULL, 
    quantity INTEGER NOT NULL, 
    order_date TEXT NOT NULL, 
    FOREIGN KEY (vegetable_id) REFERENCES VEGETABLES(id) ON DELETE CASCADE
);
''')

# 変更を保存
conn.commit()
conn.close()

print("✅ データベースの更新が完了しました！ ORDERSテーブルを作成しました！")
