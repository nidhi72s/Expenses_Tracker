from flask import Flask, render_template, request, redirect, session, url_for
from models import db, User, Expense

app = Flask(__name__)
app.secret_key = "mysecret"

# database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db.init_app(app)

# create tables
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return redirect('/login')


# ----------- AUTH -----------

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = User(username=uname, password=pwd)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=uname, password=pwd).first()
        if user:
            session['user_id'] = user.id
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ----------- DASHBOARD -----------

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# ----------- EXPENSES -----------

@app.route('/expenses')
def expenses():
    if 'user_id' not in session:
        return redirect('/login')
    expenses = Expense.query.filter_by(user_id=session['user_id']).all()
    return render_template('expenses.html', expenses=expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    if 'user_id' in session:
        category = request.form['category']
        amount = request.form['amount']
        comment = request.form['comment']
        new_expense = Expense(category=category, amount=amount, comment=comment, user_id=session['user_id'])
        db.session.add(new_expense)
        db.session.commit()
    return redirect('/expenses')

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        expense.category = request.form['category']
        expense.amount = request.form['amount']
        expense.comment = request.form['comment']
        db.session.commit()
        return redirect('/expenses')

    expenses = Expense.query.filter_by(user_id=session['user_id']).order_by(Expense.created_at.desc()).all()
    return render_template('expenses.html', expenses=expenses, edit_mode=True,edit_id = id)

@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect('/expenses')

if __name__ == "__main__":
    app.run(debug=True)
