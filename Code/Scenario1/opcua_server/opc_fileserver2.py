import asyncio
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict

from asyncua import Server, ua, uamethod


# FILE_PATH = Path("server_storage.bin")   # file that clients will read/write
FILE_PATH = Path(r"C:\shares\program01\prg001.txt")   # CHANGE THIS
MAX_CHUNK = 64 * 1024                    # 64 KiB per Read/Write (adjust as needed)

# Simple "file handle table" (per server process).
# In a full implementation you would bind handles to session/user and enforce timeouts/locks.
_next_handle = 1
_handles: Dict[int, "HandleState"] = {}


@dataclass
class HandleState:
    mode: int          # bitmask: 1=read, 2=write (simple)
    pos: int


def _new_handle(mode: int) -> int:
    global _next_handle
    h = _next_handle
    _next_handle += 1
    _handles[h] = HandleState(mode=mode, pos=0)
    return h


def _get(h: int) -> HandleState:
    if h not in _handles:
        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidArgument)
    return _handles[h]


@uamethod
def Open(parent, mode: int) -> int:
    """
    mode: simple bitmask:
      1 = read
      2 = write
      3 = read|write
    """
    if mode not in (1, 2, 3):
        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidArgument)

    # Ensure file exists if opening for read
    if mode & 0x01 and not FILE_PATH.exists():
        # mimic "not found"
        raise ua.UaStatusCodeError(ua.StatusCodes.BadNotFound)

    # Ensure file exists if opening for write (create if missing)
    if mode & 0x02:
        FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        FILE_PATH.touch(exist_ok=True)

    return _new_handle(mode)


@uamethod
def Close(parent, fileHandle: int):
    if fileHandle not in _handles:
        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidArgument)
    del _handles[fileHandle]
    return


@uamethod
def GetPosition(parent, fileHandle: int) -> int:
    st = _get(fileHandle)
    return int(st.pos)


@uamethod
def SetPosition(parent, fileHandle: int, position: int):
    st = _get(fileHandle)
    if position < 0:
        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidArgument)
    st.pos = int(position)
    return


@uamethod
def Read(parent, fileHandle: int, length: int) -> bytes:
    st = _get(fileHandle)
    if not (st.mode & 0x01):
        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidState)
    if length <= 0:
        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidArgument)

    length = min(int(length), MAX_CHUNK)

    with FILE_PATH.open("rb") as f:
        f.seek(st.pos, os.SEEK_SET)
        data = f.read(length)
        st.pos += len(data)
        return data  # returned as OPC UA ByteString


@uamethod
def Write(parent, fileHandle: int, data: bytes):
    st = _get(fileHandle)
    if not (st.mode & 0x02):
        raise ua.UaStatusCodeError(ua.StatusCodes.BadInvalidState)

    if data is None:
        data = b""

    # Optional: enforce chunk size limit
    if len(data) > MAX_CHUNK:
        raise ua.UaStatusCodeError(ua.StatusCodes.BadOutOfRange)

    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FILE_PATH.touch(exist_ok=True)

    with FILE_PATH.open("r+b") as f:
        f.seek(st.pos, os.SEEK_SET)
        f.write(data)
        st.pos += len(data)

    return


async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/filetype/server/")
    server.set_server_name("Python FileType-like Server (Part20-style)")

    uri = "urn:example:filetype"
    idx = await server.register_namespace(uri)

    # AddressSpace layout similar to: Objects -> FileSystem -> MyFile
    objects = server.nodes.objects
    fs = await objects.add_folder(idx, "FileSystem")
    fileobj = await fs.add_object(idx, "MyFile")

    # Basic properties (optional but useful)
    size_var = await fileobj.add_variable(idx, "Size", ua.UInt64(0))
    writable_var = await fileobj.add_variable(idx, "Writable", True)
    open_count_var = await fileobj.add_variable(idx, "OpenCount", ua.UInt16(0))
    for v in (size_var, writable_var, open_count_var):
        await v.set_writable(False)

    # Methods (signatures mirror Part 20 concepts)
    await fileobj.add_method(idx, "Open", Open,
                             [ua.VariantType.Byte], [ua.VariantType.UInt32])
    await fileobj.add_method(idx, "Close", Close,
                             [ua.VariantType.UInt32], [])
    await fileobj.add_method(idx, "Read", Read,
                             [ua.VariantType.UInt32, ua.VariantType.Int32],
                             [ua.VariantType.ByteString])
    await fileobj.add_method(idx, "Write", Write,
                             [ua.VariantType.UInt32, ua.VariantType.ByteString], [])
    await fileobj.add_method(idx, "GetPosition", GetPosition,
                             [ua.VariantType.UInt32], [ua.VariantType.UInt64])
    await fileobj.add_method(idx, "SetPosition", SetPosition,
                             [ua.VariantType.UInt32, ua.VariantType.UInt64], [])

    async with server:
        while True:
            # Update some properties periodically
            if FILE_PATH.exists():
                await size_var.write_value(ua.UInt64(FILE_PATH.stat().st_size))
            await open_count_var.write_value(ua.UInt16(len(_handles)))
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
