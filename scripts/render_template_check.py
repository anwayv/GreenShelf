from app import create_app
from flask import render_template

app = create_app()
# allow url_for and other url building outside request
app.config['SERVER_NAME'] = 'localhost:5000'
with app.app_context():
    try:
        # Render the recipes index template to catch syntax errors
        html = render_template('recipes/index.html', recipes=[], general_recipes=[])
        print('Template rendered successfully (length:', len(html), ')')
    except Exception as e:
        print('Error rendering template:', str(e))
