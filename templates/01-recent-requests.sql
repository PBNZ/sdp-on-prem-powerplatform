-- Most recent requests with status. Replaces GET /requests for reporting.
-- Tables (build 14990): workorder, workorderstates, statusdefinition.
SELECT wo.workorderid   AS id,
       wo.title         AS subject,
       sd.statusname    AS status,
       wo.createdtime   AS created_epoch_ms
FROM workorder wo
LEFT JOIN workorderstates ws ON wo.workorderid = ws.workorderid
LEFT JOIN statusdefinition sd ON ws.statusid = sd.statusid
ORDER BY wo.workorderid DESC
LIMIT 20
