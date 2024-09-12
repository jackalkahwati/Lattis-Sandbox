from flask import Blueprint, jsonify, request

bp = Blueprint('integration', __name__, url_prefix='/integration')

@bp.route('/gbfs', methods=['POST'])
def ingest_gbfs_data():
    """
    Ingest real-time bike location data from GBFS
    ---
    parameters:
      - name: gbfs_data
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: GBFS data ingested successfully
      400:
        description: Bad request
    """
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'gbfs_data' not in data:
            return jsonify({'error': 'Invalid or missing GBFS data'}), 400

        # In a real implementation, we would process and store the GBFS data
        # For this sandbox, we'll just acknowledge receipt
        return jsonify({'message': 'GBFS data received and processed'})
    except Exception as e:
        return jsonify({'error': 'An error occurred while processing the request', 'details': str(e)}), 500

@bp.route('/crm', methods=['POST'])
def connect_repair_ticket():
    """
    Connect repair tickets with CRM
    ---
    parameters:
      - name: ticket_id
        in: body
        required: true
        type: string
      - name: customer_id
        in: body
        required: true
        type: string
      - name: issue_description
        in: body
        required: true
        type: string
    responses:
      200:
        description: Repair ticket connected with CRM
      400:
        description: Bad request
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({'error': 'Invalid request data'}), 400

        required_fields = ('ticket_id', 'customer_id', 'issue_description')
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # In a real implementation, we would integrate with a CRM system
        # For this sandbox, we'll simulate the connection
        crm_response = {
            'ticket_id': data['ticket_id'],
            'customer_id': data['customer_id'],
            'issue_description': data['issue_description'],
            'status': 'Connected to CRM',
            'crm_reference': f"CRM-{data['ticket_id']}"
        }
        return jsonify(crm_response)
    except Exception as e:
        return jsonify({'error': 'An error occurred while processing the request', 'details': str(e)}), 500
