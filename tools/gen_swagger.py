#!/usr/bin/env python3
"""
Generate the SDP Power Platform connector Swagger 2.0 definitions from a
curated, hand-written operation spec.

This is NOT a mechanical Postman conversion (see ADR-0001). The operation
tables below are hand-authored from live-verified SDP behaviour and a companion
(private) MCP project's endpoint inventory. The generator only removes repetition: every
SDP list/get/create/update op shares the same input_data envelope, authtoken
header, and response shape, so we describe each op in a few lines and let the
generator stamp the boilerplate identically. Review the generated JSON — it is
the committed artifact.

Run:  python tools/gen_swagger.py
Emits connectors/<name>/apiDefinition.swagger.json for each connector defined
in CONNECTORS at the bottom.
"""
import json
import os

ACCEPT = "application/vnd.manageengine.sdp.v3+json"
RAW_URL = ("https://raw.githubusercontent.com/PBNZ/sdp-on-prem-powerplatform"
           "/main/connectors/{}/apiDefinition.swagger.json")
DOC_URL = ("https://github.com/PBNZ/sdp-on-prem-powerplatform"
           "/blob/main/connectors/{}/actions/{}.md")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def kebab(op_id):
    """AddRequestNote -> add-request-note. 'CI'/'CIs' count as one word so
    ListCIsByType -> list-cis-by-type (shared with gen_action_docs.py)."""
    s = op_id.replace("CIs", "Cis").replace("CI", "Ci")
    return "".join(
        ("-" if i and not s[i - 1].isupper() and c.isupper() else "") + c.lower()
        for i, c in enumerate(s))


def action_doc_url(connector, op_id):
    """Human-facing per-action doc page (blob URL renders the markdown;
    the raw-vs-blob trap only applies to definition *imports*)."""
    return DOC_URL.format(connector, kebab(op_id))


# --- shared building blocks -------------------------------------------------

def accept_ref():
    return {"$ref": "#/parameters/AcceptHeader"}


def input_data_query(default=None, desc=None, required=False):
    p = {
        "name": "input_data",
        "in": "query",
        "type": "string",
        "required": required,
        "x-ms-summary": "Input Data (JSON)",
        "x-ms-visibility": "important",
        "description": desc or "SDP input_data envelope as a JSON string.",
    }
    if default is not None:
        p["default"] = default
    return p


def input_data_form(desc, required=True):
    return {
        "name": "input_data",
        "in": "formData",
        "type": "string",
        "required": required,
        "x-ms-summary": "Input Data (JSON)",
        "x-ms-visibility": "important",
        "description": desc,
    }


def path_param(name, summary, desc):
    return {
        "name": name,
        "in": "path",
        "type": "string",
        "required": True,
        "x-ms-summary": summary,
        "description": desc,
    }


def ok(desc, schema_ref=None):
    r = {"description": desc}
    if schema_ref:
        r["schema"] = {"$ref": "#/definitions/" + schema_ref}
    return r


def err():
    return {"description": "SDP error envelope (response_status.status_code != 2000)."}


def op(op_id, summary, description, params, responses, consumes=None):
    o = {
        "operationId": op_id,
        "summary": summary,
        "description": description,
        "parameters": params,
        "responses": responses,
    }
    if consumes:
        o["consumes"] = consumes
    return o


# --- op factories for the repeating SDP patterns ----------------------------

def list_op(op_id, summary, description, default_input, resp_ref):
    return op(
        op_id, summary, description,
        [input_data_query(default_input, description + " Uses the list_info envelope."), accept_ref()],
        {"200": ok(summary + " returned.", resp_ref), "default": err()},
    )


def get_op(op_id, summary, description, id_param, id_summary, resp_ref, use_input=False):
    params = [path_param(id_param, id_summary, id_summary + ".")]
    if use_input:
        params.append(input_data_query(desc="Optional input_data envelope as a JSON string."))
    params.append(accept_ref())
    return op(op_id, summary, description, params,
              {"200": ok(summary + " returned.", resp_ref), "default": err()})


