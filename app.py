"""
ISIS Metrics Dashboard - Main Application
Collects and visualizes ISIS routing protocol metrics from Junos routers
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
import os
from dotenv import load_dotenv
from isis_collector import ISISCollector
from dashboard import create_dashboard_callbacks
from database import init_database, save_metrics, get_metrics_history

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/isis_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize database
init_database()

# Initialize ISIS Collector
isis_collector = ISISCollector()


@app.route('/')
def index():
    """Render main dashboard page"""
    return render_template('index.html')


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    API endpoint to get current ISIS metrics
    Query params:
    - device: device hostname/IP
    - format: json or xml
    """
    try:
        device = request.args.get('device', None)
        output_format = request.args.get('format', 'json')
        
        if not device:
            return jsonify({'error': 'Device parameter required'}), 400
        
        # Collect metrics from device
        metrics = isis_collector.collect_metrics(device)
        
        if not metrics:
            return jsonify({'error': f'Failed to collect metrics from {device}'}), 500
        
        # Save to database
        save_metrics(device, metrics)
        
        return jsonify(metrics), 200
    
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/history', methods=['GET'])
def get_metrics_history_api():
    """Get historical metrics data"""
    try:
        device = request.args.get('device', None)
        hours = request.args.get('hours', 24, type=int)
        
        if not device:
            return jsonify({'error': 'Device parameter required'}), 400
        
        history = get_metrics_history(device, hours)
        return jsonify(history), 200
    
    except Exception as e:
        logger.error(f"Error fetching metrics history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get list of configured devices"""
    try:
        devices = isis_collector.get_configured_devices()
        return jsonify({'devices': devices}), 200
    except Exception as e:
        logger.error(f"Error fetching devices: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    }), 200


@app.route('/api/devices/<device>/connect', methods=['POST'])
def test_device_connection(device):
    """Test SSH connection to a device"""
    try:
        result = isis_collector.test_connection(device)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Connection test failed for {device}: {str(e)}")
        return jsonify({'error': str(e), 'connected': False}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create logs directory if it doesn't exist (moved to top)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Run Flask app
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting ISIS Metrics Dashboard on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
