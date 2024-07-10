op_0 = 0x00
op_pushdata1 = 0x4c
op_pushdata2 = 0x4d
op_pushdata4 = 0x4e
op_1_negate = 0x4f
op_1 = 0x51
op_nop = 0x61
op_if = 0x63
op_notif = 0x64
op_else = 0x67
op_endif = 0x68
op_verify = 0x69
op_return = 0x6a
op_toaltstack = 0x6b
op_fromaltstack = 0x6c
op_2drop = 0x6d
op_2dup = 0x6e
op_3dup = 0x6f
op_2over = 0x70
op_2rot = 0x71
op_2swap = 0x72
op_ifdup = 0x73
op_depth = 0x74
op_drop = 0x75
op_dup = 0x76
op_nip = 0x77
op_over = 0x78
op_pick = 0x79
op_roll = 0x7a
op_rot = 0x7b
op_swap = 0x7c
op_tuck = 0x7d
op_size = 0x82
op_equal = 0x87
op_equalverify = 0x88
op_1add = 0x8b
op_1sub = 0x8c
op_negate = 0x8f
op_abs = 0x90
op_not = 0x91
op_0notequal = 0x92
op_add = 0x93
op_sub = 0x94
op_booland = 0x9a
op_boolor = 0x9b
op_numequal = 0x9c
op_numequalverify = 0x9d
op_numnotequal = 0x9e
op_lessthan = 0x9f
op_greaterthan = 0xa0
op_lessthanorequal = 0xa1
op_greaterthanorequal = 0xa2
op_min = 0xa3
op_max = 0xa4
op_within = 0xa5
op_ripemd160 = 0xa6
op_sha1 = 0xa7
op_sha256 = 0xa8
op_hash160 = 0xa9
op_hash256 = 0xaa
op_codeseparator = 0xab
op_checksig = 0xac
op_checksigverify = 0xad
op_checkmultisig = 0xae
op_checkmultisigverify = 0xaf
op_checklocktimeverify = 0xb1
op_checksequenceverify = 0xb2
op_checksigadd = 0xba


def op_pushdata(data: bytearray) -> bytearray:
    l = len(data)
    if l < 0x4c:
        return bytearray([l]) + data
    if l < 0xff:
        return bytearray([op_pushdata1, l]) + data
    if l < 0xffff:
        return bytearray([op_pushdata2]) + bytearray(l.to_bytes(2, 'little')) + data
    if l < 0xffffffff:
        return bytearray([op_pushdata4]) + bytearray(l.to_bytes(4, 'little')) + data
    raise Exception


def op_n(n: int) -> int:
    assert n >= 0
    assert n <= 16
    if n == 0:
        return op_0
    else:
        return op_1 + n - 1
