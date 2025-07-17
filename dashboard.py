from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Site
from extensions import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    sites = Site.query.filter_by(user_id=current_user.id).all()
    sites_count = len(sites)
    success_count = sum(1 for s in sites if s.status_code == 200)
    error_count = sum(1 for s in sites if s.status_code != 200)

    status_counts = {}
    for site in sites:
        key = str(site.status_code) if site.status_code else "Brak"
        status_counts[key] = status_counts.get(key, 0) + 1

    recent_sites = Site.query.filter_by(user_id=current_user.id).order_by(Site.last_checked.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        user=current_user,
        sites_count=sites_count,
        success_count=success_count,
        error_count=error_count,
        status_labels=list(status_counts.keys()),
        status_data=list(status_counts.values()),
        recent_sites=recent_sites
    )
