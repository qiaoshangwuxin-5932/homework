from flask_login import current_user,login_required
from flask import  Flask,redirect,url_for,flash
app = Flask(__name__)

@app.route('/confirm/<token>')
@login_required  #修饰器 保护路由
def confirm(token): #确认用户账户
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your accout,Thacnks')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
