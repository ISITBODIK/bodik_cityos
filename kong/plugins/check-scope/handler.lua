local cjson = require "cjson.safe"
local jwt = require "resty.jwt"

local function load_public_key(path)
  local f = io.open(path, "r")
  if not f then
    kong.log.err('failed to open public key file:' .. path)
    return nil
  end
  local key = f:read("*all")
  f:close()
  return key
end

local keycloak_pubkey = load_public_key("/etc/secrets/keycloak_pub.pem")

local CheckScope = {
  VERSION = "1.2.0",
  PRIORITY = 1000,
}

function CheckScope:access(conf)
  -- デバッグのため、処理開始を報告する
  kong.log.warn("CheckScopeプラグイン開始")

  -- リクエストヘッダーから取得
  local fiware_service = kong.request.get_header("fiware-service")
  local fiware_servicepath = kong.request.get_header("fiware-servicepath")

  -- JWT取得
  local auth_header = kong.request.get_header("authorization")
  if not auth_header then
    kong.log.warn("Missing Authorization header")
    return kong.response.exit(401, { message = "Missing Authorization header" })
  end
  local token = auth_header:match("Bearer%s+(.+)")
  if not token then
    kong.log.warn("Invalid Authorization header")
    return kong.response.exit(401, { message = "Invalid Authorization header" })
  end

  -- JWT検証（公開鍵URL）
  -- local jwt_obj = jwt:verify(conf.jwk_url, token)
  local jwt_obj = jwt:verify_jwt_obj(keycloak_pubkey, jwt:load_jwt(token))
  if not jwt_obj.verified then
    kong.log.warn("Invalid JWT token")
    return kong.response.exit(401, { message = "Invalid JWT token" })
  end

  local payload = jwt_obj.payload
  local scopes = payload.allowed_fiware_scopes
  local access_level = payload.access_level or "read_only"

  -- 1. JWT内とリクエストヘッダーの一致確認
  if not (type(scopes) == "table" and #scopes > 0) then
    kong.log.warn("Forbidden: Missing or invalid scopes")
    return kong.response.exit(403, { message = "Forbidden: Missing or invalid scopes"})
  end

  -- スコープ検証
  local scope_ok = false
  for _, s in ipairs(scopes) do
    if type(s) == "table" and
      s["fiware-service"] == fiware_service and
      s["fiware-servicepath"] == fiware_servicepath then
      scope_ok = true
      break
    end
  end

  if not scope_ok then
    kong.log.warn("Forbidden: Not authorized for this Fiware scope")
    return kong.response.exit(403, { message = "Forbidden: Not authorized for this Fiware scope"})
  end

  -- 2. プラグイン設定の組み合わせとaccess_levelチェック
  local is_allowed = false
  for _, combo in ipairs(conf.allowed_combinations or {}) do
    if fiware_service == combo.service and fiware_servicepath == combo.path then
      -- access_levelも一致しているか確認
      if access_level == combo.access_level then
        is_allowed = true
        break
      end
    end
  end

  if not is_allowed then
    return kong.response.exit(403, { message = "Forbidden (access level mismatch)" })
  end
end

return CheckScope
