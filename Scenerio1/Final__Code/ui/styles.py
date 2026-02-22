"""
Custom CSS styles for the Streamlit dashboard
"""

def get_custom_css():
    return """
    <style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Status cards */
    .status-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .status-success {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    
    .status-error {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
    
    .status-progress {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    
    .status-idle {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #28a745;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Alert messages */
    .alert-success {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        margin: 1rem 0;
    }
    
    .alert-error {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
        margin: 1rem 0;
    }
    
    /* History table */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Title styling */
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }
    
    h2, h3 {
        color: #34495e;
    }

    /* Transfer banner */
    .transfer-banner {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background-color: #fffbea;
        border-left: 5px solid #f0ad4e;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-top: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }

    .transfer-spinner {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: linear-gradient(90deg, #f0ad4e, #ffc107);
        animation: pulse 1s ease-in-out infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.85); opacity: 0.7; }
        50% { transform: scale(1.15); opacity: 1; }
        100% { transform: scale(0.85); opacity: 0.7; }
    }
    </style>
    """
