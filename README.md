# 🛒 Green Shelf - Smart Grocery Management

Green Shelf is a comprehensive grocery automation app that handles inventory management, meal planning, recipe suggestions, and automated ordering through intelligent scheduling and AI integration.

## ✨ Features

### 🧠 Smart Automation
- **Automated Inventory Tracking**: Automatically track inventory levels and generate shopping lists
- **AI-Powered Recipe Suggestions**: Get personalized recipes based on available ingredients using Gemini AI
- **Smart Meal Planning**: Plan weekly meals with automatic inventory deduction
- **Automated Ordering**: Seamless Blinkit integration for automatic order placement

### 📱 User Experience
- **User Registration & Authentication**: Secure user accounts with personalized preferences
- **Receipt Processing**: Upload receipt photos and automatically update inventory using OCR
- **Preference Management**: Set family size, dietary restrictions, brand preferences, and delivery times
- **Real-time Notifications**: Get notified about low stock, order confirmations, and reminders

### 🔧 Technical Features
- **Database Integration**: SQLAlchemy with SQLite/PostgreSQL support
- **OCR & NLP**: Advanced receipt processing with OpenCV and Tesseract
- **AI Integration**: Google Gemini API for recipe suggestions
- **Selenium Automation**: Headless browser automation for Blinkit integration
- **Responsive UI**: Modern Bootstrap-based interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome browser (for Selenium automation)
- Google Gemini API key (optional, for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Green-Shelf
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   PINCODE=your-pincode-here
   UPI_ID=your-default-upi-id@upi
   ```

4. **Initialize the database**
   ```bash
   python run.py
   ```
   The database will be created automatically on first run.

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

## 📋 Setup Guide

### 1. User Registration
- Create your account with username, email, and basic preferences
- Set your family size and pincode for delivery

### 2. Connect Blinkit (Optional)
- Use the onboarding flow to connect your Blinkit account
- This enables automated ordering features

### 3. Add Inventory
- **Manual Entry**: Add items manually with quantities and thresholds
- **Receipt Upload**: Upload receipt photos for automatic inventory population
- **Category Organization**: Organize items by categories (dairy, vegetables, etc.)

### 4. Configure Preferences
- Set preferred brands and dietary restrictions
- Configure delivery time slots
- Enable auto-ordering if desired

### 5. Start Meal Planning
- Browse AI-generated recipe suggestions
- Plan weekly meals using the calendar interface
- Mark meals as cooked to automatically update inventory

## 🏗️ Architecture

### Backend Structure
```
app/
├── __init__.py          # Flask app initialization
├── models.py            # Database models
├── routes.py            # Main dashboard routes
├── auth.py              # Authentication routes
├── recipes.py           # Recipe management
├── meal_planning.py     # Meal planning features
├── receipts.py          # Receipt processing
├── templates/           # HTML templates
└── static/             # CSS and static files

bot/
├── green_shelf_bot.py   # Selenium automation
└── utils.py            # Bot utilities

data/                   # Data storage
├── inventory.json      # Legacy inventory (migrated to DB)
└── screenshots/        # Debug screenshots
```

### Database Schema
- **Users**: User accounts with preferences
- **InventoryItems**: Grocery items with quantities and thresholds
- **Recipes**: Recipe collection with ingredients and instructions
- **MealPlans**: Weekly meal planning calendar
- **Orders**: Order history and tracking
- **Receipts**: Receipt processing and OCR results
- **Notifications**: User notifications and alerts

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `GEMINI_API_KEY`: Google Gemini API key for AI features
- `PINCODE`: Default pincode for Blinkit delivery
- `UPI_ID`: Default UPI ID for payments
- `HEADLESS`: Run Selenium in headless mode (True/False)
- `DATABASE_URL`: Database connection string

### AI Integration
To enable AI recipe suggestions:
1. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to your `.env` file as `GEMINI_API_KEY`
3. Restart the application

### Blinkit Automation
The app includes Selenium automation for Blinkit integration:
- Automatically adds items to cart
- Handles checkout process
- Supports UPI payment integration
- Runs in background for auto-ordering

## 📱 Usage

### Dashboard
- View current inventory with low-stock alerts
- Quick access to all features
- Recent notifications and activity

### Inventory Management
- Add/edit/delete items
- Set quantity thresholds
- Organize by categories
- Upload receipts for automatic updates

### Recipe Management
- Browse your recipe collection
- Get AI suggestions based on available ingredients
- Add custom recipes
- Mark recipes as cooked to update inventory

### Meal Planning
- Weekly calendar view
- Plan breakfast, lunch, dinner, and snacks
- Generate shopping lists based on meal plans
- Auto-suggest meals based on inventory

### Receipt Processing
- Upload receipt photos
- AI-powered OCR extraction
- Review and edit extracted items
- Apply to inventory with one click

## 🔒 Security

- User authentication with Flask-Login
- CSRF protection with Flask-WTF
- Secure password hashing
- Session management
- Input validation and sanitization

## 🚀 Deployment

### Production Setup
1. Set `FLASK_ENV=production`
2. Use a production database (PostgreSQL recommended)
3. Set up proper secret keys
4. Configure reverse proxy (nginx)
5. Use WSGI server (gunicorn)

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments

## 🔮 Future Enhancements

- [ ] Mobile app development
- [ ] Multi-store integration (BigBasket, Grofers)
- [ ] Advanced AI meal planning
- [ ] Social features and recipe sharing
- [ ] Barcode scanning
- [ ] Voice commands
- [ ] Integration with smart home devices


