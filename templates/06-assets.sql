-- Assets from the asset inventory. Tables (build 14990): resources.
SELECT resourceid   AS id,
       resourcename AS name,
       assettag     AS asset_tag
FROM resources
ORDER BY resourceid DESC
LIMIT 25
