from flask import Blueprint,render_template,flash,redirect,request,url_for,session,jsonify
from models import *
import bcrypt,os
from functools import wraps
from sqlalchemy import or_



controller=Blueprint("controller",__name__)

@controller.route('/')
def index():
    today = datetime.today().date()
    today_time=datetime.now()-timedelta(hours=24)
    
    for c in Campaigns.query.all():
        if c.start_date<= today and c.end_date>=today :
            c.status="Active"
        elif c.end_date <today:
            c.status="Completed"

        db.session.add(c)

    for i in OnlineSession.query.filter(OnlineSession.login_time < today_time).all():
        db.session.delete(i)
        
    db.session.commit()
    return render_template('start.html')

@controller.route('/sponsor_login',methods=["GET","POST"])
def sponsor_login():
    if request.method=="POST":
        if 'login' in request.form:
            email=request.form.get("email")
            password=request.form.get("password")

            sponsor=Sponsor.query.filter(Sponsor.email==email).first()
            if sponsor:
                if sponsor.checkpassword(password):
                    session_user=sponsor.email[0:4]+str(sponsor.id)+"sponsor"
                    session['user']=session_user

                    online=OnlineSession(user_id=sponsor.id,type="sponsor")
                    db.session.add(online)
                    db.session.commit()
                    
                    flash("Login successfull")
                    return redirect(url_for("controller.sponsor_dashboard",email=sponsor.email))
                else :
                    flash("Wrong Password !!!!")
            else:
                flash("Sponsor does not exist !!!!")
            return redirect(url_for('controller.sponsor_login'))
        
        else:
            email = request.form.get("email")
            name = request.form.get("name")
            type_ = request.form.get("type")
            password = request.form.get("password")

            if Sponsor.query.filter(Sponsor.email == email).first():
                flash("E-mail already registered")
                return redirect(url_for("controller.sponsor_login"))
            elif Influencer.query.filter(Influencer.email==email).first():
                flash("E-mail already registered as Influencer. Go to Influencer Login Page or use another Email")
                return redirect(url_for("controller.sponsor_login"))
            elif Admin.query.filter(Admin.email==email).first():
                flash("E-mail already registered")
                
            
            
            sponsor=Sponsor(email=email,name=name,type=type_,password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()))
            db.session.add(sponsor)
            db.session.commit()


    return render_template('sponsor_login.html')

@controller.route('/influencer_login',methods=["GET","POST"] )
def influencer_login():
    if request.method=="POST":
        if "login" in request.form:
            email=request.form.get("email")
            password=request.form.get("password")

            influencer=Influencer.query.filter(Influencer.email==email).first()

            if influencer:
                if influencer.checkpassword(password):
                    session_user=influencer.email[0:4]+str(influencer.id)+"influencer"
                    session['user']=session_user

                    online=OnlineSession(user_id=influencer.id,type="influencer")
                    db.session.add(online)
                    db.session.commit()

                    flash("Login Successfull !!!!") 
                    return redirect(url_for("controller.influencer_dashboard",email=influencer.email))
                else :
                    flash("Wrong Password !!!!")
            else:
                flash("Influencer does not exist !!!!")
            return redirect(url_for("controller.influencer_login"))

        else:
            email=request.form.get("email")
            password=request.form.get("password")
            name=request.form.get("name")
            sociallink=request.form.get("sociallink")
            category=request.form.get("category")
            niche=request.form.get("niche")
            platform=request.form.getlist("platform")
            platform_str=','.join(platform)

            if Influencer.query.filter(Influencer.email==email).first():
                flash("E-mail already registered")
                return redirect(url_for("controller.influencer_login"))
            elif Sponsor.query.filter(Sponsor.email==email).first():
                flash("E-mail already registered as an Sponsor. Go to the Sponsor Login Page or user another Email</a>")
                return redirect(url_for("controller.influencer_login"))
            elif Admin.query.filter(Admin.email==email).first():
                flash("E-mail already registered")
                
            
            influencer=Influencer(email=email,name=name,password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()),socialMediaLink=sociallink,niche=niche,category=category,platform=platform_str)
            db.session.add(influencer)
            db.session.commit()

    return render_template("influencer_login.html")

