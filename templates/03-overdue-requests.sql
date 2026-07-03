-- Overdue requests. workorderstates.isoverdue is a boolean flag.
SELECT wo.workorderid AS id,
       wo.title       AS subject,
       wo.duebytime   AS due_by_epoch_ms
FROM workorder wo
JOIN workorderstates ws ON wo.workorderid = ws.workorderid
WHERE ws.isoverdue = true
ORDER BY wo.duebytime ASC
LIMIT 50
