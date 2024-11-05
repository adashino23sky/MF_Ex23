import firebase_admin
from firebase_admin import credentials, db
 
# Firebaseの初期化
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-database-url.firebaseio.com'
})
 
# データベースへの参照を取得
ref = db.reference('/')
 
# データの読み取り
print(ref.get())