@controller.route("/admin_login",methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
            # comment out the code below to add the admin 
        
        # email="admin@gmail.com"
        # password="adminpassword"
        # admin=Admin(email=email,password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()))
        # db.session.add(admin)
        # db.session.commit()

        email=request.form.get("email")
        password=request.form.get("password")

        admin=Admin.query.filter(Admin.email==email).first()
        if admin:
            if admin.checkpassword(password):
                session_user=admin.email[0:4]+str(admin.id)+"admin"
                session['user']=session_user
                flash("Login Successfull !!!!") 
                return redirect(url_for("controller.admin_dashboard",email=email))
            else:
                flash("Wrong Password !!!!!!")
                
        else:
            flash("Admin permission denied for the given E-mail.") 
        return redirect(url_for("controller.admin_login"))

    return render_template("admin_login.html")




#Definition of auth_required
def auth_required(func):
    @wraps(func)
    def inner(email,*args,**kwargs):
        user=Influencer.query.filter(Influencer.email==email).first() 
        if user:
            session_user=user.email[0:4]+str(user.id)+"influencer"
            temp_re='influencer_login.html'
        else :
            user=Sponsor.query.filter(Sponsor.email==email).first()
            if user:
                session_user=user.email[0:4]+str(user.id)+"sponsor"
                temp_re='sponsor_login.html'
            else:
                user=Admin.query.filter(Admin.email==email).first() 
                if user:
                    session_user=user.email[0:4]+str(user.id)+"admin"
                    temp_re='admin_login.html'
                else :
                    return redirect(url_for('controller.index'))

        if 'user' in session and session['user'] == session_user:
            return func(email,*args,**kwargs)
        else :
            return render_template(temp_re)
        
    return inner





@controller.route("/influencer_dashboard/<email>",methods=["GET","POST"])
@auth_required
def influencer_dashboard(email):
    if request.method=="POST":
        if "accept" in request.form:
            id=request.form.get('id')
            ad=Ad_request.query.get(id)
            ad.negotiation_mesage=None
            ad.negotiation_party=None
            if ad.expected_amount:
                ad.payment_amount=ad.expected_amount
                ad.expected_amount=None
            ad.status="Accepted"
            ad.progress=0
            db.session.add(ad)
            db.session.commit()

            flash('Offer Accepted')
            return redirect(url_for('controller.influencer_dashboard',email=email))

        elif "reject" in request.form:
            id=request.form.get('id')
            ad=Ad_request.query.get(id)
            db.session.delete(ad)
            db.session.commit()

            if "pay" in request.form:
                flash("Payment Made ...")
            else:
                flash('Offer Rejected')
            return redirect(url_for('controller.influencer_dashboard',email=email))

        elif "i_offer" in request.form:
            id=request.form.get('id')
            ad=Ad_request.query.get(id)
            ad.negotiation_message=request.form.get('message')
            ad.negotiation_party="influencer"
            ad.expected_amount=request.form.get('payment_amount')
            db.session.add(ad)
            db.session.commit()

            flash("Offer Placed successfully.")
            return redirect(url_for('controller.influencer_dashboard',email=email))
        
        elif "up" in request.form:
            progress=request.form.get("slider")
            id=request.form.get('id')
            ad=Ad_request.query.get(id)
            ad.progress=progress
            db.session.add(ad)
            db.session.commit()

            flash("Progress successfully updated.")
            return redirect(url_for('controller.influencer_dashboard',email=email))

    
        elif "upload" in request.form:
            UPLOAD_FOLDER = './static/Uploads/influencer_profiles'

            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
            file = request.files['image']
            if file.filename == '':
                flash('No file selected')
                return redirect(url_for('controller.influencer_dashboard', email=email))

            if file and allowed_file(file.filename):
                user=Influencer.query.filter(Influencer.email==email).first()
                filename = str(user.id)+"."+file.filename.rsplit('.', 1)[1].lower()
                save_path = os.path.join(UPLOAD_FOLDER,filename)
                user.profile=save_path
                db.session.add(user)
                db.session.commit()

                try:
                    file.save(save_path)
                    flash(f"File successfully uploaded ..")
                except Exception as e:
                    flash(f"An error occurred while saving the file: {str(e)}")
                    return redirect(url_for('controller.influencer_dashboard', email=email))

                return redirect(url_for('controller.influencer_dashboard', email=email))
            else:
                flash("File not allowed or not provided.")
                return redirect(url_for('controller.influencer_dashboard', email=email))

    return render_template('influencer_dashboard.html', user = Influencer.query.filter_by(email=email).first(),campaigns=Campaigns,sponsor=Sponsor)

@controller.route("/sponsor_dashboard/<email>")
@auth_required
def sponsor_dashboard(email):
    return render_template('sponsor_dashboard.html', user = Sponsor.query.filter_by(email=email).first(),Influencer=Influencer)

@controller.route("/sponsor_dashboard/<email>/your_campaigns", methods=["GET", "POST"])
@auth_required
def sponsor_campaign(email):
    if request.method == "POST":
        if "edit" in request.form:
            
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            sponsor = Sponsor.query.filter_by(email=email).first()
            campaign_id=request.form.get("campaign_id_edit")
            campaign=Campaigns.query.get(campaign_id)
            campaign.name=request.form.get("name")
            campaign.description=request.form.get("description")
            campaign.goals=request.form.get("goals")
            campaign.budget=request.form.get("budget")
            campaign.visibility=request.form.get("visibility").lower()
            campaign.start_date=datetime.strptime(start_date, '%Y-%m-%d').date()
            campaign.end_date=datetime.strptime(end_date, '%Y-%m-%d').date()
            campaign.niche=request.form.get("niche")

            db.session.add(campaign)
            db.session.commit()
            flash('Campaign edited successfully!')

        elif "new" in request.form:
            name = request.form.get("name").upper()
            description = request.form.get("description")
            goals = request.form.get("goals")
            budget = request.form.get("budget")
            visibility = request.form.get("visibility")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            sponsor = Sponsor.query.filter_by(email=email).first()
            niche=request.form.get("niche")

            campaign = Campaigns( name=name, description=description, budget=int(budget), visibility=visibility.lower(),goals=goals,start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),niche=niche, sponsor_id=sponsor.id)
            
            db.session.add(campaign)
            db.session.commit()
            flash('Campaign created successfully!')

        elif "delete" in request.form:
            campaign_id=request.form.get("campaign_id_delete")
            campaign=Campaigns.query.get(campaign_id)
            db.session.delete(campaign)
            db.session.commit()
            flash("Campaign deleted successfully .")
        
        return redirect(url_for('controller.sponsor_campaign', email=email))

    return render_template("sponsor_campaigns.html", user=Sponsor.query.filter_by(email=email).first(),today=datetime.today().strftime('%Y-%m-%d'))

