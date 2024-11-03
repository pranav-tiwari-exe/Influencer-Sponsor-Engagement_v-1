from flask import Flask
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import date,datetime,timedelta


db=SQLAlchemy()


class Baseuser(db.Model):
    __abstract__=True
    
    id=db.Column(db.Integer,primary_key=True, autoincrement=True)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(128),nullable=False)


    def checkpassword(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password)

class Influencer(Baseuser):
    __tablename__='influencer'

    name=db.Column(db.String(50),nullable=False)
    social_platform=db.Column(db.String,nullable=False)
    socialMediaLink=db.Column(db.String(100),unique=True ,nullable=False)
    niche=db.Column(db.String(50),nullable=False)
    category=db.Column(db.String(50),nullable=False)
    profile=db.Column(db.String)
    flagged=db.Column(db.Boolean,default=False)
#=====relationships
    ad_requests=db.relationship('Ad_request',backref='influencer',lazy=True)

    def __init__(self,email,name,password,socialMediaLink,niche,category,platform):
        self.email=email
        self.password=password
        self.name=name
        self.socialMediaLink=socialMediaLink
        self.niche=niche
        self.category=category
        self.social_platform=platform
        self.flagged=False

class Sponsor(Baseuser):
    __tablename__='sponsor'

    name=db.Column(db.String(50))
    type=db.Column(db.String(20))
#=====relationships
    campaigns=db.relationship('Campaigns',backref='sponsor',lazy=True)

    def __init__(self,email,type,name,password):
        self.email=email
        self.type=type
        self.name=name
        self.password=password

class Admin(Baseuser):
    __tablename__='admin'

    def __init__(self,email,password):
        self.email=email
        self.password=password

class Campaigns(db.Model):
    __tablename__ = 'campaign'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.Enum('public', 'private'), default='private')
    goals = db.Column(db.String)
    status=db.Column(db.Enum('Active','Inactive','Completed'))
    flagged=db.Column(db.Boolean,default=False)
    niche=db.Column(db.String(50),nullable=False)
    
#=====foreign keys
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    
#=====relationships
    ad_requests = db.relationship('Ad_request', backref='campaign', lazy=True)

    def __init__(self, name, description, budget, visibility, goals, start_date, end_date,niche, sponsor_id):
        self.name = name
        self.description = description
        self.budget = budget
        self.visibility = visibility
        self.goals = goals
        self.start_date = start_date
        self.end_date = end_date
        self.sponsor_id = sponsor_id 
        self.flagged=False
        self.niche=niche
        today = datetime.today().date()
        if self.start_date <= today <= self.end_date:
            self.status = 'Active'
        else:
            self.status = 'Inactive'

class Ad_request(db.Model):
    __tablename__='ad_request'

    id=db.Column(db.Integer,primary_key=True,autoincrement=True)                                                                                 
    message=db.Column(db.String)
    requirements=db.Column(db.String)
    payment_amount=db.Column(db.Integer,nullable=False)
    status=db.Column(db.Enum('Pending','Accepted'),default='Pending')
    negotiation_party=db.Column(db.Enum('influencer','sponsor'))
    negotiation_message=db.Column(db.String)
    expected_amount=db.Column(db.Integer)
    progress=db.Column(db.Integer)
    
#=====foreign key
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'),nullable=False)

    def __init__(self,campaign_id,influencer_id,message,requirements,payment_amount):
        self.campaign_id=campaign_id
        self.influencer_id=influencer_id
        self.message=message
        self.requirements=requirements
        self.status="Pending"
        self.payment_amount=payment_amount
        self.negotiation_mesage=None
        self.progress=0

class OnlineSession(db.Model):
    __tablename__ = 'online_session'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type=db.Column(db.Enum('influencer','sponsor'))
    user_id = db.Column(db.Integer, nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime)

    def __init__(self, user_id,type):
        self.user_id = user_id
        self.type=type
    
    def set_logout_time(self):
        self.logout_time = datetime.utcnow()


