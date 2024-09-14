from flask import Blueprint, jsonify, request
from models import Invoice, User
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

bp = Blueprint('payment', __name__, url_prefix='/api/v1')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class InvoiceSchema(Schema):
    user_id = fields.Integer(required=True)
    amount = fields.Float(required=True)
    description = fields.String(required=True)

class PaymentSchema(Schema):
    invoice_id = fields.Integer(required=True)
    amount = fields.Float(required=True)
    payment_method = fields.String(required=True)

@bp.route('/invoices', methods=['POST'])
def create_invoice():
    try:
        schema = InvoiceSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        new_invoice = Invoice(
            user_id=data['user_id'],
            amount=data['amount'],
            description=data['description'],
            status='Pending',
            created_at=datetime.utcnow()
        )
        db.session.add(new_invoice)
        db.session.commit()
        return jsonify({"message": "Invoice created successfully", "invoice_id": new_invoice.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_invoice: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while creating the invoice"}), 500

@bp.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    try:
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404

        return jsonify({
            "id": invoice.id,
            "user_id": invoice.user_id,
            "amount": invoice.amount,
            "description": invoice.description,
            "status": invoice.status,
            "created_at": invoice.created_at.isoformat()
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_invoice: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the invoice"}), 500

@bp.route('/invoices', methods=['GET'])
def list_invoices():
    try:
        invoices = Invoice.query.all()
        return jsonify([{
            "id": invoice.id,
            "user_id": invoice.user_id,
            "amount": invoice.amount,
            "description": invoice.description,
            "status": invoice.status,
            "created_at": invoice.created_at.isoformat()
        } for invoice in invoices]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_invoices: {str(e)}")
        return jsonify({"error": "An error occurred while fetching invoices"}), 500

@bp.route('/payments', methods=['POST'])
def process_payment():
    try:
        schema = PaymentSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        invoice = Invoice.query.get(data['invoice_id'])
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404

        if invoice.status == 'Paid':
            return jsonify({"error": "Invoice has already been paid"}), 400

        if data['amount'] != invoice.amount:
            return jsonify({"error": "Payment amount does not match invoice amount"}), 400

        # In a real-world scenario, you would integrate with a payment gateway here
        # For this example, we'll just mark the invoice as paid
        invoice.status = 'Paid'
        db.session.commit()

        return jsonify({"message": "Payment processed successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in process_payment: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while processing the payment"}), 500

@bp.route('/billing/history', methods=['GET'])
def get_billing_history():
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        invoices = Invoice.query.filter_by(user_id=user_id).order_by(Invoice.created_at.desc()).all()
        return jsonify([{
            "id": invoice.id,
            "amount": invoice.amount,
            "description": invoice.description,
            "status": invoice.status,
            "created_at": invoice.created_at.isoformat()
        } for invoice in invoices]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_billing_history: {str(e)}")
        return jsonify({"error": "An error occurred while fetching billing history"}), 500