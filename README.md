# OPC UA File Upload + SMB Mover

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Start the OPC UA server:

```powershell
python .\opcua_chunkhexupload.py
```

Upload a file (this sets `TransferRequest` to TRUE after a successful upload):

```powershell
python .\OPC_Client.py "C:\path\to\file.gcode"
```

Run the SMB mover (waits for `TransferRequest` if enabled):

```powershell
python .\opcua_smb_mover.py
```

## Notes

- `opcua_smb_mover.py` polls the `TransferRequest` node and waits for the uploaded file to appear in `uploads` before copying to the SMB share.
- Ensure the SMB share path in `SMB_TARGET_DIR` is reachable from this machine.
