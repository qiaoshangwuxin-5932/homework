# -*- coding: utf-8 -*-
from flask_wtf import Form

from flask import Flask,request,redirect,jsonify,url_for,current_app,flash
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from flask_cors import CORS
import pymysql
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import current_user
pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.config['SQLALCMEY_DATABASE_URL'] = 'mysql://  :  @localhost/  ?charset=utf8'
app.config['SQLALCMEY_TRACK_MODIFCATIONS'] = True                 #链接数据库
db = SQLAlchemy(app)

@app.before_request     #钩子
def before_request():
    print("HTTP {} {}".format(request.method,request.url))  #符合 HTTP 的才可接受
    if current_user.is_autjenticated\
            and not current_user.confirmed:             #用户已被登录//用户不存在//双方都会被过滤
        return redirect(url_for('unconfirmed'))       #重新被调回到unconfirmed 路由上

@app.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return  redirect('unconfirmed.html')    #该页面为提示用户确认信息


##
#建立RegistrationForm模型
class RegistrationForm(Form): #该模型 来对 输入的 email，username，password进行校对正确的格式
    email = StringField('Email',validators=[Required(), Length(1,64), Email()])
    username = StringField('Username',validators=[
        Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                       'Username musta have only letters'
                                       'numbers,dots or underscores')])
    password = PasswordField('Password',validators=[
        Required(),EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm passwword', validators=[Required()])
    submit = SubmitField('Register')

##
#建立User模型
class User(db.Model):
    __tablename__ = "user"          #数据库名字
    id = db.Column(db.Integer,primary_key=True,nullable=False)  #id
    email = db.Column(db.String(64),nullable=False) #用户email
    username = db.Column(db.String(64),nullable=False) #用户名字
    password = db.Column(db.String(20),nullable=False) #用户密码
    confirmed = db.Column(db.Boolean,default=False)

    #生成令牌，有效期一个小时
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    #检验令牌
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True         #如果通过 confirm睡醒会被设置为True
##登录
@app.route('/login',methods=['GET','POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username and password:
        if not username:
            return jsonify({
                'message':'Your username have error'
            })
        elif not password:
            return jsonify({
                'message':'Your password have error'
            })
    else:
        return redirect(url_for('main.index'))

##修改密码
@app.route('/chg_pwd',methods=['PUT'])
def change_password():
    username = request.args.get('username')
    passwrod = request.args.get('password')
    hchg_password = request.args.get('password2')
    check_username = User.query.filter_by(username=username).first()
    if not check_username:
        flash('Your username have error')
    check_password = User.query.filter_by(passwrod=passwrod).first()
    if not check_password:
        flash('Your old password has error')
    else:
        user.password = hchg_password
        db.session.commit()
        flash('Your password have been changed succeedly')

 #注册
@app.route('/register',methods=['GET','POST'])
def register():
    # 判断邮箱是否已被注册
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    # 判断账户是否已被注册
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():  # 判断建立账户的符合格式的数据是否在数据库中有和他一样的
            raise ValidationError('Username already in use ')  # 如果拥有，则返回 “username 正在使用”
            # username = request.args.get("username")
            # email = request.args.get("email")                                             # 此方法
            # validate_username =User.query.filter_by(username=username).first_or_404()     # 为
            # validate_email =User.query.filter_by(email=email).first_or_404()              # 原来的
            # if validate_username:                                                         # 使用方法（也可以实现对重复username和password的判定）
            #     return jsonify({
            #         "message":"The username already in use"
            #     })
            # if avlidate_email:
            #     return jsonify({
            #         "message":"The email already registered"
            #     })
    form = RegistrationForm() #把Reg模型赋给form变量
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username = form.username.data,
                    password = form.password.data)
        db.session.add(user) #提交注册的信息
        db.session.commit()                  #信息提交，调用
        #return jsonify({"you can now login"})  # 返回注册成功
        token = user.generate_confirmation_token()
        send_email(User.email,'Confirm Your Account','Desktop/wuxin/confirm',user=user,token=token) #确认邮件的纯文本正文
        flash('A confirmation email has been sent to you by email')
        return redirect(url_for('main.index')) #跳转
    return redirect('Desktop/wuxin/ceshi.html',form=form)






if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)