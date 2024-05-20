import subprocess


def test_addr():
    subprocess.run('python example/addr.py --net mainnet --prikey 1', check=True, shell=True)


def test_taproot():
    subprocess.run('python example/taproot.py', check=True, shell=True)


def test_transfer():
    subprocess.run('python example/transfer.py --net develop --prikey 1 --script-type p2pkh --to mg8Jz5776UdyiYcBb9Z873NTozEiADRW5H --value 0.1', check=True, shell=True)
