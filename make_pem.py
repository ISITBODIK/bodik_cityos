x5c_str = ""
pem = f"-----BEGIN CERTIFICATE-----\n{x5c_str}\n-----END CERTIFICATE-----\n"

with open("keycloak_cert.pem", "w") as f:
    f.write(pem)

