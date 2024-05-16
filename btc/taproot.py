import btc
import typing


class Leaf:
    def __init__(self, script: bytearray):
        data = bytearray()
        data.append(0xc0)
        data.extend(btc.core.compact_size_encode(len(script)))
        data.extend(script)
        self.hash = btc.core.hashtag('TapLeaf', data)
        self.script = script


class Node:
    def __init__(self, l: typing.Self | Leaf, r: typing.Self | Leaf):
        if l.hash < r.hash:
            self.hash = btc.core.hashtag('TapBranch', l.hash + r.hash)
        else:
            self.hash = btc.core.hashtag('TapBranch', r.hash + l.hash)
        self.l = l
        self.r = r