@controller.route("/sponsor_dashboard/<email>/your_campaigns/<campaign_id>",methods=["GET","POST"])
@auth_required
def view_campaign(email, campaign_id):
    if request.method == "POST":
        if "add" in request.form:
            message = request.form.get("message")
            requirements = request.form.get("requirements")
            payment_amount = request.form.get("payment_amount")
            influencer_id = request.form.get("influencer_id")
            influencer = Influencer.query.get(influencer_id)

            for i in influencer.ad_requests:
                if i.campaign_id == campaign_id:
                    flash("Request with the influencer already exists....")
                    return redirect(url_for('controller.view_campaign', email=email, campaign_id=campaign_id))

            ad_request = Ad_request(campaign_id=campaign_id, influencer_id=influencer_id, message=message, requirements=requirements, payment_amount=payment_amount)
            db.session.add(ad_request)
            db.session.commit()

            flash("Ad request created successfully.")
            return redirect(url_for('controller.view_campaign', email=email, campaign_id=campaign_id))
        
        if "s_offer" in request.form:
            n_message = request.form.get("message")
            ad=Ad_request.query.get(request.form.get('id'))
            ad.negotiation_party='sponsor'
            ad.negotiation_message=n_message
            db.session.add(ad)
            db.session.commit()

            flash("Offer Placed successfully.")
            return redirect(url_for('controller.view_campaign', email=email, campaign_id=campaign_id))
        
        if "accept" in request.form:
            id=request.form.get('id')
            ad=Ad_request.query.get(id)
            c=Campaigns.query.get(campaign_id)
            ad.negotiation_mesage=None
            ad.negotiation_party=None
            if ad.expected_amount:
                ad.payment_amount=ad.expected_amount
                ad.expected_amount=None
            ad.status="Accepted"
            ad.progress=0
            db.session.add(ad)
            db.session.commit()

            flash('Offer Accepted')
            return redirect(url_for('controller.view_campaign',email=email,campaign_id=campaign_id))

        if "reject" in request.form:
            id=request.form.get('id')
            ad=Ad_request.query.get(id)
            db.session.delete(ad)
            db.session.commit()

            flash('Offer Rejected')
            return redirect(url_for('controller.view_campaign',email=email,campaign_id=campaign_id))

        if "update_requirements" in request.form:
            id=request.form.get('id')
            ad=Ad_request.query.get(id)
            requirements=request.form.get("requirements")
            ad.requirements=requirements
            db.session.add(ad)
            db.session.commit()

            flash('Updated Requirements')
            return redirect(url_for('controller.view_campaign',email=email,campaign_id=campaign_id))

    sponsor = Sponsor.query.filter(Sponsor.email == email).first()
    campaign = Campaigns.query.filter(Campaigns.id == campaign_id).first()
    return render_template("sponsor_view_campaign.html", user=sponsor, campaign=campaign, influencer=Influencer)

