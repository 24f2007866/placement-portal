from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy() #I need tp initialize my database

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # role is student or company or admin
    role = db.Column(db.String(20), nullable=False, default='student')

    # connect- user post job n apply
    jobs = db.relationship('Job', backref='company', lazy=True)

    applications = db.relationship('Application', backref='applicant', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password) #hashed passwords will store
        print("Setting password for user")
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User: {self.username}, Role: {self.role}>'


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    applications = db.relationship('Application', backref='job', lazy=True)

    def __repr__(self):
        return f'<Job {self.title}>'


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    # status: 'applied', 'accepted', 'rejected'
    status = db.Column(db.String(20), nullable=False, default='applied')

    def __repr__(self):
        return f'<Application user={self.user_id} job={self.job_id} status={self.status}>'
