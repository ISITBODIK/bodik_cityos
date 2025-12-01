curl -X POST https://cityos.bodik.jp:8087/services/xxxxx/plugins \
  --data "name=jwt" \
  --data "config.claims_to_verify=exp" \
  --data "config.key_claim_name=iss" \
  --data "config.secret_is_base64=false" \
  --data "consumer.id=xxxx"
