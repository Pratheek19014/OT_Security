from opcua import Client

client = Client("opc.tcp://0.0.0.0:4840/")
client.connect()

# Browse to your FileType node
file_node = client.get_node("ns=2;i=1234")  # Replace with actual node ID

# Open the file in read mode
handle = file_node.call_method("2:Open", 1)  # 1 = Read

# Get file size
file_size = file_node.get_child("2:Size").get_value()

# Read the file in chunks
chunk_size = 4096
data = bytearray()
position = 0
while position < file_size:
    bytes_to_read = min(chunk_size, file_size - position)
    chunk = file_node.call_method("2:Read", handle, bytes_to_read)
    data.extend(chunk)
    position += len(chunk)

# Close the file
file_node.call_method("2:Close", handle)

# Save to local disk
with open("downloaded_file.bin", "wb") as f:
    f.write(data)

client.disconnect()
