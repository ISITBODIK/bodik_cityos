FROM fiware/orion

HEALTHCHECK --interval=60s --timeout=5s --start-period=10s CMD curl --insecure --fail https://localhost:1026/v2/entities?limit=1 || exit 1

