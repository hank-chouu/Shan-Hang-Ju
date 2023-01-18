from flask import Flask
from flask_login import LoginManager
import os

from src.customer.routes import customer
from src.admin.routes import admin
from src.extensions.models import User


def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(16).hex()
    
    login_manager = LoginManager()
    # login_manager.login_view = 'pages.login'
    # login_manager.login_message = '請登入以進行更多操作'
    login_manager.init_app(app)
      
    
    @login_manager.user_loader  
    def user_loader(id):

        user = User()  
        user.id = id  
        return user

    app.register_blueprint(customer, url_prefix = '/')
    app.register_blueprint(admin, url_prefix = '/admin')

    return app