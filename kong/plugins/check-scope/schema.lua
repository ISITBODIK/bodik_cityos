-- kong/plugins/check-scope/schema.lua
local typedefs = require "kong.db.schema.typedefs"

return {
  name = "check-scope",
  fields = {
    {
      config = {
        type = "record",
        fields = {
          {
            allowed_combinations = {
              type = "array",
              elements = {
                type = "record",
                fields = {
                  { service = { type = "string" } },
                  { path = { type = "string" } },
                  { access_level = { type = "string" } },
                },
              },
            },
          },
        },
      },
    },
  },
}
