# SDP – CMDB (v1 legacy) connector

Power Platform custom connector for the **legacy XML CMDB API** of ManageEngine ServiceDesk Plus
On-Premises. This exists for **builds below 15100**, where the CMDB v3 JSON API (and its
`assoc_ci_relationships` endpoint) is unavailable. On build 15100+, prefer **SDP – Assets & CMDB
(v3)**. 4 operations. Hand-authored (the V1 API's auth/format differ too much for the shared
generator).

## What's different about V1

| Aspect | V1 (this connector) | V3 (other connectors) |
|---|---|---|
| Base path | `/api/cmdb/...` | `/api/v3/...` |
| Auth | `TECHNICIAN_KEY` **query parameter** | `authtoken` **header** |
| Write payload | **XML** in the `INPUT_DATA` form field | JSON in `input_data` |
| Response | `{ API: { response: { operation: { result, Details } } } }` | `{ response_status, ... }` |
| Success | `result.statuscode` **200** | `response_status.status_code` **2000** |

The `TECHNICIAN_KEY` is the **same secret** as the V3 `authtoken`. Because it travels in the URL,
**HTTPS is mandatory** — model it as a secured parameter (this connector does) and scope the key
tightly.

## Operations

| Operation | Method | Path | Notes |
|---|---|---|---|
| List all CIs | GET | `/cmdb/ci/list/all` | Verified live. |
| Count all CIs | GET | `/cmdb/ci/count/all` | Verified live. |
| Get CI relationships | GET | `/cmdb/cirelationships/{ci_name}` | All relationships for a CI (name is case-sensitive). |
| Modify CI relationships | POST | `/cmdb/cirelationships` | Add or delete via the XML `INPUT_DATA` payload. |

**Verification note:** *List/Count all CIs* were verified live (HTTP 200, `statuscode` 200) on the
public demo. The **relationship** operations are modeled from a working V1 client (in a
companion project of the author's — private, not published) and the official
CMDB v1↔v3 comparison; on the 15100+ demo the V1 relationship endpoint is superseded by V3, so
verify them on an actual sub-15100 instance.

## Relationship payloads (XML in `INPUT_DATA`)

**Add** a relationship:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<API version="1.0" locale="en">
  <records><relationships>
    <addrelationship>
      <toci>CI-A</toci>
      <relationshiptype>Depends on</relationshiptype>
      <relatedcis>
        <citype>Windows Server</citype>
        <ci><name>CI-B</name></ci>
      </relatedcis>
    </addrelationship>
  </relationships></records>
</API>
```

**Delete** a relationship:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<API version="1.0" locale="en">
  <relationships>
    <deleterelationship>
      <fromci>CI-A</fromci>
      <relationshiptype>Depends on</relationshiptype>
      <relatedcis><ci>CI-B</ci></relatedcis>
    </deleterelationship>
  </relationships>
</API>
```

To filter *Get CI relationships* by type or find the relationship between two CIs, the V1 API
uses sub-paths (`cirelationships/{ci}/{relationship_type}` and `cirelationships/{ci}<->{other}`);
those aren't exposed as separate operations here (awkward path characters) — add them if needed.

## Setup

Import `apiDefinition.swagger.json`, set the **Host** to your SDP server, create a connection and
paste the technician key (stored as a secured `TECHNICIAN_KEY` query parameter).
