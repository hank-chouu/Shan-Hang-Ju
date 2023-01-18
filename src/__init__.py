from flask import Flask
from flask_login import LoginManager
import os

from customer.routes import customer
from admin.routes import admin


def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(16).hex()
    
    # login_manager = LoginManager()
    # login_manager.login_view = 'pages.login'
    # login_manager.login_message = '請登入以進行更多操作'
    # login_manager.init_app(app)
      
    
    # @login_manager.user_loader  
    # def user_loader(uid):

    #     user = User()  
    #     user.id = uid  
    #     return user

    app.register_blueprint(customer, url_prefix = '/')

    return app