@controller.route("/find/<email>",methods=["GET","POST"])
@auth_required
def find(email):
    if request.method == "POST":
        if "bid_offer" in request.form:
            message = request.form.get("message")
            payment_amount = request.form.get("payment_amount")

            ad_request = Ad_request(
                campaign_id=request.form.get("id"),
                influencer_id=request.form.get("u_id"),
                message=None,
                requirements=None,
                payment_amount=payment_amount
            )
            ad_request.negotiation_message = message
            ad_request.negotiation_party = "influencer"

            db.session.add(ad_request)
            db.session.commit()

        if "flag_btn_i" in request.form:
            id=request.form.get("id")
            influencer=Influencer.query.get(id)
            influencer.flagged= not influencer.flagged
            db.session.add(influencer)
            db.session.commit()

        if "flag_btn_c" in request.form:
            id=request.form.get("id")
            campaign=Campaigns.query.get(id)
            campaign.flagged= not campaign.flagged
            db.session.add(campaign)
            db.session.commit()

        return redirect(url_for('controller.find', email=email))
    
    search_query = request.args.get('query', '')
    selection = request.args.get('selection', 'none')

    filtered_campaigns = []
    filtered_influencers = []

    user = Influencer.query.filter_by(email=email).first()
    user_role = 'influencer' if user else 'none'
    
    if user:
        for campaign in Campaigns.query.all():
            has_requested = any(ad_request.influencer_id == user.id for ad_request in campaign.ad_requests)
            if not has_requested:
                filtered_campaigns.append(campaign)
    else:
        user = Sponsor.query.filter_by(email=email).first()
        user_role = 'sponsor' if user else 'none'
        if user:
            
            filtered_influencers = Influencer.query.filter(
                or_(
                    Influencer.name.ilike(f'%{search_query}%'),
                    Influencer.niche.ilike(f'%{search_query}%'),
                    Influencer.category.ilike(f'%{search_query}%')
                )
            ).all()
        else:
            user = Admin.query.filter_by(email=email).first()
            user_role = 'admin' if user else 'none'

            filtered_campaigns= Campaigns.query.join(Sponsor, Campaigns.sponsor_id == Sponsor.id).filter(
                or_(
                    Campaigns.name.ilike(f'%{search_query}%'),
                    Sponsor.name.ilike(f'%{search_query}%'),
                    Campaigns.niche.ilike(f'%{search_query}%')
                )
            ).all()

            filtered_influencers = Influencer.query.filter(
                or_(
                    Influencer.name.ilike(f'%{search_query}%'),
                    Influencer.niche.ilike(f'%{search_query}%'),
                    Influencer.category.ilike(f'%{search_query}%')
                )
            ).all()

            if not user:
                flash("Session Error please try again Later!!!!!")
                return redirect(url_for('controller.find', email=email))
        print (filtered_influencers)
        print (filtered_campaigns)

    return render_template(
        'find.html',
        user=user,
        user_role=user_role,
        filtered_i=filtered_influencers,
        filtered_c=filtered_campaigns,
        select=selection,
        search_query=search_query,
        influencer=Influencer,
        sponsor=Sponsor,
        admin=Admin,
        ad_request=Ad_request
    )
       
@controller.route("/admin_dashboard/<email>",methods=["GET","POST"])
@auth_required
def admin_dashboard(email):
    if request.method == "POST":
        if "flag_btn_i" in request.form:
            id=request.form.get("id")
            influencer=Influencer.query.get(id)
            influencer.flagged= not influencer.flagged
            db.session.add(influencer)
            db.session.commit()

        if "flag_btn_c" in request.form:
            id=request.form.get("id")
            campaign=Campaigns.query.get(id)
            campaign.flagged= not campaign.flagged
            db.session.add(campaign)
            db.session.commit()

        return redirect(url_for('controller.admin_dashboard', email=email))
    return render_template("admin_dashboard.html",user=Admin.query.filter(Admin.email==email).first(),influencer=Influencer,campaign=Campaigns,sponsor=Sponsor)

