curl -X PATCH https://cityos.bodik.jp:8087/plugins/xxxxx \
  --data "config.allowed_combinations[1].service=bodik" \
  --data "config.allowed_combinations[1].path=/protected/forest" \
  --data "config.allowed_combinations[1].access_level=read_only" \
  --data "config.allowed_combinations[2].service=bodik" \
  --data "config.allowed_combinations[2].path=/protected/municipality" \
  --data "config.allowed_combinations[2].access_level=read_only" \
  --data "config.allowed_combinations[3].service=bodik" \
  --data "config.allowed_combinations[3].path=/protected/elementary" \
  --data "config.allowed_combinations[3].access_level=read_only"
