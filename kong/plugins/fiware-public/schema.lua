-- kong/plugins/fiware-public/schema.lua
local typedefs = require "kong.db.schema.typedefs"

return {
  name = "fiware-public",
  fields = {
    -- 最小限のスキーマ
    { config = {
        type = "record",
        fields = {}, -- 空のレコードであることを明示
      },
    },
  },
}