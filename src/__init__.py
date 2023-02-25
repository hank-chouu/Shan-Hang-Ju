from flask import Flask
from flask_login import LoginManager
import os
from dotenv import load_dotenv

from src.customer.routes import customer
from src.admin.routes import admin
from src.extensions.models import User, db
from src.extensions.email import mail
from src.extensions.logger import allLogger

def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(16).hex()

    # load .env
    load_dotenv()

    

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
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
    allLogger.info('Database initialized.')

    # email configs
    
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PROT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
    )

    mail.init_app(app)
    allLogger.info('Mail server initialized. ')

    ## blueprints   

    app.register_blueprint(customer, url_prefix = '/')
    app.register_blueprint(admin, url_prefix = '/admin')

    
    return app