"""
Reusable UI components for the dashboard
"""
import streamlit as st
from datetime import datetime
from utils.helpers import format_file_size, format_timestamp


def render_header():
    """Render dashboard header"""
    st.title("SMB File Transfer")
    st.markdown("**Transfer files securely**")
    st.markdown("---")



def render_status_card(status, file_name=None, message=None):
    """Render status card with current transfer state"""
    
    status_config = {
        "idle": {
            "color": "status-idle",
            "icon": "",
            "title": "System is Ready to Transfer",
            "description": "No active transfer"
        },
        "in_progress": {
            "color": "status-progress",
            "icon": "",
            "title": "Transfer In Progress",
            "description": f"Transferring: {file_name}"
        },
        "success": {
            "color": "status-success",
            "icon": "",
            "title": "Transfer Successful",
            "description": f"File: {file_name}"
        },
        "failed": {
            "color": "status-error",
            "icon": "",
            "title": "Transfer Failed",
            "description": f"File: {file_name}"
        }
    }
    
    config = status_config.get(status, status_config["idle"])
    
    st.markdown(f"""
    <div class="status-card {config['color']}">
        <h2 style="color: #000000;">{config['title']}</h2>
        <p style="font-size: 1.1rem; margin: 0.5rem 0; color: #333;">{config['description']}</p>
        {f'<p style="margin: 0; color: #666;">{message}</p>' if message else ''}
    </div>
    """, unsafe_allow_html=True)



def render_progress_bar(current, total, label="Transfer Progress"):
    """Render progress bar for file transfer"""
    progress = current / total if total > 0 else 0
    percentage = int(progress * 100)
    
    st.markdown(f"### {label}")
    st.progress(progress)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Chunks Sent", f"{current}/{total}")
    with col2:
        st.metric("Progress", f"{percentage}%")
    with col3:
        st.metric("Remaining", f"{total - current}")


def render_file_info(file_info):
    """Render file information card"""
    st.markdown("### File Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("File Name", file_info.get("name", "N/A"))
    
    with col2:
        st.metric("File Size", file_info.get("size_formatted", "N/A"))
    
    with col3:
        st.metric("File Type", file_info.get("extension", "N/A"))


def render_alert(message, alert_type="success"):
    """Render alert message"""
    alert_class = f"alert-{alert_type}"
    icon = "SUCCESS" if alert_type == "success" else "ERROR"
    
    st.markdown(f"""
    <div class="{alert_class}">
        <strong>{icon}: {message}</strong>
    </div>
    """, unsafe_allow_html=True)


def render_transfer_history(logs):
    """Render transfer history table"""
    if not logs:
        st.info("No transfer history available")
        return
    
    st.markdown("### Transfer History")
    
    # Convert logs to display format
    display_data = []
    for log in logs[:10]:  # Show last 10
        status_text = "Success" if log["status"] == "success" else "Failed"
        
        # Get error message if transfer failed
        error_msg = log.get("error_message", "-")
        if log["status"] == "success":
            error_msg = "-"
        elif error_msg is None:
            error_msg = "Unknown error"
        
        display_data.append({
            "Timestamp": datetime.fromisoformat(log["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
            "File Name": log["file_name"],
            "Size": format_file_size(log["file_size"]),
            "Status": status_text,
            "Chunks": f"{log.get('chunks_sent', 0)}/{log.get('total_chunks', 0)}" if log.get('total_chunks') else "N/A",
            "Error Message": error_msg
        })
    
    st.table(display_data)



def render_connection_status(connected):
    """Render OPC UA connection status indicator"""
    if connected:
        st.success("Connected to the Server")
    else:
        st.error("Not Connected to the Server")
