from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from openai import OpenAI
from extensions import db
import os
from dotenv import load_dotenv
from config import Config

blog_bp = Blueprint('blog', __name__)

load_dotenv()
client = OpenAI(api_key=Config.OPENAI_API_KEY)

@blog_bp.route('/blog-ai', methods=['GET', 'POST'])
@login_required
def blog_ai():
    generated = None

    if current_user.articles_generated >= 3:
        flash('Osiągnąłeś limit 3 wygenerowanych artykułów. Skontaktuj się z nami, aby uzyskać więcej.', 'danger')
        return render_template('blog_ai.html', generated=None, user=current_user)

    if request.method == 'POST':
        topic = request.form.get('topic')
        if not topic:
            flash('Podaj temat wpisu.', 'danger')
        else:
            # Generowanie tytułu SEO
            title_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": f"Wciel się w rolę developere z 10 letnim doświadczeniem w SEO i podaj mi dobry dla seo tytuł dla artykułu na temat: {topic}"}]
            )
            title = title_response.choices[0].message.content.strip()

            # Generowanie artykułu SEO
            content_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": f"Wciel się w rolę senior copywritera z 10 letnim doświadczeniem i napisz zoptymalizowany pod kątem SEO artykuł na temat: {topic}. Minimum 500 słów."}]
            )
            content = content_response.choices[0].message.content.strip()

            # Generowanie obrazka DALL-E
            image_prompt = f"Wciel się w rolę grafika z 10 letnim stażem. Stwórz prostą ilustrację pasującą idealnie do naszego tematu: {topic}. Ilustracja ma być prosta, czytelna, bez napisów. Jakościowa i dokładna."
            image_response = client.images.generate(
                prompt=image_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = image_response.data[0].url

            generated = {
                'title': title,
                'content': content,
                'image_url': image_url
            }

            current_user.articles_generated += 1
            db.session.commit()

            flash(f'Artykuł wygenerowany! Wykorzystałeś {current_user.articles_generated}/3 dostępnych.', 'success')

    return render_template('blog_ai.html', generated=generated, user=current_user)
