from eth_account import Account
import secrets

private_key = "0x" + secrets.token_hex(32)
acct = Account.from_key(private_key)

print("Address:", acct.address)
print("Private Key:", private_key)