def create_op(op_id, summary, description, example, resp_ref, extra_path=None):
    params = list(extra_path or [])
    params.append(input_data_form(description + " Example: " + example))
    params.append(accept_ref())
    return op(op_id, summary, description, params,
              {"201": ok(summary + " created.", resp_ref),
               "200": ok(summary + " created (builds returning 200).", resp_ref),
               "default": err()},
              consumes=["application/x-www-form-urlencoded"])


def update_op(op_id, summary, description, id_param, id_summary, example, resp_ref):
    return op(
        op_id, summary, description,
        [path_param(id_param, id_summary, id_summary + "."),
         input_data_form(description + " Example: " + example),
         accept_ref()],
        {"200": ok(summary + " updated.", resp_ref), "default": err()},
        consumes=["application/x-www-form-urlencoded"],
    )


def delete_op(op_id, summary, description, id_param, id_summary):
    return op(
        op_id, summary, description,
        [path_param(id_param, id_summary, id_summary + "."), accept_ref()],
        {"200": ok(summary + " done."), "204": ok("Deleted."), "default": err()},
    )


# --- assemble a connector from an ops list ----------------------------------

def build(title, description, base_path, ops, definitions):
    """ops: list of (path, method, op_object). Merges methods per path."""
    paths = {}
    for path, method, o in ops:
        paths.setdefault(path, {})[method] = o
    return {
        "swagger": "2.0",
        "info": {
            "title": title,
            "description": description,
            "version": "0.3.0",
            "contact": {"name": "PBNZ", "url": "https://github.com/PBNZ/sdp-on-prem-powerplatform"},
        },
        "host": "sdp.example.com",
        "basePath": base_path,
        "schemes": ["https"],
        "produces": ["application/json"],
        "securityDefinitions": {"api_key": {"type": "apiKey", "in": "header", "name": "authtoken"}},
        "security": [{"api_key": []}],
        "paths": paths,
        "parameters": {
            "AcceptHeader": {
                "name": "Accept", "in": "header", "type": "string", "required": True,
                "default": ACCEPT, "x-ms-summary": "Accept", "x-ms-visibility": "internal",
                "description": "SDP V3 media type; leave the default.",
            }
        },
        "definitions": definitions,
    }


# --- shared response definitions --------------------------------------------

def common_defs():
    name = {"type": "object", "properties": {
        "id": {"type": "string", "x-ms-summary": "ID"},
        "name": {"type": "string", "x-ms-summary": "Name"}}}
    user = {"type": "object", "properties": {
        "id": {"type": "string", "x-ms-summary": "ID"},
        "name": {"type": "string", "x-ms-summary": "Name"},
        "email_id": {"type": "string", "x-ms-summary": "Email"}}}
    time = {"type": "object", "properties": {
        "display_value": {"type": "string", "x-ms-summary": "Display Value"},
        "value": {"type": "string", "x-ms-summary": "Value (epoch ms)"}}}
    status = {"description": "SDP status envelope (object or array by build); success has status_code 2000.",
              "x-ms-summary": "Response Status"}
    list_info = {"type": "object", "x-ms-summary": "List Info", "properties": {
        "has_more_rows": {"type": "boolean", "x-ms-summary": "Has More Rows"},
        "start_index": {"type": "integer", "x-ms-summary": "Start Index"},
        "row_count": {"type": "integer", "x-ms-summary": "Row Count"},
        "total_count": {"type": "integer", "x-ms-summary": "Total Count"}}}
    return name, user, time, status, list_info


def ref(n):
    return {"$ref": "#/definitions/" + n}


def list_envelope(list_key, item_ref):
    return {"type": "object", "properties": {
        "response_status": ref("ResponseStatus"),
        "list_info": ref("ListInfo"),
        list_key: {"type": "array", "x-ms-summary": list_key.replace("_", " ").title(),
                   "items": ref(item_ref)}}}


def single_envelope(key, item_ref):
    return {"type": "object", "properties": {
        "response_status": ref("ResponseStatus"),
        key: ref(item_ref)}}


# ---------------------------------------------------------------------------
# SDP – Service Desk connector
# ---------------------------------------------------------------------------

