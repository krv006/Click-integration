import hashlib

click_trans_id = "3376634945"
service_id = "80756"
secret_key = "ALW593cHXtux"
merchant_trans_id = "5"
amount = "1000"

sign_source = click_trans_id + service_id + secret_key + merchant_trans_id + amount
sign_string = hashlib.md5(sign_source.encode()).hexdigest().lower()

print(sign_string)
