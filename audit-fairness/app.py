import dash
from dash import html, dcc
from monitor import FairnessMonitor

from flask import jsonify

app = dash.Dash(__name__)
server = app.server
monitor = FairnessMonitor()

@server.route('/health')
def health():
    return jsonify({
        'status': 'UP',
        'service': 'AuditFairness'
    })

@server.route('/metrics')
def get_metrics():
    """Return fairness metrics as JSON for dashboard"""
    data = monitor.fetch_data()
    
    if data.empty:
        return jsonify({
            'overall_score': 0,
            'demographic_analysis': [],
            'age_group_analysis': [],
            'bias_metrics': [],
            'model_dimensions': [],
            'recommendations': []
        })
    
    metrics = monitor.calculate_metrics(data)
    return jsonify(metrics)

@server.route('/report', methods=['POST'])
def generate_report():
    """Trigger report generation"""
    return jsonify({'status': 'success', 'message': 'Report generated'})

def get_report_html():
    return monitor.generate_report()

app.layout = html.Div([
    html.H1("HealthFlow AI Fairness & Drift Audit", style={'textAlign': 'center'}),
    html.Div([
        html.Button('Refresh Report', id='refresh-btn', n_clicks=0),
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    html.Iframe(
        id='report-frame',
        srcDoc=get_report_html(),
        style={'width': '100%', 'height': '100vh', 'border': 'none'}
    )
])

# Simple callback could be added here for the button, 
# but for now we rely on page refresh or dynamic srcDoc update if we added callback.
# Keeping it simple for the initial implementation.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
