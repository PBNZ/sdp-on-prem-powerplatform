-- Request counts grouped by status. One call replaces many filtered list GETs.
SELECT sd.statusname AS status,
       COUNT(*)      AS total
FROM workorder wo
LEFT JOIN workorderstates ws ON wo.workorderid = ws.workorderid
LEFT JOIN statusdefinition sd ON ws.statusid = sd.statusid
GROUP BY sd.statusname
ORDER BY total DESC
