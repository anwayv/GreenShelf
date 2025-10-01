from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from werkzeug.utils import secure_filename
from app.models import db, Receipt, InventoryItem
import os
import cv2
import pytesseract
import re
import json
from datetime import datetime
from PIL import Image
import numpy as np

receipts_bp = Blueprint('receipts', __name__)

class ReceiptUploadForm(FlaskForm):
    receipt_file = FileField('Receipt Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed!')
    ])
    submit = SubmitField('Upload Receipt')

@receipts_bp.route('/')
@login_required
def index():
    """Display all uploaded receipts"""
    receipts = Receipt.query.filter_by(user_id=current_user.id).order_by(Receipt.created_at.desc()).all()
    return render_template('receipts/index.html', receipts=receipts)

@receipts_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload and process a receipt"""
    form = ReceiptUploadForm()
    
    if form.validate_on_submit():
        file = form.receipt_file.data
        if file:
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Create receipt record
            receipt = Receipt(
                user_id=current_user.id,
                filename=filename,
                file_path=file_path
            )
            db.session.add(receipt)
            db.session.commit()
            
            # Process receipt in background
            try:
                process_receipt(receipt.id)
                flash('Receipt uploaded and processed successfully!', 'success')
            except Exception as e:
                flash(f'Receipt uploaded but processing failed: {str(e)}', 'warning')
            
            return redirect(url_for('receipts.view', id=receipt.id))
    
    return render_template('receipts/upload.html', form=form)

@receipts_bp.route('/<int:id>')
@login_required
def view(id):
    """View a specific receipt"""
    receipt = Receipt.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('receipts/view.html', receipt=receipt)

@receipts_bp.route('/<int:id>/process', methods=['POST'])
@login_required
def process(id):
    """Manually process a receipt"""
    receipt = Receipt.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        process_receipt(receipt.id)
        flash('Receipt processed successfully!', 'success')
    except Exception as e:
        flash(f'Processing failed: {str(e)}', 'error')
    
    return redirect(url_for('receipts.view', id=receipt.id))

@receipts_bp.route('/<int:id>/apply', methods=['POST'])
@login_required
def apply_to_inventory(id):
    """Apply parsed receipt items to inventory"""
    receipt = Receipt.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if not receipt.is_processed:
        flash('Receipt must be processed first', 'error')
        return redirect(url_for('receipts.view', id=receipt.id))
    
    try:
        parsed_items = receipt.get_parsed_items()
        updated_count = 0
        
        for item in parsed_items:
            # Find or create inventory item
            inventory_item = InventoryItem.query.filter_by(
                user_id=current_user.id,
                name=item['name']
            ).first()
            
            if inventory_item:
                # Update existing item
                inventory_item.quantity += item['quantity']
                updated_count += 1
            else:
                # Create new item
                new_item = InventoryItem(
                    user_id=current_user.id,
                    name=item['name'],
                    quantity=item['quantity'],
                    unit=item.get('unit', 'pcs'),
                    threshold=item['quantity'] * 0.2,  # Set threshold to 20% of purchased quantity
                    blinkit_query=item['name']
                )
                db.session.add(new_item)
                updated_count += 1
        
        receipt.is_processed = True
        db.session.commit()
        
        flash(f'Applied {updated_count} items to inventory!', 'success')
        
    except Exception as e:
        flash(f'Failed to apply items to inventory: {str(e)}', 'error')
    
    return redirect(url_for('receipts.view', id=receipt.id))

def process_receipt(receipt_id):
    """Process a receipt using OCR and NLP"""
    receipt = Receipt.query.get(receipt_id)
    if not receipt:
        return
    
    try:
        # Load and preprocess image
        image = cv2.imread(receipt.file_path)
        if image is None:
            raise ValueError("Could not load image")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply preprocessing
        processed = preprocess_image(gray)
        
        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(processed, config='--psm 6')
        receipt.extracted_text = extracted_text
        
        # Parse items from text
        parsed_items = parse_receipt_text(extracted_text)
        receipt.set_parsed_items(parsed_items)
        
        # Extract total amount
        total_amount = extract_total_amount(extracted_text)
        receipt.total_amount = total_amount
        
        # Extract store name
        store_name = extract_store_name(extracted_text)
        receipt.store_name = store_name
        
        # Extract date
        purchase_date = extract_purchase_date(extracted_text)
        receipt.purchase_date = purchase_date
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error processing receipt {receipt_id}: {e}")
        raise

def preprocess_image(image):
    """Preprocess image for better OCR results"""
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Apply threshold to get binary image
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Apply morphological operations to clean up
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return cleaned

def parse_receipt_text(text):
    """Parse receipt text to extract items and quantities"""
    items = []
    lines = text.split('\n')
    
    # Common patterns for receipt items
    item_patterns = [
        r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?\s+(.+)',  # quantity unit item
        r'(.+?)\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?',  # item quantity unit
        r'(.+?)\s+(\d+(?:\.\d+)?)',  # item quantity
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip lines that look like totals, taxes, etc.
        if any(keyword in line.lower() for keyword in ['total', 'tax', 'subtotal', 'discount', 'change']):
            continue
        
        # Try to match item patterns
        for pattern in item_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    if pattern == item_patterns[0]:  # quantity unit item
                        quantity = float(match.group(1))
                        unit = match.group(2) or 'pcs'
                        name = match.group(3).strip()
                    elif pattern == item_patterns[1]:  # item quantity unit
                        name = match.group(1).strip()
                        quantity = float(match.group(2))
                        unit = match.group(3) or 'pcs'
                    else:  # item quantity
                        name = match.group(1).strip()
                        quantity = float(match.group(2))
                        unit = 'pcs'
                    
                    # Clean up item name
                    name = re.sub(r'\d+(?:\.\d+)?\s*[a-zA-Z]*\s*$', '', name).strip()
                    name = re.sub(r'[^\w\s]', '', name).strip()
                    
                    if name and quantity > 0:
                        items.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit
                        })
                        break
                        
                except (ValueError, IndexError):
                    continue
    
    return items

def extract_total_amount(text):
    """Extract total amount from receipt text"""
    # Look for total patterns
    total_patterns = [
        r'total[:\s]*(\d+(?:\.\d+)?)',
        r'amount[:\s]*(\d+(?:\.\d+)?)',
        r'grand\s+total[:\s]*(\d+(?:\.\d+)?)',
        r'final\s+total[:\s]*(\d+(?:\.\d+)?)',
    ]
    
    for pattern in total_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None

def extract_store_name(text):
    """Extract store name from receipt text"""
    lines = text.split('\n')
    # Usually store name is in the first few lines
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) > 3 and not re.search(r'\d', line):
            return line
    return None

def extract_purchase_date(text):
    """Extract purchase date from receipt text"""
    # Look for date patterns
    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        r'(\d{1,2}\s+\w+\s+\d{2,4})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                date_str = match.group(1)
                # Try to parse the date
                for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d %b %Y']:
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
            except:
                continue
    
    return None

