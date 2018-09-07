import sys
from .BCDataStream import *
from .enumeration import Enumeration
from .base58 import public_key_to_bc_address, hash_160_to_bc_address
import struct

# This function comes from bitcointools, bct-LICENSE.txt.


def long_hex(bytes):
    return bytes.encode('hex_codec')

# This function comes from bitcointools, bct-LICENSE.txt.


def short_hex(bytes):
    t = bytes.encode('hex_codec')
    if len(t) < 11:
        return t
    return t[0:4]+"..."+t[-4:]


opcodes = Enumeration("Opcodes", [
    ("OP_0", 0), ("OP_PUSHDATA1",
                  76), "OP_PUSHDATA2", "OP_PUSHDATA4", "OP_1NEGATE", "OP_RESERVED",
    "OP_1", "OP_2", "OP_3", "OP_4", "OP_5", "OP_6", "OP_7",
    "OP_8", "OP_9", "OP_10", "OP_11", "OP_12", "OP_13", "OP_14", "OP_15", "OP_16",
    "OP_NOP", "OP_VER", "OP_IF", "OP_NOTIF", "OP_VERIF", "OP_VERNOTIF", "OP_ELSE", "OP_ENDIF", "OP_VERIFY",
    "OP_RETURN", "OP_TOALTSTACK", "OP_FROMALTSTACK", "OP_2DROP", "OP_2DUP", "OP_3DUP", "OP_2OVER", "OP_2ROT", "OP_2SWAP",
    "OP_IFDUP", "OP_DEPTH", "OP_DROP", "OP_DUP", "OP_NIP", "OP_OVER", "OP_PICK", "OP_ROLL", "OP_ROT",
    "OP_SWAP", "OP_TUCK", "OP_CAT", "OP_SUBSTR", "OP_LEFT", "OP_RIGHT", "OP_SIZE", "OP_INVERT", "OP_AND",
    "OP_OR", "OP_XOR", "OP_EQUAL", "OP_EQUALVERIFY", "OP_RESERVED1", "OP_RESERVED2", "OP_1ADD", "OP_1SUB", "OP_2MUL",
    "OP_2DIV", "OP_NEGATE", "OP_ABS", "OP_NOT", "OP_0NOTEQUAL", "OP_ADD", "OP_SUB", "OP_MUL", "OP_DIV",
    "OP_MOD", "OP_LSHIFT", "OP_RSHIFT", "OP_BOOLAND", "OP_BOOLOR",
    "OP_NUMEQUAL", "OP_NUMEQUALVERIFY", "OP_NUMNOTEQUAL", "OP_LESSTHAN",
    "OP_GREATERTHAN", "OP_LESSTHANOREQUAL", "OP_GREATERTHANOREQUAL", "OP_MIN", "OP_MAX",
    "OP_WITHIN", "OP_RIPEMD160", "OP_SHA1", "OP_SHA256", "OP_HASH160",
    "OP_HASH256", "OP_CODESEPARATOR", "OP_CHECKSIG", "OP_CHECKSIGVERIFY", "OP_CHECKMULTISIG",
    "OP_CHECKMULTISIGVERIFY",
    "OP_NOP1", "OP_NOP2", "OP_NOP3", "OP_NOP4", "OP_NOP5", "OP_NOP6", "OP_NOP7", "OP_NOP8", "OP_NOP9", "OP_NOP10",
    ("OP_INVALIDOPCODE", 0xFF),
])


def script_GetOp(bytes):
    i = 0
    while i < len(bytes):
        vch = None
        opcode = bytes[i]
        i += 1

        if opcode <= opcodes.OP_PUSHDATA4:
            nSize = opcode
            if opcode == opcodes.OP_PUSHDATA1:
                if i + 1 > len(bytes):
                    vch = "_INVALID_NULL"
                    i = len(bytes)
                else:
                    nSize = ord(bytes[i])
                    i += 1
            elif opcode == opcodes.OP_PUSHDATA2:
                if i + 2 > len(bytes):
                    vch = "_INVALID_NULL"
                    i = len(bytes)
                else:
                    (nSize,) = struct.unpack_from('<H', bytes, i)
                    i += 2
            elif opcode == opcodes.OP_PUSHDATA4:
                if i + 4 > len(bytes):
                    vch = "_INVALID_NULL"
                    i = len(bytes)
                else:
                    (nSize,) = struct.unpack_from('<I', bytes, i)
                    i += 4
            if i+nSize > len(bytes):
                vch = "_INVALID_"+bytes[i:]
                i = len(bytes)
            else:
                vch = bytes[i:i+nSize]
                i += nSize
        elif opcodes.OP_1 <= opcode <= opcodes.OP_16:
            vch = chr(opcode - opcodes.OP_1 + 1)
        elif opcode == opcodes.OP_1NEGATE:
            vch = chr(255)

        yield (opcode, vch)


def script_GetOpName(opcode):
    try:
        return (opcodes.whatis(opcode)).replace("OP_", "")
    except KeyError:
        return "InvalidOp_"+str(opcode)


def decode_script(bytes):
    result = ''
    for (opcode, vch) in script_GetOp(bytes):
        if len(result) > 0:
            result += " "
        if opcode <= opcodes.OP_PUSHDATA4:
            result += "%d:" % (opcode,)
            result += short_hex(vch)
        else:
            result += script_GetOpName(opcode)
    return result


