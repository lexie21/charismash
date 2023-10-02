from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app 
import os


db = SQLAlchemy(app)
migrate = Migrate(app,db)

# app.config['SECRET_KEY'] = 'thisissurpringsinglystimulating'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Candidates(db.Model):

    __tablename__ = 'candidates'

    id = db.Column(db.Integer,primary_key=True)
    img = db.Column(db.String)
    win = db.Column(db.Integer)
    loss = db.Column(db.Integer)
    score = db.Column(db.Float)
    opponents = db.relationship('Opponents',backref='candidates',lazy='dynamic')

    def __init__(self, img,score,win,loss):
        self.score = score
        self.img = img
        self.win = win
        self.loss = loss
        
        
   
    def __repr__(self):
        return f"Candidate {self.id}: score = {self.score}, win = {self.win}, loss = {self.loss}"

    def report_opponents(self):
        for opp in self.opponents:
            return opp.opponent_img
        # if self.opponents:
        #     return f"Candidate {self.img} has these opponents:"
        #     for oppo in self.opponents:
        #         print(oppo.opponent_img)
        #     # return self.opponent_img
        #     # for oppo in self.opponent:
        #     #     print(self.opponent_img)
        # else:
        #     print('This candidate has no opponents so far.')
# self.img.split('.')[0].split('/')[-1]}

class Opponents(db.Model):
    __tablename__='opponent'

    id = db.Column(db.Integer, primary_key=True)
    opponent_img = db.Column(db.String, nullable=False)
    candidate_id = db.Column(db.Integer,db.ForeignKey('candidates.id'))

    def __init__(self, opponent_img, candidate_id):
        self.candidate_id = candidate_id
        self.opponent_img = opponent_img
    
    def __repr__(self):
        return f"Opponent {self.opponent_img} vs Candidate {self.candidate_id}"
    
# db.create_all() stays here
db.create_all()


