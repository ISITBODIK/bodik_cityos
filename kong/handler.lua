-- kong/plugins/fiware-authz/handler.lua

-- Kong 3.x 以降の PDK (Plugin Development Kit) を使用
local PDK = require "kong.pdk"
local json = require "cjson" -- JSON操作のためにcjsonライブラリを使用

-- プラグインのハンドラーテーブルを定義
local FiwareAuthzHandler = {
    -- プラグインの実行優先度 (数値が高いほど早く実行される)
    PRIORITY = 1000,
    -- プラグインのバージョン
    VERSION = "1.0.0",
}

-- Kongのプラグインライフサイクルフェーズに対応するメソッドを定義
function FiwareAuthzHandler:access(conf)
    -- conf: プラグインの設定テーブル (schema.lua で定義されたもの)

    -- kong.ctx.shared は、他のプラグインとデータを共有するためのコンテキスト
    -- local jwt_payload = PDK.ctx.shared.jwt_token
    -- JWTプラグインが設定した認証情報を取得
    -- local jwt_payload = PDK.plugin.get_context("jwt", "payload")
    -- local jwt_payload = PDK.ctx.shared.jwt_payload

    local jwt_payload = nil
    
    -- JWTプラグインが認証に成功したコンシューマをチェック
    -- authenticated_entityが設定されていれば、JWT認証は成功している
    if kong.ctx.authenticated_entity and kong.ctx.authenticated_entity.jwt_credentials then
      -- JWTクレデンシャルから、JWTのペイロードを取得する
      -- この部分は、JWTプラグインの実装に依存するため、
      -- 環境によって異なる可能性がある
      -- 暫定的に、kong.ctx.shared から取得を試みる
      jwt_payload = kong.ctx.shared.jwt_payload
    end

    if not jwt_payload then
        PDK.log.warn("Forbidden: JWT not found or invalid.")
        -- ログに詳細情報を出力してデバッグを容易にする
        PDK.log.debug("Debug: Shared context keys: " .. json.encode(PDK.ctx.shared))
        return PDK.response.exit(403, "Forbidden: JWT not found or invalid.")
    end

    -- 1. Fiware-Service と Fiware-ServicePath の認可
    local request_fiware_service = PDK.request.get_header("fiware-service")
    local request_fiware_service_path = PDK.request.get_header("fiware-servicepath")
    local allowed_fiware_scopes = jwt_payload.allowed_fiware_scopes -- KeycloakのJWTクレーム名

    PDK.log.debug("Requested Fiware-Service: ", request_fiware_service)
    PDK.log.debug("Requested Fiware-ServicePath: ", request_fiware_service_path)
    PDK.log.debug("Allowed Fiware Scopes from JWT: ", json.encode(allowed_fiware_scopes))

    if not request_fiware_service or not request_fiware_service_path then
        PDK.log.warn("Missing Fiware-Service or Fiware-ServicePath header.")
        return PDK.response.exit(400, "Bad Request: Missing Fiware-Service or Fiware-ServicePath header.")
    end

    if type(allowed_fiware_scopes) ~= "table" then
        PDK.log.warn("JWT payload does not contain 'allowed_fiware_scopes' claim or it's not a table.")
        return PDK.response.exit(403, "Forbidden: Missing or invalid Fiware scopes in token.")
    end

    local is_fiware_scope_allowed = false
    for _, allowed_scope in ipairs(allowed_fiware_scopes) do
        if type(allowed_scope) == "table" and
            allowed_scope.service == request_fiware_service and
            allowed_scope.service_path == request_fiware_service_path then
            is_fiware_scope_allowed = true
            break
        end
    end

    if not is_fiware_scope_allowed then
        PDK.log.warn("Unauthorized Fiware-Service/ServicePath combination: %s/%s", request_fiware_service, request_fiware_service_path)
        return PDK.response.exit(403, "Forbidden: Not authorized for this Fiware Service/ServicePath combination.")
    end

    -- 2. データ更新/参照の区別 (HTTPメソッドとパスに基づく認可)
    local access_level = jwt_payload.access_level -- KeycloakのJWTクレーム名
    local method = PDK.request.get_method()
    local path = PDK.request.get_path() -- リクエストパスも取得

    PDK.log.debug("Requested Method: ", method)
    PDK.log.debug("Requested Path: ", path)
    PDK.log.debug("Access Level from JWT: ", access_level)

    if access_level == "read_only" then
        if method == "GET" then
            PDK.log.debug("User has read_only access, GET method is permitted.")
        elseif method == "POST" and path:match("^/protected/v2/op/query") then
            PDK.log.debug("User has read_only access, POST /v2/op/query is permitted for search.")
        else
            PDK.log.warn("User has read_only access but attempted write method: %s on path: %s", method, path)
            return PDK.response.exit(403, "Forbidden: Read-only access allowed. Method '" .. method .. "' on path '" .. path .. "' is not permitted.")
        end
    elseif access_level == "read_write" then
        PDK.log.debug("User has read_write access, method %s on path %s is permitted.", method, path)
    else
        PDK.log.warn("Unknown access_level '%s' in JWT for consumer.", access_level)
        return PDK.response.exit(403, "Forbidden: Invalid access level configured.")
    end

end

-- プラグインハンドラーオブジェクトを Kong に登録
-- Kong 3.x で PDK.plugin.new や kong.plugin.new が機能しない場合、
-- 単にハンドラーテーブルを返すことでプラグインがロードされるか試す

-- return kong.plugin.new(FiwareAuthzHandler, "fiware-authz")
return FiwareAuthzHandler
