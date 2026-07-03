-- Requests joined to their associated assets. A single JOIN replaces many
-- per-request association GETs. Tables (build 14990): workordertoasset,
-- workorder, resources.
SELECT wta.workorderid AS request_id,
       wo.title        AS subject,
       r.resourcename  AS asset_name
FROM workordertoasset wta
JOIN workorder wo  ON wta.workorderid = wo.workorderid
JOIN resources r   ON wta.assetid     = r.resourceid
ORDER BY wta.workorderid DESC
LIMIT 25