def service_desk():
    name, user, time, status, list_info = common_defs()
    defs = {
        "SdpName": name, "SdpUser": user, "SdpTime": time,
        "ResponseStatus": status, "ListInfo": list_info,
        "RequestSummary": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Request ID"},
            "subject": {"type": "string", "x-ms-summary": "Subject"},
            "status": ref("SdpName"), "priority": ref("SdpName"),
            "created_time": ref("SdpTime"), "requester": ref("SdpUser"),
            "technician": ref("SdpUser"), "group": ref("SdpName"), "site": ref("SdpName"),
            "due_by_time": ref("SdpTime"), "is_overdue": {"type": "boolean", "x-ms-summary": "Is Overdue"}}},
        "RequestDetail": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Request ID"},
            "subject": {"type": "string", "x-ms-summary": "Subject"},
            "description": {"type": "string", "x-ms-summary": "Description"},
            "status": ref("SdpName"), "priority": ref("SdpName"), "request_type": ref("SdpName"),
            "created_time": ref("SdpTime"), "due_by_time": ref("SdpTime"),
            "requester": ref("SdpUser"), "technician": ref("SdpUser"),
            "group": ref("SdpName"), "site": ref("SdpName")}},
        "ChangeSummary": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Change ID"},
            "title": {"type": "string", "x-ms-summary": "Title"},
            "status": ref("SdpName"), "priority": ref("SdpName"), "change_type": ref("SdpName"),
            "stage": ref("SdpName"), "created_time": ref("SdpTime"),
            "change_owner": ref("SdpUser"), "group": ref("SdpName"), "site": ref("SdpName")}},
        "ProblemSummary": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Problem ID"},
            "title": {"type": "string", "x-ms-summary": "Title"},
            "status": ref("SdpName"), "priority": ref("SdpName"),
            "created_time": ref("SdpTime"), "technician": ref("SdpUser")}},
        "SolutionSummary": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Solution ID"},
            "title": {"type": "string", "x-ms-summary": "Title"},
            "topic": ref("SdpName"), "created_time": ref("SdpTime")}},
        "NoteItem": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Note ID"},
            "description": {"type": "string", "x-ms-summary": "Note"},
            "created_time": ref("SdpTime"),
            "show_to_requester": {"type": "boolean", "x-ms-summary": "Show To Requester"}}},
        "WorklogItem": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Worklog ID"},
            "description": {"type": "string", "x-ms-summary": "Description"},
            "owner": ref("SdpUser")}},
        "TaskItem": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Task ID"},
            "title": {"type": "string", "x-ms-summary": "Title"},
            "status": ref("SdpName")}},
        "LookupItem": name,
        "RequestListEnvelope": list_envelope("requests", "RequestSummary"),
        "RequestEnvelope": single_envelope("request", "RequestDetail"),
        "ChangeListEnvelope": list_envelope("changes", "ChangeSummary"),
        "ChangeEnvelope": single_envelope("change", "ChangeSummary"),
        "ProblemListEnvelope": list_envelope("problems", "ProblemSummary"),
        "ProblemEnvelope": single_envelope("problem", "ProblemSummary"),
        "SolutionListEnvelope": list_envelope("solutions", "SolutionSummary"),
        "SolutionEnvelope": single_envelope("solution", "SolutionSummary"),
        "NoteListEnvelope": list_envelope("notes", "NoteItem"),
        "NoteEnvelope": single_envelope("note", "NoteItem"),
        "WorklogListEnvelope": list_envelope("worklogs", "WorklogItem"),
        "WorklogEnvelope": single_envelope("worklog", "WorklogItem"),
        "TaskListEnvelope": list_envelope("tasks", "TaskItem"),
        "ResolutionEnvelope": {"type": "object", "properties": {
            "response_status": ref("ResponseStatus"),
            "resolution": {"type": "object", "x-ms-summary": "Resolution", "properties": {
                "content": {"type": "string", "x-ms-summary": "Content"}}}}},
        "LookupListEnvelope": {"type": "object", "properties": {
            "response_status": ref("ResponseStatus"), "list_info": ref("ListInfo"),
            "list": {"type": "array", "x-ms-summary": "Items", "items": ref("LookupItem")}}},
    }

    LIST_DEFAULT = '{"list_info":{"row_count":10,"start_index":1,"get_total_count":true}}'
    rid = ("request_id", "Request ID")
    cid = ("change_id", "Change ID")
    pid = ("problem_id", "Problem ID")
    sid = ("solution_id", "Solution ID")

    ops = [
        # Requests
        ("/requests", "get", list_op("ListRequests", "List requests",
            "Lists service desk requests with pagination, sorting, and search criteria.",
            '{"list_info":{"row_count":10,"start_index":1,"get_total_count":true,"search_criteria":{"field":"status.name","condition":"is","value":"Open"}}}',
            "RequestListEnvelope")),
        ("/requests", "post", create_op("CreateRequest", "Create request",
            "Creates a new service desk request. Only subject is required.",
            '{"request":{"subject":"Printer down","requester":{"email_id":"user@company.com"},"priority":{"name":"High"}}}',
            "RequestEnvelope")),
        ("/requests/{request_id}", "get", get_op("GetRequest", "Get request",
            "Gets the full details of a single service desk request by its ID.", *rid, "RequestEnvelope")),
        ("/requests/{request_id}", "put", update_op("UpdateRequest", "Update request",
            "Updates an existing request; only provided fields change.", *rid,
            '{"request":{"priority":{"name":"High"},"status":{"name":"In Progress"}}}', "RequestEnvelope")),
        ("/requests/{request_id}", "delete", delete_op("DeleteRequest", "Delete request",
            "Moves a request to the trash (destructive).", *rid)),
        ("/requests/{request_id}/close", "put", op("CloseRequest", "Close request",
            "Closes a request with optional closure details. Mandatory fields and workflow status transitions may be required first.",
            [path_param("request_id", "Request ID", "Request ID."),
             input_data_form('Closure envelope. Example: {"request":{"closure_info":{"closure_comments":"Resolved","closure_code":{"name":"Success"}}}}'),
             accept_ref()],
            {"200": ok("Request closed.", "RequestEnvelope"), "default": err()},
            consumes=["application/x-www-form-urlencoded"])),
        ("/requests/{request_id}/notes", "get", get_op("ListRequestNotes", "List request notes",
            "Lists notes attached to a request.", *rid, "NoteListEnvelope", use_input=True)),
        ("/requests/{request_id}/notes", "post", create_op("AddRequestNote", "Add request note",
            "Adds a note to a request.",
            '{"note":{"description":"Called the user","show_to_requester":false}}', "NoteEnvelope",
            extra_path=[path_param("request_id", "Request ID", "Request ID.")])),
        ("/requests/{request_id}/worklogs", "get", get_op("ListRequestWorklogs", "List request worklogs",
            "Lists worklogs (time entries) for a request.", *rid, "WorklogListEnvelope", use_input=True)),
        ("/requests/{request_id}/worklogs", "post", create_op("AddRequestWorklog", "Add request worklog",
            "Adds a worklog (time entry) to a request.",
            '{"worklog":{"description":"Investigated the issue","owner":{"email_id":"tech@company.com"}}}', "WorklogEnvelope",
            extra_path=[path_param("request_id", "Request ID", "Request ID.")])),
        ("/requests/{request_id}/tasks", "get", get_op("ListRequestTasks", "List request tasks",
            "Lists tasks associated with a request.", *rid, "TaskListEnvelope", use_input=True)),
        ("/requests/{request_id}/resolutions", "get", get_op("GetRequestResolution", "Get request resolution",
            "Gets the resolution of a request.", *rid, "ResolutionEnvelope")),
        ("/requests/{request_id}/resolutions", "post", create_op("AddRequestResolution", "Add request resolution",
            "Adds/sets the resolution of a request.",
            '{"resolution":{"content":"Replaced the toner cartridge."}}', "ResolutionEnvelope",
            extra_path=[path_param("request_id", "Request ID", "Request ID.")])),

        # Changes
        ("/changes", "get", list_op("ListChanges", "List changes",
            "Lists change requests with pagination and search criteria.", LIST_DEFAULT, "ChangeListEnvelope")),
        ("/changes", "post", create_op("CreateChange", "Create change",
            "Creates a new change. title is required.",
            '{"change":{"title":"Upgrade DB server","change_type":{"name":"Normal"}}}', "ChangeEnvelope")),
        ("/changes/{change_id}", "get", get_op("GetChange", "Get change",
            "Gets full details of a single change by its ID.", *cid, "ChangeEnvelope")),
        ("/changes/{change_id}", "put", update_op("UpdateChange", "Update change",
            "Updates an existing change; only provided fields change.", *cid,
            '{"change":{"stage":{"name":"Implementation"}}}', "ChangeEnvelope")),

        # Problems
        ("/problems", "get", list_op("ListProblems", "List problems",
            "Lists problems with pagination and search criteria.", LIST_DEFAULT, "ProblemListEnvelope")),
        ("/problems", "post", create_op("CreateProblem", "Create problem",
            "Creates a new problem. title is required.",
            '{"problem":{"title":"Recurring VPN drops"}}', "ProblemEnvelope")),
        ("/problems/{problem_id}", "get", get_op("GetProblem", "Get problem",
            "Gets full details of a single problem by its ID.", *pid, "ProblemEnvelope")),
        ("/problems/{problem_id}", "put", update_op("UpdateProblem", "Update problem",
            "Updates an existing problem; only provided fields change.", *pid,
            '{"problem":{"status":{"name":"Closed"}}}', "ProblemEnvelope")),

        # Solutions
        ("/solutions", "get", list_op("ListSolutions", "List solutions",
            "Lists knowledge base / solution articles.", LIST_DEFAULT, "SolutionListEnvelope")),
        ("/solutions", "post", create_op("CreateSolution", "Create solution",
            "Creates a new solution article. title is required.",
            '{"solution":{"title":"How to reset VPN","description":"Steps...","topic":{"name":"Network"}}}', "SolutionEnvelope")),
        ("/solutions/{solution_id}", "get", get_op("GetSolution", "Get solution",
            "Gets a single solution article by its ID.", *sid, "SolutionEnvelope")),
        ("/solutions/{solution_id}", "put", update_op("UpdateSolution", "Update solution",
            "Updates an existing solution article; only provided fields change.", *sid,
            '{"solution":{"is_public":true}}', "SolutionEnvelope")),
    ]

    # Admin lookups (dropdown sources for x-ms-dynamic-values).
    # (endpoint, operationId, summary, description). Endpoints are the ones
    # verified live on the demo build: this build exposes /users and
    # /support_groups (not /requesters, /groups) — see README build note.
    lookups = [
        ("technicians", "ListTechnicians", "List technicians", "Lists technicians."),
        ("users", "ListRequesters", "List requesters", "Lists requesters / end users (the /users module; some builds use /requesters)."),
        ("categories", "ListCategories", "List categories", "Lists request categories."),
        ("statuses", "ListStatuses", "List statuses", "Lists request statuses."),
        ("priorities", "ListPriorities", "List priorities", "Lists priority levels."),
        ("sites", "ListSites", "List sites", "Lists sites (locations)."),
        ("support_groups", "ListSupportGroups", "List support groups", "Lists technician/support groups (the /support_groups module; some builds use /groups)."),
        ("departments", "ListDepartments", "List departments", "Lists departments."),
        ("urgencies", "ListUrgencies", "List urgencies", "Lists urgency levels."),
        ("impacts", "ListImpacts", "List impacts", "Lists impact levels."),
        ("modes", "ListModes", "List modes", "Lists request submission modes."),
        ("request_types", "ListRequestTypes", "List request types", "Lists request types (e.g. Incident, Service Request)."),
    ]
    for ep, opid, summ, desc in lookups:
        o = list_op(opid, summ, desc + " Intended as a dropdown source.",
                    '{"list_info":{"row_count":100,"start_index":1,"get_total_count":true}}', "LookupListEnvelope")
        o["x-ms-visibility"] = "advanced"
        ops.append(("/" + ep, "get", o))

    return build(
        "SDP - Service Desk",
        "Work with ManageEngine ServiceDesk Plus On-Premises requests, changes, problems, "
        "solutions, notes, worklogs, tasks, and resolutions, plus admin lookups for dropdowns. "
        "Auth: technician API key in the 'authtoken' header. Every parameter is wrapped in a "
        "single 'input_data' JSON envelope per the SDP V3 API contract.",
        "/api/v3", ops, defs)


