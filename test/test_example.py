import subprocess


def call(c: str):
    return subprocess.run(c, check=True, shell=True)


def test_addr():
    call('python example/addr.py --net mainnet --prikey 1')


def test_message():
    call('python example/message.py --prikey 1 --msg pybtc')
    call('python example/message.py --prikey 1 --msg pybtc --sig ICvzXjwjJVMilSGyMqwlqMTuGF6UMwddFJzVmm0Di5qNnqkBRKP8Pldm3YbOskg3ewV1tszVLy8gVX1u+qFrx6o=')


def test_taproot():
    call('python example/taproot.py')


def test_transfer():
    call('python example/transfer.py --net develop --prikey 1 --script-type p2pkh --to mg8Jz5776UdyiYcBb9Z873NTozEiADRW5H --value 0.1')
