-- Capability probe. Run this once at setup: if it returns a row, the Execute
-- Query API is enabled for this connection (permission + edition + build).
-- If it errors, fall back to the REST connectors.
SELECT 1 AS test