# ---------------------------------------------------------------------------
# SDP – Assets & CMDB (v3) connector
# ---------------------------------------------------------------------------

def assets_cmdb_v3():
    name, user, time, status, list_info = common_defs()
    ci_obj = {"type": "object", "x-ms-summary": "Configuration Item",
              "description": "A CMDB configuration item. Fields vary by CI type; see the type's _metadata.",
              "properties": {
                  "id": {"type": "string", "x-ms-summary": "CI ID"},
                  "name": {"type": "string", "x-ms-summary": "Name"},
                  "ci_type": ref("SdpName")}}
    # V3 CMDB CIs/assets don't use the user/time sub-objects — omit them (lean).
    defs = {
        "SdpName": name,
        "ResponseStatus": status, "ListInfo": list_info,
        "CIType": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "CI Type ID"},
            "display_name": {"type": "string", "x-ms-summary": "Display Name"},
            "api_plural_name": {"type": "string", "x-ms-summary": "API Plural Name",
                                "description": "Use this value as the CI Type path segment in the CI operations."},
            "description": {"type": "string", "x-ms-summary": "Description"}}},
        "ConfigurationItem": ci_obj,
        "AssetSummary": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Asset ID"},
            "name": {"type": "string", "x-ms-summary": "Name"},
            "product_type": ref("SdpName"), "asset_state": ref("SdpName"),
            "site": ref("SdpName"), "department": ref("SdpName")}},
        "Relationship": {"type": "object", "properties": {
            "id": {"type": "string", "x-ms-summary": "Relationship ID"},
            "relationship_type": ref("SdpName")}},
        "CITypeListEnvelope": list_envelope("ci_types", "CIType"),
        "CIListEnvelope": {"type": "object", "properties": {
            "response_status": ref("ResponseStatus"), "list_info": ref("ListInfo"),
            "cmdb": {"type": "array", "x-ms-summary": "Configuration Items", "items": ref("ConfigurationItem")}}},
        "CIEnvelope": single_envelope("ci", "ConfigurationItem"),
        "MetadataEnvelope": {"type": "object", "properties": {
            "response_status": ref("ResponseStatus"),
            "metadata": {"type": "object", "x-ms-summary": "Metadata"}}},
        "RelationshipListEnvelope": list_envelope("assoc_ci_relationships", "Relationship"),
        "AssetListEnvelope": list_envelope("assets", "AssetSummary"),
        "AssetEnvelope": single_envelope("asset", "AssetSummary"),
        "AssetModuleListEnvelope": list_envelope("asset_modules", "SdpName"),
    }
    LIST_DEFAULT = '{"list_info":{"row_count":10,"start_index":1,"get_total_count":true}}'
    cit = ("ci_type", "CI Type (api_plural_name)")
    ciid = ("ci_id", "CI ID")

    ops = [
        ("/ci_types", "get", list_op("ListCITypes", "List CI types",
            "Lists all CMDB configuration-item types. Each has an api_plural_name used as the CI Type path segment.",
            '{"list_info":{"row_count":100,"start_index":1,"get_total_count":true}}', "CITypeListEnvelope")),
        ("/cmdb", "get", list_op("ListAllCIs", "List all CIs",
            "Lists all configuration items across every type.", LIST_DEFAULT, "CIListEnvelope")),
        ("/{ci_type}", "get", op("ListCIsByType", "List CIs by type",
            "Lists configuration items of one CI type. Set CI Type to the type's api_plural_name (from List CI types).",
            [path_param("ci_type", "CI Type (api_plural_name)", "The CI type's api_plural_name, e.g. cmdb_businessservice."),
             input_data_query(LIST_DEFAULT, "list_info envelope as a JSON string."), accept_ref()],
            {"200": ok("CIs returned.", "CIListEnvelope"), "default": err()})),
        ("/{ci_type}", "post", create_op("CreateCI", "Create CI",
            "Creates a configuration item of the given type. The input_data payload wraps the CI object; confirm the field set against the type's metadata.",
            '{"ci":{"name":"web01","ci_type":{"name":"Business Service"}}}', "CIEnvelope",
            extra_path=[path_param("ci_type", "CI Type (api_plural_name)", "The CI type's api_plural_name.")])),
        ("/{ci_type}/{ci_id}", "get", op("GetCI", "Get CI",
            "Gets a single configuration item by type and ID.",
            [path_param("ci_type", "CI Type (api_plural_name)", "The CI type's api_plural_name."),
             path_param("ci_id", "CI ID", "The numeric CI ID."), accept_ref()],
            {"200": ok("CI returned.", "CIEnvelope"), "default": err()})),
        ("/{ci_type}/{ci_id}", "put", op("UpdateCI", "Update CI",
            "Updates a configuration item by type and ID (V3 updates by CI ID only, no criteria-based update).",
            [path_param("ci_type", "CI Type (api_plural_name)", "The CI type's api_plural_name."),
             path_param("ci_id", "CI ID", "The numeric CI ID."),
             input_data_form('CI payload. Example: {"ci":{"name":"web01-renamed"}}'), accept_ref()],
            {"200": ok("CI updated.", "CIEnvelope"), "default": err()},
            consumes=["application/x-www-form-urlencoded"])),
        ("/{ci_type}/_metadata", "get", op("GetCITypeMetadata", "Get CI type metadata",
            "Gets the field/layout metadata for a CI type (its api_plural_name).",
            [path_param("ci_type", "CI Type (api_plural_name)", "The CI type's api_plural_name."), accept_ref()],
            {"200": ok("Metadata returned.", "MetadataEnvelope"), "default": err()})),
        ("/{ci_type}/{ci_id}/assoc_ci_relationships", "get", op("ListCIRelationships", "List CI relationships",
            "Lists the association relationships of a CI (V3; requires SDP build 15100+).",
            [path_param("ci_type", "CI Type (api_plural_name)", "The CI type's api_plural_name."),
             path_param("ci_id", "CI ID", "The numeric CI ID."),
             input_data_query(desc='Optional filter, e.g. {"list_info":{"filter":{"name":"get_all_association"}}}'),
             accept_ref()],
            {"200": ok("Relationships returned.", "RelationshipListEnvelope"), "default": err()})),
        ("/{ci_type}/{ci_id}/assoc_ci_relationships", "post", create_op("AddCIRelationship", "Add CI relationship",
            "Adds an association relationship to a CI (V3; requires SDP build 15100+).",
            '{"assoc_ci_relationship":{"end_ci":{"id":"123"},"relationship":{"id":"1"}}}', "RelationshipListEnvelope",
            extra_path=[path_param("ci_type", "CI Type (api_plural_name)", "The CI type's api_plural_name."),
                        path_param("ci_id", "CI ID", "The numeric CI ID.")])),
        ("/asset_modules", "get", list_op("ListAssetModules", "List asset modules",
            "Lists the asset type/module hierarchy.", LIST_DEFAULT, "AssetModuleListEnvelope")),
        ("/assets", "get", list_op("ListAssets", "List assets",
            "Lists assets with pagination and search criteria.", LIST_DEFAULT, "AssetListEnvelope")),
        ("/assets/{asset_id}", "get", get_op("GetAsset", "Get asset",
            "Gets a single asset by its ID.", "asset_id", "Asset ID", "AssetEnvelope")),
        ("/assets/{asset_id}", "put", update_op("UpdateAsset", "Update asset",
            "Updates an existing asset; only provided fields change.", "asset_id", "Asset ID",
            '{"asset":{"asset_state":{"name":"In Use"}}}', "AssetEnvelope")),
    ]
    return build(
        "SDP - Assets & CMDB (v3)",
        "Manage ManageEngine ServiceDesk Plus On-Premises assets and the CMDB (v3 JSON API): "
        "CI types, configuration items per type and across the CMDB, CI metadata, association "
        "relationships, and assets. Auth: technician API key in the 'authtoken' header; every "
        "parameter is wrapped in a single 'input_data' JSON envelope. Full CMDB v3 requires SDP "
        "build 15100+ (or AssetExplorer 7700+).",
        "/api/v3", ops, defs)


