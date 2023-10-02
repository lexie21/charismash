import os, random
from flask import Flask, session, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import GateKeeper

##### create db
###config db model
app = Flask(__name__)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

app.config['SECRET_KEY'] = 'thisissurpringsinglystimulating'

######################################################################################
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join(basedir,"data.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################################MODELS###########################################
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
        # for opp in self.opponents:
        #print(opp.opponent_img)
        return self.opponents


class Opponents(db.Model):
    __tablename__='opponent'

    id = db.Column(db.Integer, primary_key=True)
    opponent_img = db.Column(db.String, nullable=False)
    candidate_id = db.Column(db.Integer,db.ForeignKey('candidates.id'))

    def __init__(self, opponent_img, candidate_id):
        
        self.opponent_img = opponent_img
        self.candidate_id = candidate_id
    
    def __repr__(self):
        return f"Opponent {self.opponent_img} vs Candidate {self.candidate_id}"
    
# db.create_all() stays here
db.create_all()

# #################################################################################
candi_list = Candidates.query.all()
no_ovlap = list()
candi_imgs = []
for candi in candi_list:
    candi_img = candi.img
    candi_imgs.append(candi_img)


dbase_len = len(candi_list)
random_lst = list()
count = 0
answer = ''

####session to distinguish users############
@app.route('/',methods=['POST','GET'])
def gatekeeper():
    global count, answer
    form = GateKeeper()
   
    if form.validate_on_submit():
        prefix = str(random.randint(0,2000))
        answer = form.question.data
        answer = answer.lower()
        if answer == 'submit':
            session['user'] = answer + prefix
            count = 0
            return redirect(url_for('index'))
            
        else:
            count = count + 1
        #     flash('Guess again, presumably if you will. Hint: 6 letters.')
    return render_template('gatekeeper.html',form=form, count = count)



@app.route('/home')
def index():
    if 'user' in session:
        return render_template('index.html',candi_imgs=candi_imgs,candi_list=candi_list)
    else:
        return redirect(url_for('gatekeeper'))
###########add items to db#########

@app.route('/choosePics', methods=["POST"])
def choosePic():
    global no_ovlap,candi_imgs, candi_imgs2
    test = request.form['images']

    # if request.method == 'GET':
    #     no_ovlap = []

    rivals_list = test.split('+')

# #  ######Performance rating#############
# #  #Performance rating = (Total of opponents' ratings +- 400 x (Wins - Losses)/Games)   
    
    winner = rivals_list[0]

    winning_cand = Candidates.query.filter_by(img=winner).first()
    winning_cand.win = winning_cand.win + 1
    db.session.commit()

    loser = rivals_list[-1]

    losing_cand = Candidates.query.filter_by(img=loser).first()
    candi_imgs.remove(losing_cand.img)
    losing_cand.loss = losing_cand.loss + 1
    db.session.commit()

    
 
         

# #     # add both to each other's opponents list
    oppofwinner = Opponents(loser,winning_cand.id) 
    oppofloser = Opponents(winner,losing_cand.id)
    db.session.add_all([oppofwinner,oppofloser])
    db.session.commit()
  
# add all opps score of these 2 rivals:
    winner_opplist = winning_cand.report_opponents()
    winner_oppscore = 0
    if winner_opplist:
        for winner_opp in winner_opplist:
            winner_thisopp = winner_opp.opponent_img
            winner_thisopp = Candidates.query.filter_by(img=winner_thisopp).first()
            # winneropp_list.append(winner_thisopp)
            winner_thisoppscore = winner_thisopp.score
            winner_oppscore = winner_oppscore + winner_thisoppscore


    loser_opplist = losing_cand.report_opponents()
    loser_oppscore = 0 
    if loser_opplist:
        for loser_opp in loser_opplist:
            loser_thisopp = loser_opp.opponent_img
            loser_thisopp = Candidates.query.filter_by(img=loser_thisopp).first()
            # loseropp_list.append(loser_thisoppscore)
            loser_thisoppscore = loser_thisopp.score
            loser_oppscore = loser_oppscore + loser_thisoppscore
  

# # add, deduct scores
    if winning_cand.win > winning_cand.loss:
        winning_cand.score = (winner_oppscore + 400*(winning_cand.win-winning_cand.loss))/(winning_cand.win+winning_cand.loss)
    else:
        winning_cand.score = (winner_oppscore + 400*(winning_cand.loss-winning_cand.win))/(winning_cand.win+winning_cand.loss)
    # winning_cand.score = (winner_oppscore + 400*(winning_cand.win-winning_cand.loss))/(winning_cand.win+winning_cand.loss)
    if losing_cand.win > losing_cand.loss:
        losing_cand.score = (loser_oppscore - 400*(losing_cand.win-losing_cand.loss))/(losing_cand.win+losing_cand.loss)
    else:
        losing_cand.score = (loser_oppscore - 400*(losing_cand.loss-losing_cand.win))/(losing_cand.win+losing_cand.loss)
    db.session.commit()
    
#list of winners after each round
    if len(no_ovlap) == 2*len(candi_imgs):
        no_ovlap = []
    elif len(no_ovlap) > 2*len(candi_imgs):
        no_ovlap = []
        # candi_img = candi_imgs2
  
# #once winner is decided:
    if len(candi_imgs) == 1:
        return redirect(url_for('result'))

    return redirect(url_for('rank'))
    

@app.route('/rank', methods=['GET'])
def rank():
    if 'user' in session:
       
        global no_ovlap
        img1 = random.choice(candi_imgs)
        no_ovlap.append(img1)  
    
        while True:
            img_test = random.choice(candi_imgs)
            if img_test in no_ovlap:
                continue
            elif img_test not in candi_imgs:
                continue
            else:
                img2 = img_test
                no_ovlap.append(img2)
                break

    #how to know when users only refresh the page, not count anything until form submitted

        if len(no_ovlap) == 2*len(candi_imgs): 
            no_ovlap = []
        if len(candi_imgs) == dbase_len and len(no_ovlap) == 4:
            no_ovlap = []
            
        
        return render_template('rank.html', img1=img1, img2=img2,candi_imgs=candi_imgs,no_ovlap=no_ovlap,candi_list=candi_list)
    else:
        return redirect(url_for('gatekeeper'))
######################
# html form needs to be submittable, upon submit, add score to the chosen image, update score in the db of that image
# then if all photos have been chosen (for now, wrong algo), redirect to results. otherwise, stay at rank.
# if photo chosen, add 200 scores to that image's score para =>> DONE




@app.route('/result')
def result():
    if 'user' in session:
        
        global no_ovlap
        global candi_imgs
        candi_imgs = []
        for candi in candi_list:
            candi_img = candi.img
            candi_imgs.append(candi_img)
        unsorted_score = []
        # max_score = None

        for candi in candi_imgs:
            
            #find the 3 candidates with highest scores
            cand_score = Candidates.query.filter_by(img=candi).first().score
            unsorted_score.append(cand_score)
        
        sorted_score = sorted(unsorted_score,reverse=True)

        top1_score = sorted_score[0]
        top1 = Candidates.query.filter_by(score=top1_score).first()
        top1_img = top1.img

        top2_score = sorted_score[1]
        top2 = Candidates.query.filter_by(score=top2_score).first()
        top2_img = top2.img

        top3_score = sorted_score[2]
        top3 = Candidates.query.filter_by(score=top3_score).first()
        top3_img = top3.img


        no_ovlap = []
        
        return render_template('result.html',sorted_score=sorted_score,top1 = top1, top2 = top2, top3 = top3, top1_img = top1_img, top2_img = top2_img, top3_img = top3_img)
        # return render_template('result.html',unsorted_score=unsorted_score,sorted_score=sorted_score, candi_imgs2=candi_imgs2)
    return redirect(url_for('gatekeeper'))

if __name__ == '__main__':
    app.run(debug=True)