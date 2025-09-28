from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os

from storage import (
    list_users,
    add_user as storage_add_user,
    list_expenses,
    add_expense_record,
    compute_balances,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        paid_by = int(request.form['paid_by'])
        split_type = request.form['split_type']

        try:
            users = list_users()
            if not users:
                raise ValueError('No users found. Add users first.')

            all_users = users
            other_users = [u for u in all_users if u['id'] != paid_by]

            shares = []
            if split_type == 'EQUAL':
                participant_count = len(all_users)
                if participant_count == 0:
                    raise ValueError('No participants to split the expense.')
                share = amount / participant_count
                for u in all_users:
                    shares.append({'user_id': u['id'], 'amount': round(share, 2)})

            elif split_type == 'EXACT':
                total_others = 0.0
                for u in other_users:
                    key = f'exact_{u["id"]}'
                    val = request.form.get(key)
                    amt = float(val) if val and val.strip() != '' else 0.0
                    if amt < 0:
                        raise ValueError('Exact amounts cannot be negative.')
                    total_others += amt
                    if amt > 0:
                        shares.append({'user_id': u['id'], 'amount': round(amt, 2)})
                if total_others - amount > 1e-6:
                    raise ValueError('Sum of exact amounts exceeds total expense.')
                payer_share = round(amount - total_others, 2)
                if payer_share < -1e-6:
                    raise ValueError('Calculated payer share is negative. Check inputs.')
                shares.append({'user_id': paid_by, 'amount': payer_share})

            elif split_type == 'PERCENTAGE':
                total_percent = 0.0
                total_others = 0.0
                for u in other_users:
                    key = f'percent_{u["id"]}'
                    val = request.form.get(key)
                    pct = float(val) if val and val.strip() != '' else 0.0
                    if pct < 0:
                        raise ValueError('Percentages cannot be negative.')
                    total_percent += pct
                    share_amt = round(amount * (pct / 100.0), 2)
                    total_others += share_amt
                    if share_amt > 0:
                        shares.append({'user_id': u['id'], 'amount': share_amt})
                if abs(total_percent - 100.0) > 0.5 and total_percent > 100.0:
                    raise ValueError('Total percentage exceeds 100%.')
                payer_share = round(amount - total_others, 2)
                if payer_share < -1e-6:
                    raise ValueError('Calculated payer share is negative. Check percentages.')
                shares.append({'user_id': paid_by, 'amount': payer_share})
            else:
                raise ValueError('Unsupported split type.')

            add_expense_record(
                description=description,
                amount=round(amount, 2),
                paid_by=paid_by,
                split_type=split_type,
                shares=shares,
                date_iso=datetime.utcnow().isoformat()
            )
            flash('Expense added successfully!', 'success')
            return redirect(url_for('view_balances'))

        except Exception as e:
            flash(str(e), 'danger')
            users = list_users()
            return render_template('add_expense.html', users=users), 400
    
    users = list_users()
    return render_template('add_expense.html', users=users)

@app.route('/view_balances')
def view_balances():
    users = list_users()
    balances = compute_balances()
    # Convert to tuples of (user_dict, balance)
    user_map = {u['id']: u for u in users}
    user_balances = [(user_map[uid], bal) for uid, bal in balances.items()]
    return render_template('view_balances.html', user_balances=user_balances)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # In production, hash this password
        try:
            storage_add_user(name=name, email=email, password=password)
            flash('User added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(str(e), 'danger')
            return render_template('add_user.html'), 400
    
    return render_template('add_user.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
