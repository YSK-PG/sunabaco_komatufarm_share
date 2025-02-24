from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vegetable_app2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# データベースのモデル
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # '生産者' or '社員'

class Vegetables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, nullable=False)
    producer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    vegetable_id = db.Column(db.Integer, db.ForeignKey('vegetables.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.String(100), nullable=False)

# データベースの初期化
with app.app_context():
    db.create_all()

# 商品一覧ページ
@app.route('/')
def index():
    vegetables = Vegetables.query.all()
    
    if not vegetables:
        flash("商品データがありません！商品を追加してください。", "danger")
    
    return render_template('index.html', vegetables=vegetables)

# 商品追加ページ
@app.route('/add', methods=['GET', 'POST'])
def add_vegetable():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        stock = request.form['stock']
        producer_id = 1  # 仮の生産者ID

        new_vegetable = Vegetables(
            name=name, 
            price=price, 
            description=description, 
            stock=stock, 
            producer_id=producer_id
        )
        db.session.add(new_vegetable)
        db.session.commit()
        flash('商品が追加されました！', 'success')
        return redirect(url_for('index'))

    return render_template('add_vegetable.html')

# 商品を注文するページ
@app.route('/order/<int:vegetable_id>', methods=['GET', 'POST'])
def order_vegetable(vegetable_id):
    vegetable = Vegetables.query.get(vegetable_id)

    if vegetable is None:
        flash("指定された野菜は存在しません。", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        employee_id = request.form['employee_id']
        name = request.form['name']
        quantity = int(request.form['quantity'])

        # 在庫確認
        if vegetable.stock < quantity:
            flash('在庫が不足しています。', 'danger')
            return redirect(url_for('index'))

        # 在庫を減らす
        vegetable.stock -= quantity

        # 注文データを追加
        new_order = Orders(
            employee_id=employee_id,
            name=name,
            vegetable_id=vegetable_id,
            quantity=quantity,
            order_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.session.add(new_order)
        db.session.commit()
        flash('注文が完了しました！', 'success')
        return redirect(url_for('index'))

    return render_template('order.html', vegetable=vegetable)

# 注文履歴ページ
@app.route('/orders')
def order_history():
    orders = Orders.query.all()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