# ---------------------------------------------------------------------------
# SDP – Query (Execute Query) connector
# ---------------------------------------------------------------------------

def query():
    _, _, _, status, _ = common_defs()
    defs = {
        "ResponseStatus": status,
        "ExecuteQueryEnvelope": {"type": "object", "properties": {
            "response_status": ref("ResponseStatus"),
            "execute_query": {"type": "object", "x-ms-summary": "Execute Query", "properties": {
                "data": {"type": "array", "x-ms-summary": "Rows",
                         "description": "Result rows, keyed by the SQL column aliases (always use AS).",
                         "items": {"type": "object"}}}}}},
    }
    example = ('SQL SELECT as a JSON string. Read-only (SELECT only; DML and information_schema '
               'are rejected). Always alias columns with AS. Example: '
               '{"query":"SELECT workorderid AS id, title AS title FROM workorder LIMIT 5"}')
    ops = [
        ("/reports/_execute_query", "post", op(
            "ExecuteQuery", "Execute query",
            "Runs a single read-only SQL SELECT against the SDP database and returns rows keyed "
            "by the column aliases. POST-only; SELECT-only (UPDATE/DELETE/INSERT and "
            "information_schema/catalog queries are rejected server-side). Physical table/column "
            "names are build-specific — see the templates/ library (build 14990).",
            [input_data_form(example), accept_ref()],
            {"200": ok("Query result rows.", "ExecuteQueryEnvelope"), "default": err()},
            consumes=["application/x-www-form-urlencoded"])),
    ]
    return build(
        "SDP - Query",
        "Read-only power tool for ManageEngine ServiceDesk Plus On-Premises: run one SQL SELECT "
        "via the Execute Query report API to replace many REST GETs (JOINs, custom fields, "
        "aggregates). Auth: technician API key in the 'authtoken' header; the SELECT is wrapped "
        "in a single 'input_data' JSON envelope. Admin-scoped ('Create Query Report' permission) "
        "and build/edition-gated — probe with 'SELECT 1 AS test' at setup and fall back to REST "
        "if it errors. Physical schema names vary by build; keep SQL in the templates/ library.",
        "/api/v3", ops, defs)


