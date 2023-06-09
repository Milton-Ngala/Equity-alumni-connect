from flask import Blueprint, render_template, url_for, request, flash, jsonify, redirect
from flask_login import login_required,  current_user
from flask_wtf.csrf import generate_csrf
from .models import User, AlumniScholarProfiles, Events, Careers
from . import db
from datetime import datetime
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'] )
def home(): 
    return render_template("home.html", user=current_user)

@views.route('/about')
def about():
    return render_template("about.html", user=current_user)

@views.route('/events', methods=['GET', 'POST'])
def events():
    search_query = request.form.get('search')
    if search_query:
        events = Events.query.filter(Events.event_name.ilike(f'%{search_query}%')).order_by(Events.event_date.asc()).all()
    else:
        events = Events.query.order_by(Events.event_date.asc()).all()
    return render_template("events.html", user=current_user, events=events, search_query=search_query)


@views.route('/upcoming events', methods=['GET', 'POST'])
def upcoming_events():
    if request.method == 'POST':
        search_query = request.form['search_query']
        events = Events.query.filter(Events.event_name.contains(search_query)).order_by(Events.event_date.asc()).all()
    else:
        events = Events.query.order_by(Events.event_date.asc()).all()
    
    today = datetime.today().date()
    upcoming_events = [event for event in events if event.event_date.date() >= today]
    
    return render_template("events.html", user=current_user, events=upcoming_events, )


@views.route('/events/<int:event_id>')
@login_required
def event_details(event_id):
    # Retrieve the event details from the database using the event_id
    event = Events.query.filter_by(id=event_id).first()
    if not event:
        return "<h1> Event Not found</h1? <a href='{{url_for('views.events')}};>Go back</a>"
    # Render the event details template with the event object
    return render_template('event_details.html',user=current_user, event=event)


@views.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        event = Events(
            user_id=current_user.id,
            event_name=request.form.get('event_name'),
            event_venue=request.form.get('event_venue'),
            event_date=datetime.strptime(request.form.get('event_date'), '%Y-%m-%dT%H:%M') if request.form.get('event_date') else None,
            event_description=request.form.get('event_description'),
            phone_number=request.form.get('phone_number'),
            email=request.form.get('email')
        )
        db.session.add(event)
        db.session.commit()
        flash('Your event has been created!', 'success')
        return redirect(url_for('views.events'))
    csrf_token = generate_csrf()
    return render_template("create_event.html", user=current_user, csrf_token=csrf_token)


@views.route('/careers', methods=['GET', 'POST'] )
def careers():
    search_query = request.form.get('search')
    if search_query:
        careers = Careers.query.filter(Careers.job_title.ilike(f'%{search_query}%')).order_by(Careers.date_published.asc()).all()
    else:
        careers = Careers.query.order_by(Careers.date_published.asc()).all()
    return render_template("careers.html", user=current_user, careers=careers, search_query=search_query)

@views.route('/create-job-listing', methods=['GET', 'POST'])
@login_required
def create_job_listing():
    if request.method == 'POST':
        career = Careers(
            user_id=current_user.id,
            job_title=request.form.get('job_title'),
            company=request.form.get('company'),
            location=request.form.get('location'),
            salary=request.form.get('salary'),
            deadline_date=request.form.get('deadline_date'),
            job_description=request.form.get('job_description'),
            phone_number=request.form.get('phone_number'),
            email=request.form.get('email')
        )
        db.session.add(career)
        db.session.commit()
        flash('Your job listing has been created!', 'success')
        return redirect(url_for('views.careers'))
    return render_template("create_job.html", user=current_user)


@views.route('/find-alumni', methods=['GET', 'POST'])
def find_alumni():
    search_query = request.form.get('search')
    if search_query:
        scholars = User.query.filter(
            (User.firstname.ilike(f'%{search_query}%')) | 
            (User.lastname.ilike(f'%{search_query}%'))
        ).order_by(User.firstname.asc()).all() 
    else:
        scholars = User.query.order_by(User.firstname.asc()).all()
    return render_template("find_alumni.html", user=current_user, scholars=scholars)


@views.route('/profile/<int:scholar_id>')
@login_required
def profile_detail(scholar_id):
    scholar = User.query.filter_by(id=scholar_id).first()
    return render_template('profile_details.html',user=current_user, scholar=scholar)
