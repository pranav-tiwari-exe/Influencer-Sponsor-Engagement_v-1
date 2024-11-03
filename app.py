from flask import Flask
import os
from models import *
from flask_sqlalchemy import SQLAlchemy


def createapp():
    app=Flask(__name__)
    app.config["SECRET_KEY"]='secret_key'
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.sqlite'

    db.init_app(app)

    UPLOAD_FOLDER = './static/Uploads/influencer_profiles'

    if not os.path.exists(UPLOAD_FOLDER):
        print("Directory does not exist, creating now.")
        os.makedirs(UPLOAD_FOLDER)      

    else:
        print("Directory already exists.")
    

    from controller import controller as con
    app.register_blueprint(con)
    
    return app


if __name__=='__main__':
    app=createapp() 
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)




