from flask import Flask
from flask_login import LoginManager
import os




from src.customer.routes import customer
from src.admin.routes import admin
from src.extensions.models import User, db


def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(16).hex()

    ## login 
    
    login_manager = LoginManager()
    # login_manager.login_view = 'pages.login'
    # login_manager.login_message = '請登入以進行更多操作'
    login_manager.init_app(app)      
    
    @login_manager.user_loader  
    def user_loader(id):

        user = User()  
        user.id = id  
        return user

    ## database

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:I227j7lZsmd33wn86f8J@containers-us-west-179.railway.app:6784/railway"
    
    db.init_app(app)
    with app.app_context():
        db.create_all()

    ## blueprints   

    app.register_blueprint(customer, url_prefix = '/')
    app.register_blueprint(admin, url_prefix = '/admin')

    return app