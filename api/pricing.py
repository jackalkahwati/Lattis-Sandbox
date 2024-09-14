from flask import Blueprint, jsonify, request
from models import PricingRule
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError
import json

bp = Blueprint('pricing', __name__, url_prefix='/api/v1/pricing')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class BasePriceSchema(Schema):
    base_price = fields.Float(required=True)

class SurgePricingSchema(Schema):
    multiplier = fields.Float(required=True)
    conditions = fields.Dict(required=True)

@bp.route('/base', methods=['POST'])
def set_base_price():
    try:
        schema = BasePriceSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        base_price_rule = PricingRule.query.filter_by(rule_type='base').first()
        if base_price_rule:
            base_price_rule.price_modifier = data['base_price']
        else:
            base_price_rule = PricingRule(
                name='Base Price',
                rule_type='base',
                price_modifier=data['base_price']
            )
            db.session.add(base_price_rule)

        db.session.commit()
        return jsonify({"message": "Base price set successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in set_base_price: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while setting the base price"}), 500

@bp.route('/surge', methods=['POST'])
def set_surge_pricing():
    try:
        schema = SurgePricingSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        surge_rule = PricingRule.query.filter_by(rule_type='surge').first()
        if surge_rule:
            surge_rule.price_modifier = data['multiplier']
            surge_rule.conditions = json.dumps(data['conditions'])
        else:
            surge_rule = PricingRule(
                name='Surge Pricing',
                rule_type='surge',
                price_modifier=data['multiplier'],
                conditions=json.dumps(data['conditions'])
            )
            db.session.add(surge_rule)

        db.session.commit()
        return jsonify({"message": "Surge pricing rules set successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in set_surge_pricing: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while setting surge pricing rules"}), 500

@bp.route('/rules', methods=['GET'])
def get_pricing_rules():
    try:
        rules = PricingRule.query.all()
        return jsonify([{
            "id": rule.id,
            "name": rule.name,
            "rule_type": rule.rule_type,
            "price_modifier": rule.price_modifier,
            "conditions": json.loads(rule.conditions) if rule.conditions else None,
            "created_at": rule.created_at.isoformat()
        } for rule in rules]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_pricing_rules: {str(e)}")
        return jsonify({"error": "An error occurred while fetching pricing rules"}), 500