def parse_TxIn(vds):
    d = {}
    d['prevout_hash'] = vds.read_bytes(32)
    d['prevout_n'] = vds.read_uint32()
    d['scriptSig'] = vds.read_bytes(vds.read_compact_size())
    d['sequence'] = vds.read_uint32()
    return d


def deserialize_TxIn(d, transaction_index=None, owner_keys=None):
    if d['prevout_hash'] == "\x00"*32:
        result = "TxIn: COIN GENERATED"
        result += " coinbase:"+d['scriptSig'].encode('hex_codec')
    elif transaction_index is not None and d['prevout_hash'] in transaction_index:
        p = transaction_index[d['prevout_hash']]['txOut'][d['prevout_n']]
        result = "TxIn: value: %f" % (p['value']/1.0e8,)
        result += " prev("+long_hex(d['prevout_hash']
                                    [::-1])+":"+str(d['prevout_n'])+")"
    else:
        result = "TxIn: prev("+long_hex(d['prevout_hash']
                                        [::-1])+":"+str(d['prevout_n'])+")"
        pk = extract_public_key(d['scriptSig'])
        #pk = 1
        result += " pubkey: "+pk
        result += " sig: "+decode_script(d['scriptSig'])
    if d['sequence'] < 0xffffffff:
        result += " sequence: "+hex(d['sequence'])
    return result


def parse_Transaction(vds, has_nTime=False):
    d = {}
    start_pos = vds.read_cursor
    d['version'] = vds.read_int32()
    if has_nTime:
        d['nTime'] = vds.read_uint32()
    n_vin = vds.read_compact_size()
    d['txIn'] = []
    for i in range(n_vin):
        d['txIn'].append(parse_TxIn(vds))
    n_vout = vds.read_compact_size()
    d['txOut'] = []
    for i in range(n_vout):
        d['txOut'].append(parse_TxOut(vds))
    d['lockTime'] = vds.read_uint32()
    d['__data__'] = vds.input[start_pos:vds.read_cursor]
    return d


def parse_TxOut(vds):
    d = {}
    d['value'] = vds.read_int64()
    d['scriptPubKey'] = vds.read_bytes(vds.read_compact_size())
    return d


def match_decoded(decoded, to_match):
    if len(decoded) != len(to_match):
        return False
    for i in range(len(decoded)):
        if to_match[i] == opcodes.OP_PUSHDATA4 and decoded[i][0] <= opcodes.OP_PUSHDATA4:
            # Opcodes below OP_PUSHDATA4 all just push data onto stack, and are equivalent.
            continue
        if to_match[i] != decoded[i][0]:
            return False
    return True


def extract_public_key(bytes, version='\x00'):
    try:
        decoded = [x for x in script_GetOp(bytes)]
    except struct.error:
        return "(None)"

    # non-generated TxIn transactions push a signature
    # (seventy-something bytes) and then their public key
    # (33 or 65 bytes) onto the stack:
    match = [opcodes.OP_PUSHDATA4, opcodes.OP_PUSHDATA4]
    if match_decoded(decoded, match):
        return public_key_to_bc_address(decoded[1][1], version=version)

    # The Genesis Block, self-payments, and pay-by-IP-address payments look like:
    # 65 BYTES:... CHECKSIG
    match = [opcodes.OP_PUSHDATA4, opcodes.OP_CHECKSIG]
    if match_decoded(decoded, match):
        return public_key_to_bc_address(decoded[0][1], version=version)

    # Pay-by-Bitcoin-address TxOuts look like:
    # DUP HASH160 20 BYTES:... EQUALVERIFY CHECKSIG
    match = [opcodes.OP_DUP, opcodes.OP_HASH160, opcodes.OP_PUSHDATA4,
             opcodes.OP_EQUALVERIFY, opcodes.OP_CHECKSIG]
    if match_decoded(decoded, match):
        return hash_160_to_bc_address(decoded[2][1], version=version)

    # BIP11 TxOuts look like one of these:
    multisigs = [
        [opcodes.OP_PUSHDATA4, opcodes.OP_PUSHDATA4,
            opcodes.OP_1, opcodes.OP_CHECKMULTISIG],
        [opcodes.OP_PUSHDATA4, opcodes.OP_PUSHDATA4,
            opcodes.OP_PUSHDATA4, opcodes.OP_2, opcodes.OP_CHECKMULTISIG],
        [opcodes.OP_PUSHDATA4, opcodes.OP_PUSHDATA4, opcodes.OP_PUSHDATA4,
            opcodes.OP_PUSHDATA4, opcodes.OP_3, opcodes.OP_CHECKMULTISIG]
    ]
    for match in multisigs:
        if match_decoded(decoded, match):
            return "["+','.join([public_key_to_bc_address(decoded[i][1]) for i in range(1, len(decoded)-1)])+"]"

    # BIP16 TxOuts look like:
    # HASH160 20 BYTES:... EQUAL
    match = [opcodes.OP_HASH160, 0x14, opcodes.OP_EQUAL]
    if match_decoded(decoded, match):
        return hash_160_to_bc_address(decoded[1][1], version="\x05")

    return "(None)"
