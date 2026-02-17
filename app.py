"""
Main Streamlit application for OPC UA File Transfer Dashboard
"""
import streamlit as st
import time
import os
import glob
from ui.components import (
    render_header,
    render_status_card,
    render_progress_bar,
    render_file_info,
    render_alert,
    render_transfer_history,
    render_connection_status
)
from ui.styles import get_custom_css
from core.opc_client import OPCFileTransferClient
from core.file_handler import FileHandler
from data.transfer_log import TransferLogger
from config.settings import REFRESH_INTERVAL

# Page configuration
st.set_page_config(
    page_title="OPC UA File Transfer Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize session state
if 'transfer_status' not in st.session_state:
    st.session_state.transfer_status = 'idle'
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'progress' not in st.session_state:
    st.session_state.progress = {'current': 0, 'total': 0}
if 'last_message' not in st.session_state:
    st.session_state.last_message = None
if 'alert_queue' not in st.session_state:
    st.session_state.alert_queue = []
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = None
if 'last_check_time' not in st.session_state:
    st.session_state.last_check_time = 0
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# Initialize logger
logger = TransferLogger()


def perform_transfer(file_path):
    """Perform the file transfer operation"""
    try:
        # Initialize components
        file_handler = FileHandler(file_path)
        opc_client = OPCFileTransferClient()
        
        # Update status
        st.session_state.transfer_status = 'in_progress'
        st.session_state.current_file = file_handler.file_info['name']
        
        # Connect to server
        success, message = opc_client.connect()
        if not success:
            raise Exception(message)
        
        # Prepare file
        file_handler.create_chunks()
        total_chunks = file_handler.get_total_chunks()
        st.session_state.progress = {'current': 0, 'total': total_chunks}
        
        # Log start
        logger.log_transfer(
            file_handler.file_info['name'],
            file_handler.file_info['size'],
            'in_progress',
            chunks_sent=0,
            total_chunks=total_chunks
        )
        
        # Open file
        success, message = opc_client.open_file(file_handler.file_info['name'])
        if not success:
            raise Exception(message)
        
        # Send chunks
        for i, chunk in enumerate(file_handler.chunks):
            success, message = opc_client.write_chunk(chunk)
            if not success:
                raise Exception(message)
            
            st.session_state.progress['current'] = i + 1
            time.sleep(0.1)  # Small delay for UI update
        
        # Close file
        success, message = opc_client.close_file()
        if not success:
            raise Exception(message)
        
        # Set transfer request
        success, message = opc_client.set_transfer_request()
        if not success:
            raise Exception(message)
        
        # Success!
        st.session_state.transfer_status = 'success'
        st.session_state.last_message = "Transfer completed successfully!"
        
        logger.log_transfer(
            file_handler.file_info['name'],
            file_handler.file_info['size'],
            'success',
            chunks_sent=total_chunks,
            total_chunks=total_chunks
        )
        
        opc_client.disconnect()
        return True
        
    except Exception as e:
        st.session_state.transfer_status = 'failed'
        st.session_state.last_message = str(e)
        
        logger.log_transfer(
            st.session_state.current_file or "Unknown",
            0,
            'failed',
            error_message=str(e),
            chunks_sent=st.session_state.progress['current'],
            total_chunks=st.session_state.progress['total']
        )
        
        if 'opc_client' in locals():
            opc_client.disconnect()
        
        return False


def main():
    """Main dashboard application"""
    
    # Render header
    render_header()
    
    # Sidebar
    with st.sidebar:
        st.header("Control Panel")
        
        # File upload with dynamic key for reset capability
        uploaded_file = st.file_uploader(
            "Upload File for Transfer",
            type=None,
            help="Select any file to transfer via OPC UA",
            key=f"file_uploader_{st.session_state.uploader_key}"
        )
        
        # Transfer button - only show if server is connected
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Check if server is connected
            if st.session_state.connection_status:
                # Custom green button with white text
                st.markdown("""
                    <style>
                    div.stButton > button {
                        background-color: #28a745;
                        color: white;
                        font-weight: bold;
                        border: none;
                        padding: 0.5rem 1rem;
                        border-radius: 5px;
                    }
                    div.stButton > button:hover {
                        background-color: #218838;
                        color: white;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                if st.button("Start Transfer", type="primary"):
                    perform_transfer(temp_path)
                    st.rerun()
            else:
                st.markdown(
                    '<p style="color: #dc3545; font-weight: bold; padding: 10px; '
                    'background-color: #f8d7da; border-radius: 5px; text-align: center;">'
                    'Please Connect to the Server First</p>',
                    unsafe_allow_html=True
                )
        
        st.markdown("---")
        
        # Clear alerts button
        if st.session_state.transfer_status in ['success', 'failed']:
            if st.button("Acknowledge and Clear"):
                st.session_state.transfer_status = 'idle'
                st.session_state.current_file = None
                st.session_state.progress = {'current': 0, 'total': 0}
                st.session_state.last_message = None
                
                # Increment uploader key to reset file uploader
                st.session_state.uploader_key += 1
                
                # Delete temporary files
                for temp_file in glob.glob("temp_*"):
                    try:
                        os.remove(temp_file)
                    except Exception:
                        pass
                
                st.rerun()
        
        st.markdown("---")
        
        # Clear history
        if st.button("Clear History"):
            logger.clear_logs()
            st.success("History cleared!")
            time.sleep(1)
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Status card
        render_status_card(
            st.session_state.transfer_status,
            st.session_state.current_file,
            st.session_state.last_message
        )
        
        # Progress bar (only during transfer)
        if st.session_state.transfer_status == 'in_progress':
            render_progress_bar(
                st.session_state.progress['current'],
                st.session_state.progress['total']
            )
    
    with col2:
        # Real connection status check (cached to avoid slowdowns)
        current_time = time.time()
        if current_time - st.session_state.last_check_time > 5:
            try:
                opc_client = OPCFileTransferClient()
                is_connected, _ = opc_client.connect()
                if is_connected:
                    opc_client.disconnect()
                st.session_state.connection_status = is_connected
            except Exception:
                st.session_state.connection_status = False
            st.session_state.last_check_time = current_time
        
        # Display current connection status
        render_connection_status(st.session_state.connection_status)
        
        # Current file info
        if st.session_state.current_file:
            latest_log = logger.get_latest_log()
            if latest_log:
                st.markdown("### Current Transfer")
                st.metric("File", latest_log['file_name'])
                st.metric("Status", latest_log['status'].title())
    
    # Transfer history
    st.markdown("---")
    logs = logger.get_all_logs()
    render_transfer_history(logs)
    
    # Auto-refresh during transfer
    if st.session_state.transfer_status == 'in_progress':
        time.sleep(REFRESH_INTERVAL)
        st.rerun()


if __name__ == "__main__":
    main()
