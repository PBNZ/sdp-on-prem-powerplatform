-- Configuration items from the CMDB. Tables (build 14990): ci.
SELECT ciid       AS id,
       ciname     AS name,
       citypeid   AS ci_type_id
FROM ci
ORDER BY ciid DESC
LIMIT 25
