-- kong/plugins/fiware-public/handler.lua

-- プラグインのハンドラーテーブルを定義
local FiwarePublicHandler = {
    -- プラグインの実行優先度 (数値が高いほど早く実行される)
    PRIORITY = 1000,
    -- プラグインのバージョン
    VERSION = "1.0.0",
}

-- Kongのプラグインライフサイクルフェーズに対応するメソッドを定義
function FiwarePublicHandler:access(conf)
    -- conf: プラグインの設定テーブル (schema.lua で定義されたもの)

    -- 1. Fiware-Service と Fiware-ServicePath の認可
    local requested_fiware_service = kong.request.get_header("fiware-service")
    local requested_fiware_servicepath = kong.request.get_header("fiware-servicepath")
    
    kong.log.debug("Requested Fiware-Service: ", requested_fiware_service)
    kong.log.debug("Requested Fiware-ServicePath: ", requested_fiware_servicepath)

    if requested_fiware_servicepath and requested_fiware_servicepath:match("^/protected") then
        kong.log.warn("Protected Fiware-ServicePath required in /public route.")
        return kong.response.exit(403, "Bad Request: protected Fiware-ServicePath required.")
    end

end

return FiwarePublicHandler
