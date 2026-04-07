from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Job, Application, User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        users = User.query.all()
        jobs = Job.query.all()
        return render_template('admin_dashboard.html', users=users, jobs=jobs)

    elif current_user.role == 'company':
        jobs = Job.query.filter_by(company_id=current_user.id).all()
        return render_template('company_dashboard.html', jobs=jobs)

    else:  # student
        jobs = Job.query.all()
        # Get job IDs this student has already applied to
        applied_job_ids = {
            app.job_id for app in Application.query.filter_by(user_id=current_user.id).all()
        }
        return render_template('student_dashboard.html', jobs=jobs, applied_job_ids=applied_job_ids)


# ── Company: Post a job ─────────────────────────────────────────────────────

@main.route('/jobs/new', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'company':
        flash('Only companies can post jobs.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title or not description:
            flash('Title and description are required.', 'error')
            return render_template('post_job.html')

        job = Job(title=title, description=description, company_id=current_user.id)
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('post_job.html')


# ── Company: View applicants for a job ──────────────────────────────────────

@main.route('/jobs/<int:job_id>/applicants')
@login_required
def view_applicants(job_id):
    job = Job.query.get_or_404(job_id)

    if current_user.role != 'company' or job.company_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    applications = Application.query.filter_by(job_id=job_id).all()
    return render_template('applicants.html', job=job, applications=applications)


# ── Company: Update application status ──────────────────────────────────────

@main.route('/applications/<int:app_id>/update', methods=['POST'])
@login_required
def update_application(app_id):
    application = Application.query.get_or_404(app_id)
    job = Job.query.get(application.job_id)

    if current_user.role != 'company' or job.company_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    new_status = request.form.get('status')
    if new_status in ('applied', 'accepted', 'rejected'):
        application.status = new_status
        db.session.commit()
        flash('Application status updated.', 'success')

    return redirect(url_for('main.view_applicants', job_id=job.id))


# ── Student: Apply for a job ─────────────────────────────────────────────────

@main.route('/jobs/<int:job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    if current_user.role != 'student':
        flash('Only students can apply for jobs.', 'error')
        return redirect(url_for('main.dashboard'))

    job = Job.query.get_or_404(job_id)

    already_applied = Application.query.filter_by(
        user_id=current_user.id, job_id=job_id
    ).first()

    if already_applied:
        flash('You have already applied for this job.', 'error')
    else:
        application = Application(user_id=current_user.id, job_id=job_id)
        db.session.add(application)
        db.session.commit()
        flash(f'Successfully applied for "{job.title}"!', 'success')

    return redirect(url_for('main.dashboard'))


# ── Student: View my applications ───────────────────────────────────────────

@main.route('/my-applications')
@login_required
def my_applications():
    if current_user.role != 'student':
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    applications = Application.query.filter_by(user_id=current_user.id).all()
    return render_template('my_applications.html', applications=applications)
