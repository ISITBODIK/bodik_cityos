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

local FiwareAuthzHandler = {
  PRIORITY = 1000,
  VERSION = "1.0.0",
}

function FiwareAuthzHandler:access(conf)
  local method = kong.request.get_method()
  local path = kong.request.get_path()
  local fiware_service = kong.request.get_header("fiware-service")
  local fiware_servicepath = kong.request.get_header("fiware-servicepath")

  -- 全員禁止: subscriptions
  if path:match("^/v2/subscriptions") then
    kong.log.warn("Forbidden: subscriptions access is prohibited")
    return kong.response.exit(403, {status = 403, message = "Forbidden: subscriptions access is prohibited"})
  end

  -- 全員禁止: registrations
  if path:match("^/v2/registrations") then
    kong.log.warn("Forbidden: registrations access is prohibited")
    return kong.response.exit(403, {status = 403, message = "Forbidden: registrations access is prohibited"})
  end

  -- /public の read_only は JWT 不要
  local public_read_only = (fiware_servicepath:match("^/public/") and
    (method == "GET" or (method == "POST" and path:match("^/v2/op/query"))))

  if public_read_only then
    -- OK 認証不要で許可
    kong.log.warn("認証不要")
  else
    -- ここから先は JWT 必須
    local auth_header = kong.request.get_header("Authorization")
    if not auth_header then
      kong.log.warn("Missing Authorization header")
      return kong.response.exit(401, {status = 401, message = "Missing Authorization header"})
    end

    local token = auth_header:match("Bearer%s+(.+)")
    if not token then
      kong.log.warn("Invalid Authorization header format")
      return kong.response.exit(401, {status = 401, message = "Invalid Authorization header format"})
    end

    local jwt_obj = jwt:verify_jwt_obj(keycloak_pubkey, jwt:load_jwt(token))
    if not jwt_obj.verified then
      local reason = jwt_obj.reason or "unknown"
      if reason:match("expired") then
        kong.log.warn("Token expired: " ..  reason)
        return kong.response.exit(401, {status = 401, message = "Token expired"})
      else
        kong.log.warn("JWT verification failed: " .. reason)
        return kong.response.exit(401, {status = 401, message = "Invalid or malformed JWT"})
      end
    end

    local payload = jwt_obj.payload
    local scopes = payload.allowed_fiware_scopes
    local access_level = payload.access_level or "read_only"

    if type(scopes) ~= "table" then
      kong.log.warn("Forbidden: Missing or invalid scopes")
      return kong.response.exit(403, {status = 403, message = "Forbidden: Missing or invalid scopes"})
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
      return kong.response.exit(403, {status = 403, message = "Forbidden: Not authorized for this Fiware scope"})
    end

    -- アクセスレベルに応じたメソッド制御
    if access_level == "read_only" then
      if method == "GET" or (method == "POST" and path:match("^/v2/op/query")) then
        -- OK
      else
        kong.log.warn("Forbidden: Read-only access")
        return kong.response.exit(403, {status = 403, message = "Forbidden: Read-only access"})
      end
    elseif access_level == "read_write" then
      if method == "GET" or method == "POST" or method == "PUT" or method == "DELETE" then
        -- OK
      else
        kong.log.warn("Forbidden: Invalid method")
        return kong.response.exit(403, {status = 403, message = "Forbidden: Invalid method"})
      end
    else
      kong.log.warn("Forbidden: Invalid access level")
      return kong.response.exit(403, {status = 403, message = "Forbidden: Invalid access level"})
    end
  end

  -- ここまで来たら全てのチェック通過
  kong.log.warn("Authorization success: access granted")

end

return FiwareAuthzHandler
