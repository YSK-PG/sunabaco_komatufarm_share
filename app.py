from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Flaskアプリの作成
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

# **📌 トップページ（index）**
@app.route('/')
def index():
    return redirect(url_for('order_page'))  # トップページを注文ページにリダイレクト

# **📌 管理者ページ（生産者用）**
@app.route('/admin')
def admin():
    return render_template('admin.html', vegetables=Vegetables.query.all())

# **📌 商品追加機能**
@app.route('/add', methods=['GET', 'POST'])
def add_vegetable():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        stock = request.form.get('stock')

        if not name or not price or not stock:
            flash('すべての必須項目を入力してください。', 'danger')
            return redirect(url_for('add_vegetable'))

        new_vegetable = Vegetables(
            name=name,
            price=int(price),
            description=description,
            stock=int(stock),
            producer_id=1  # 仮の生産者ID（適切に設定）
        )
        db.session.add(new_vegetable)
        db.session.commit()
        flash('商品が追加されました！', 'success')
        return redirect(url_for('admin'))

    return render_template('add_vegetable.html')

# **📌 商品編集機能**
@app.route('/edit/<int:vegetable_id>', methods=['GET', 'POST'])
def edit_vegetable(vegetable_id):
    vegetable = Vegetables.query.get(vegetable_id)

    if vegetable is None:
        flash("指定された野菜は存在しません。", "danger")
        return redirect(url_for('admin'))

    if request.method == 'POST':
        vegetable.name = request.form.get('name')
        vegetable.price = request.form.get('price')
        vegetable.description = request.form.get('description')
        vegetable.stock = request.form.get('stock')

        db.session.commit()
        flash('商品が更新されました！', 'success')
        return redirect(url_for('admin'))

    return render_template('edit_vegetable.html', vegetable=vegetable)

# **📌 商品削除機能**
@app.route('/delete/<int:vegetable_id>', methods=['POST'])
def delete_vegetable(vegetable_id):
    vegetable = Vegetables.query.get(vegetable_id)

    if vegetable is None:
        flash("指定された野菜は存在しません。", "danger")
        return redirect(url_for('admin'))

    db.session.delete(vegetable)
    db.session.commit()
    flash('商品が削除されました！', 'success')
    return redirect(url_for('admin'))

# **📌 注文ページ（社員用）**
@app.route('/order_page')
def order_page():
    return render_template('order_page.html', vegetables=Vegetables.query.all())

# **📌 注文機能**
@app.route('/order/<int:vegetable_id>', methods=['GET', 'POST'])
def order_vegetable(vegetable_id):
    vegetable = Vegetables.query.get(vegetable_id)

    if vegetable is None:
        flash("指定された野菜は存在しません。", "danger")
        return redirect(url_for('order_page'))

    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        quantity = request.form.get('quantity')

        if not employee_id or not name or not quantity:
            flash("すべての項目を入力してください。", "danger")
            return redirect(url_for('order_vegetable', vegetable_id=vegetable_id))

        quantity = int(quantity)

        if vegetable.stock < quantity:
            flash('在庫が不足しています。', 'danger')
            return redirect(url_for('order_vegetable', vegetable_id=vegetable_id))

        vegetable.stock -= quantity

        new_order = Orders(
            employee_id=employee_id,
            name=name,
            vegetable_id=vegetable_id,
            quantity=quantity,
            order_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.session.add(new_order)
        db.session.commit()
        flash('注文OK！', 'success')
        return redirect(url_for('order_history'))

    return render_template('order.html', vegetable=vegetable)

# **📌 注文履歴ページ**
@app.route('/orders')
def order_history():
    orders = db.session.query(
        Orders.id,
        Orders.employee_id,
        Orders.name,
        Vegetables.name.label("vegetable_name"),
        (Vegetables.price * Orders.quantity).label("total_price"),
        Orders.quantity,
        Orders.order_date
    ).join(Vegetables, Orders.vegetable_id == Vegetables.id).all()

    return render_template('orders.html', orders=orders)

# Flaskアプリの起動
if __name__ == '__main__':
    app.run(debug=True)
