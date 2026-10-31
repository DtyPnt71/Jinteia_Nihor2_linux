"""Exact-build patch specification. DtyPnt71. No downloads or DLL payloads."""
import hashlib
import struct

ORIGINAL_SHA256 = 'ad0243384afa5fad82331dacfd7e45383b2a0c955fb8f99dd12e1cfd7d558438'
LEGACY_SHA256 = '4eda8ac60454c496487643d4b96ecb0f4668c2fcb9f7b3e35c46cf5785eab106'
PATCHED_SHA256 = '7b925e64a014111f80a1be831866f4d38f34c51abc35640ea87a6926716b021f'
PATCH_OFFSET = 0x4651b
HOOK = 0x1bcea
HELPER = 0x77aa0
TEXT_SIZE_OFFSET = 0x190
OLD_TEXT_SIZE = 0x76a90
OLD_HOOK = bytes.fromhex('4c8d7c082789d989d883e1f7')
# A real CALL to a leaf helper: unchanged RSP and nonvolatile registers inside
# the helper allow the standard x64 leaf unwind. Only RAX, RCX and flags change.
# Replay the original size calculation, align it, round ONLY 0x5f0 to 0x600,
# then replay the original masked flags calculation into ECX.
HELPER_CODE = bytes.fromhex(
    '488d440827'       # lea rax,[rax+rcx+0x27]
    '4883e0f0'         # and rax,-16
    '483df0050000'     # cmp rax,0x5f0
    '7504'             # jne unchanged
    '4883c010'         # add rax,16
    '89d9'             # mov ecx,ebx
    '83e1f7'           # and ecx,-9
    'c3')             # ret
NEW_HOOK = (b'\xe8' + struct.pack('<i', HELPER - HOOK - 5)
            + bytes.fromhex('4989c789d86690'))
NEW_TEXT_SIZE = HELPER + len(HELPER_CODE) - 0x1000


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checksum(data):
    work = bytearray(data)
    pe = struct.unpack_from('<I', work, 0x3c)[0]
    offset = pe + 24 + 64
    work[offset:offset + 4] = b'\0' * 4
    if len(work) % 2:
        work.append(0)
    value = sum(struct.unpack('<%dH' % (len(work) // 2), work))
    while value >> 16:
        value = (value & 0xffff) + (value >> 16)
    return offset, value + len(data)


def finish(data):
    data = bytearray(data)
    offset, value = checksum(data)
    struct.pack_into('<I', data, offset, value)
    return bytes(data)


def original_bytes(data):
    sha = digest(data)
    if sha == ORIGINAL_SHA256:
        return data
    if sha not in (LEGACY_SHA256, PATCHED_SHA256):
        raise RuntimeError('Unsupported DLL build. Requires the matching Jinteia-Proton fix. Nothing was patched.')
    result = bytearray(data)
    result[PATCH_OFFSET] = 0x0b
    if sha == PATCHED_SHA256:
        result[HOOK:HOOK + len(OLD_HOOK)] = OLD_HOOK
        result[HELPER:HELPER + len(HELPER_CODE)] = bytes(len(HELPER_CODE))
        struct.pack_into('<I', result, TEXT_SIZE_OFFSET, OLD_TEXT_SIZE)
    result = finish(result)
    if digest(result) != ORIGINAL_SHA256:
        raise RuntimeError('Original reconstruction failed verification. No DLL changes made.')
    return result


def legacy_bytes(data):
    result = bytearray(original_bytes(data))
    result[PATCH_OFFSET] = 0x0f
    result = finish(result)
    if digest(result) != LEGACY_SHA256:
        raise RuntimeError('Heap-Test1 verification failed.')
    return result


def patched_bytes(data):
    original = original_bytes(data)
    if (original[HOOK:HOOK + len(OLD_HOOK)] != OLD_HOOK
            or any(original[0x77a90:0x78000])
            or struct.unpack_from('<I', original, TEXT_SIZE_OFFSET)[0] != OLD_TEXT_SIZE
            or original[PATCH_OFFSET - 3:PATCH_OFFSET + 3] != bytes.fromhex('483dc00b0000')):
        raise RuntimeError('Unexpected machine code or PE layout. Nothing was patched.')
    result = bytearray(legacy_bytes(original))
    result[HOOK:HOOK + len(NEW_HOOK)] = NEW_HOOK
    result[HELPER:HELPER + len(HELPER_CODE)] = HELPER_CODE
    struct.pack_into('<I', result, TEXT_SIZE_OFFSET, NEW_TEXT_SIZE)
    result = finish(result)
    if digest(result) != PATCHED_SHA256:
        raise RuntimeError('Heap-Test2 checksum verification failed.')
    return result