@controller.route("/stats/<email>")
@auth_required
def stats(email):
    user=Influencer.query.filter(Influencer.email==email).first()
    type="influencer"
    if not user:
        user=Sponsor.query.filter(Sponsor.email==email).first()
        type="sponsor"
        if not user:
            user=Admin.query.filter(Admin.email==email).first()
            type="admin"
            if not user:
                flash("Internal error User not Found !!!!")     
                return redirect(url_for("controller.index"))   
        
    

    return render_template("stats.html",user=user,type=type,influencer=Influencer,campaigns=Campaigns,sponsor=Sponsor)

@controller.route("/logout/<email>")
@auth_required
def logout(email):
    user=Influencer.query.filter(Influencer.email==email).first() 
    if user:
        session_user=user.email[0:4]+str(user.id)+"influencer"
        type="influencer"
    else :
        user=Sponsor.query.filter(Sponsor.email==email).first()
        if user:
            session_user=user.email[0:4]+str(user.id)+"sponsor" 
            type="sponsor"
        else:
            user=Admin.query.filter(Admin.email==email).first()
            if user:
                flash("Logout successful.")
                return redirect(url_for("controller.index"))
            

    online=OnlineSession.query.filter(OnlineSession.user_id==user.id,OnlineSession.type==type,OnlineSession.logout_time==None).first()
    if online:
        online.set_logout_time()
        db.session.commit()
        flash("Logout successful.")
    else:
        flash("No active session found for this user.")


    if 'user' in session and session['user'] == session_user:
        session.pop('user', None)
    return redirect(url_for('controller.index'))


#AJAX Functions and Routes

@controller.route('/sessions', methods=['GET'])
def get_sessions():
    sessions = OnlineSession.query.all()
    sessions_list = []
    for session in sessions:
        sessions_list.append({
            'id': session.id,
            'type': session.type,
            'user_id': session.user_id,
            'login_time': session.login_time,
            'logout_time': session.logout_time
        })
    return jsonify(sessions_list)

@controller.route('/get_flagged',methods=["GET"])
def get_flagged():
    flagged_list=({
        "i_f":Influencer.query.filter(Influencer.flagged==True).count(),
        "c_f":Campaigns.query.filter(Campaigns.flagged==True).count(),
    })

    return jsonify(flagged_list)
    
@controller.route("/get_work_composition/<email>",methods=["GET"])
def get_work_composition(email):
    user=Influencer.query.filter(Influencer.email==email).first()
    accepted_requests = Ad_request.query.filter_by(influencer_id=user.id, status="Accepted").all()
    avg_percentage=sum([req.progress for req in accepted_requests])/len(accepted_requests)

    workcomposition=({
        "avg_percentage": avg_percentage,
        "accepted_requests_count": len(accepted_requests)
    })

    return jsonify(workcomposition)

@controller.route("/get_ad_requests/<email>",methods=["GET"])
def get_ad_requests(email):
    user = Sponsor.query.filter(Sponsor.email==email).first()
    ad_requests = []
    for campaign in user.campaigns:
        for ad_request in campaign.ad_requests:
            if ad_request.status=="Accepted":
                ad_requests.append({
                    "id": ad_request.id,
                    "campaign_name": Campaigns.query.get(ad_request.campaign_id).name,
                    "status": ad_request.status,
                    "progress": ad_request.progress,
                })
    print(ad_requests)
    return jsonify(ad_requests)

@controller.route("/get_budget_info/<email>",methods=["GET"])
def get_budget_info(email):
    user = Sponsor.query.filter(Sponsor.email==email).first()
    budget_info=[]
    for campaign in user.campaigns:
        total_budget=campaign.budget
        spent=0
        for  ad_request in campaign.ad_requests:
            if ad_request.status=="Accepted":
                spent=spent+ad_request.payment_amount
        budget_info.append({
            "campaign_name": Campaigns.query.get(campaign.id).name,
            "total_budget":total_budget,
            "spent":spent
        })
    print(budget_info)
    return jsonify(budget_info)


