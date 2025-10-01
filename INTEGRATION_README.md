# Green Shelf - Cookie Management & Grocery Ordering Integration

This document describes the integration of cookie management and grocery ordering functionality into the existing Green Shelf application.

## 🚀 Features Added

### 1. Cookie Management System

- **Save Blinkit Cookies**: Users can save their Blinkit login cookies for automatic authentication
- **User-specific Cookies**: Each user has their own cookie file (`cookies_{user_id}.pkl`)
- **Cookie Status Indicator**: Dashboard shows whether cookies are saved
- **Secure Storage**: Cookies are stored locally and user-specific

### 2. Grocery Ordering System

- **Direct Product Links**: Pre-configured links for common grocery items
- **Automatic Cart Addition**: Items are automatically added to Blinkit cart
- **Checkout Integration**: Automatic checkout and payment initiation
- **Headless Mode**: Option to run browser in background
- **Order Tracking**: Orders are saved in the database

## 📁 Files Added/Modified

### New Files:

- `app/templates/cookies/save.html` - Cookie management UI
- `app/templates/grocery/order.html` - Grocery ordering UI
- `migrate_cookies_field.py` - Database migration script
- `test_integration.py` - Integration test script
- `INTEGRATION_README.md` - This documentation

### Modified Files:

- `app/routes.py` - Added cookie management and grocery ordering routes
- `app/models.py` - Added `cookies_saved` field to User model
- `app/templates/index.html` - Added links to new features
- `bot/green_shelf_bot.py` - Added cookie loading functionality

## 🔧 Setup Instructions

### 1. Database Migration

Run the migration script to add the new field:

```bash
python migrate_cookies_field.py
```

### 2. Test Integration

Verify everything works correctly:

```bash
python test_integration.py
```

### 3. Start Application

```bash
python run.py
```

## 🎯 How to Use

### Cookie Management

1. Navigate to the dashboard
2. Click "Cookie Management" in Quick Actions
3. Click "Open Browser for Login"
4. Complete your Blinkit login in the opened browser
5. Cookies will be saved automatically

### Grocery Ordering

1. Ensure cookies are saved (green badge on dashboard)
2. Click "Grocery Order" in Quick Actions
3. Enter your grocery list (one item per line)
4. Choose headless mode if desired
5. Click "Place Order"
6. Approve payment in your UPI app

## 📋 Supported Products

The system includes direct links for common grocery items:

### Dairy Products:

- Amul Milk (500ml, 200ml)
- Gokul Full Cream Milk
- Mother Dairy Cow Milk
- Amul Gold Milk
- And many more...

### Bread Products:

- English Oven Sandwich White Bread
- Britannia Brown Bread
- Modern White Bread
- Britannia Pav
- And more...

## 🔒 Security Features

- **User Isolation**: Each user's cookies are stored separately
- **Local Storage**: Cookies are stored locally, not on external servers
- **Session Management**: Cookies are loaded per user session
- **Error Handling**: Graceful fallback when cookies are not available

## 🐛 Troubleshooting

### Common Issues:

1. **"No Cookies Saved" Warning**

   - Solution: Go to Cookie Management and save your Blinkit cookies

2. **"Cookies Required" Error**

   - Solution: Complete the cookie saving process first

3. **Browser Doesn't Open**

   - Solution: Ensure Chrome is installed and Selenium is properly configured

4. **Items Not Added to Cart**
   - Solution: Check if the item name matches exactly with supported products

### Debug Mode:

- Uncheck "Headless Mode" to see the browser in action
- Check the console output for detailed error messages
- Screenshots are automatically saved in `data/screenshots/` for debugging

## 🔄 Integration with Existing Features

### Inventory Management:

- Low stock items can be automatically ordered using the existing inventory system
- The new grocery ordering system works alongside the existing order functionality

### User Authentication:

- Cookie management is tied to user accounts
- Each user maintains their own Blinkit authentication

### Order Tracking:

- All orders (both inventory-based and grocery list-based) are tracked in the same system
- Notifications are sent for all order types

## 🚀 Future Enhancements

- **Product Search Integration**: Add more products to the direct link database
- **Price Comparison**: Compare prices across different items
- **Scheduled Orders**: Set up recurring orders
- **Delivery Time Selection**: Choose preferred delivery slots
- **Order History**: Enhanced order tracking and history

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Run the test script to verify integration
3. Check the console output for error messages
4. Ensure all dependencies are installed correctly

## 🔧 Technical Details

### Cookie Storage:

- Format: Pickle files (`cookies_{user_id}.pkl`)
- Location: Project root directory
- Content: Selenium cookie objects from Blinkit

### Browser Configuration:

- Uses Chrome with custom profile
- Profile location: `C:\Users\ranve\SeleniumProfile`
- Profile name: `Automation`

### Database Schema:

- Added `cookies_saved` boolean field to User table
- Default value: `False`
- Updated via migration script

---

**Note**: This integration maintains backward compatibility with existing features while adding new functionality. All existing workflows continue to work as before.
