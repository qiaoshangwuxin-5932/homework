# -*- coding: utf-8 -*-
from flask_wtf import Form

from flask import Flask,request,abort,session,redirect,jsonify,url_for
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
# from flask_cors import CORS
import pymysql

from flask_sqlalchemy import SQLAlchemy

pymysql.install_as_MySQLdb()

app = Flask(__name__)


@app.before_request     #钩子
def app_before_request():
    print("HTTP {} {}".format(request.method,request.url))

app.config['SQLALCMEY_DATABASE_URL'] = 'mysql://  :  @localhost/  ?charset=utf8'
app.config['SQLALCMEY_TRACK_MODIFCATIONS'] = True
db = SQLAlchemy(app)

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

class User(db.Model):  #建立User模型
    __tablename__ = ""          #数据库名字
    id = db.Column(db.Integer,primary_key=True,nullable=False)  #id
    email = db.Column(db.String(64),nullable=False) #用户email
    username = db.Column(db.String(64),nullable=False) #用户名字
    password = db.Column(db.String(20),nullable=False) #用户密码

#注册
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm() #把Reg模型赋给form变量
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username = form.username.data,
                    password = form.password.data)
        db.session.add(user) #提交注册的信息
        return jsonify({"you can now login"}) #返回注册成功

    #判断邮箱是否已被注册
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')
    #判断账户是否已被注册
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use ')
        # username = request.args.get("username")
        # email = request.args.get("email")
        # validate_username =User.query.filter_by(username=username).first_or_404()
        # validate_email =User.query.filter_by(email=email).first_or_404()
        # if validate_username:
        #     return jsonify({
        #         "message":"The username already in use"
        #     })
        # if avlidate_email:
        #     return jsonify({
        #         "message":"The email already registered"
        #     })










if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)