from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Site
from datetime import datetime
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

sites_bp = Blueprint('sites', __name__)
def take_screenshot(url, site_id):
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--window-size=1280,800")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.set_window_size(1280, 800)
        driver.get(url)
        time.sleep(2)

        screenshots_dir = 'static/screenshots'
        os.makedirs(screenshots_dir, exist_ok=True)

        filepath = os.path.join(screenshots_dir, f'site_{site_id}.png')
        driver.save_screenshot(filepath)
        return filepath
    except Exception as e:
        print(f'Błąd przy robieniu screenshota: {e}')
        return None
    finally:
        driver.quit()

def check_site_status(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code
    except requests.RequestException:
        return None

@sites_bp.route('/sites', methods=['GET', 'POST'])
@login_required
def sites():
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')

        status_code = check_site_status(url)

        new_site = Site(
            name=name,
            url=url,
            status_code=status_code,
            last_checked=datetime.utcnow(),
            owner=current_user
        )
        db.session.add(new_site)
        db.session.commit()

        flash('Strona została dodana.', 'success')
        return redirect(url_for('sites.sites'))

    user_sites = Site.query.filter_by(user_id=current_user.id).all()
    return render_template('sites.html', sites=user_sites, user=current_user)

@sites_bp.route('/sites/delete/<int:site_id>', methods=['POST'])
@login_required
def delete_site(site_id):
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first()

    if site:
        db.session.delete(site)
        db.session.commit()
        flash('Strona została usunięta.', 'info')
    else:
        flash('Nie znaleziono strony.', 'danger')

    return redirect(url_for('sites.sites'))

@sites_bp.route('/sites/refresh/<int:site_id>', methods=['POST'])
@login_required
def refresh_site(site_id):
    site = Site.query.filter_by(id=site_id, user_id=current_user.id).first()

    if site:
        site.status_code = check_site_status(site.url)
        site.last_checked = datetime.utcnow()

        site.screenshot_path = take_screenshot(site.url, site.id)

        db.session.commit()
        flash(f'Status strony "{site.name}" został odświeżony.', 'info')
    else:
        flash('Nie znaleziono strony.', 'danger')

    return redirect(url_for('sites.sites'))