CONNECTORS = {
    "sdp-service-desk": service_desk,
    "sdp-assets-cmdb-v3": assets_cmdb_v3,
    "sdp-query": query,
}


def main():
    for name, fn in CONNECTORS.items():
        out_dir = os.path.join(ROOT, "connectors", name)
        os.makedirs(out_dir, exist_ok=True)
        doc = fn()
        doc["info"]["description"] += " Definition (import-by-URL): " + RAW_URL.format(name)
        # Per-action "Learn more" links, belt and braces: externalDocs is the
        # Swagger 2.0 field for exactly this (allowed on operations by
        # Microsoft's connector schema), and the URL is also appended to the
        # description because the flow designer's About tab provably shows the
        # description text ("Operation note") for custom connectors.
        for methods in doc["paths"].values():
            for o in methods.values():
                url = action_doc_url(name, o["operationId"])
                o["description"] = o["description"].rstrip() + " Learn more: " + url
                o["externalDocs"] = {"description": "Learn more", "url": url}
        n_ops = sum(len(m) for m in doc["paths"].values())
        path = os.path.join(out_dir, "apiDefinition.swagger.json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
            f.write("\n")
        size = os.path.getsize(path)
        print(f"{name}: {n_ops} operations, {size} bytes -> {path}")
        assert size < 1_000_000, f"{name} exceeds 1 MB"
        assert n_ops <= 256, f"{name} exceeds 256 operations"


if __name__ == "__main__":
    main()
