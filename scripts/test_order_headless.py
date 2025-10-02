from app import create_app
from unittest.mock import patch

app = create_app()
app.config['SERVER_NAME'] = 'localhost'
app.config['WTF_CSRF_ENABLED'] = False

with app.test_client() as client:
    with app.app_context():
        # Prepare form data
        data = {
            'upi': 'user@upi',
            'checkout': '1',
            'headless': '1',
            'grocery_list': 'amul milk 500ml\nenglish oven sandwich white bread'
        }

        # Patch the GreenShelfBot to avoid real Selenium calls
        with patch('app.routes.GreenShelfBot') as MockBot:
            instance = MockBot.return_value
            instance.process_items.return_value = ['✅ item added']
            instance.proceed_to_checkout_and_select_upi.return_value = ['✅ UPI triggered']

            resp = client.post('/order', data=data, follow_redirects=True)
            print('Status code:', resp.status_code)
            print('Response data snippet:', resp.data[:500])
