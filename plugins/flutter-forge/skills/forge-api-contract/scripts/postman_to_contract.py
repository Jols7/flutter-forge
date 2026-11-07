#!/usr/bin/env python3
"""Turn a Postman collection or an OpenAPI 3 spec into an API contract for flutter-forge.

Supported inputs (auto-detected):
  * Postman v2.1 export (JSON file)
  * Postman v3 JSON (`postman collection get <id> --json > c.json`)
  * Postman v3 git-native directory (postman/collections/<name>/, YAML files)
  * OpenAPI 3.x (JSON, or simple YAML)

Usage:
  postman_to_contract.py SOURCE [--format md|json] [--out FILE]
                         [--filter TEXT ...] [--fixtures-dir DIR] [--list]

Security: never prints variable values, auth credentials or header values that
look sensitive; fixture bodies are redacted for sensitive-looking keys. Read-only
except for --out/--fixtures-dir. No network. Python 3.9+ stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

_SENSITIVE_TOKENS = {
    "password", "passwd", "pwd", "pass", "secret", "token", "authorization", "auth", "cookie",
    "session", "otp", "pin", "nip", "cvv", "cvc", "pan", "iban", "clabe", "ssn", "curp", "rfc",
    "private", "credential", "credentials", "bearer", "signature",
}
_SENSITIVE_SUBSTRINGS = ("password", "token", "secret", "apikey", "cardnumber", "authorization", "credential", "privatekey")


def is_sensitive(key: str) -> bool:
    """True when a field/header/param name looks like it carries a secret or regulated data."""
    if not key:
        return False
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", key).lower()
    tokens = [t for t in re.split(r"[^a-z0-9]+", spaced) if t]
    if any(t in _SENSITIVE_TOKENS for t in tokens):
        return True
    compact = "".join(tokens)
    if any(sub in compact for sub in _SENSITIVE_SUBSTRINGS):
        return True
    return any(a + b in ("apikey", "cardnumber", "accountnumber") for a, b in zip(tokens, tokens[1:]))


VAR_REF = re.compile(r"\{\{\s*([^}\s]+)\s*\}\}")
REDACTED = "<redacted>"


# --------------------------------------------------------------------------- YAML (subset)
def load_simple_yaml(text: str) -> Any:
    """Parse the YAML subset used by Postman v3 files and simple OpenAPI specs.

    Supports mappings, sequences (of scalars or mappings), block scalars (| |- >),
    quoted scalars, inline [] / {} for empty values and flow lists of scalars.
    Not supported: anchors, tags, multi-document streams, complex flow mappings.
    """
    lines = [l.rstrip("\n") for l in text.splitlines()]
    pos = [0]

    def indent_of(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def is_blank(line: str) -> bool:
        s = line.strip()
        return not s or s.startswith("#")

    def skip_blank() -> None:
        while pos[0] < len(lines) and is_blank(lines[pos[0]]):
            pos[0] += 1

    def scalar(raw: str) -> Any:
        s = raw.strip()
        if s.startswith("'") and s.endswith("'") and len(s) >= 2:
            return s[1:-1].replace("''", "'")
        if s.startswith('"') and s.endswith('"') and len(s) >= 2:
            try:
                return json.loads(s)
            except ValueError:
                return s[1:-1]
        if " #" in s:
            s = s.split(" #", 1)[0].rstrip()
        if s in ("", "~", "null", "Null", "NULL"):
            return None
        if s in ("true", "True"):
            return True
        if s in ("false", "False"):
            return False
        if s == "[]":
            return []
        if s == "{}":
            return {}
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            return [scalar(p) for p in _split_flow(inner)] if inner else []
        if re.fullmatch(r"-?\d+", s):
            return int(s)
        if re.fullmatch(r"-?\d+\.\d+([eE][-+]?\d+)?", s):
            return float(s)
        return s

    def block_scalar(style: str, parent_indent: int) -> str:
        collected: List[str] = []
        block_indent: Optional[int] = None
        while pos[0] < len(lines):
            line = lines[pos[0]]
            if line.strip() == "":
                collected.append("")
                pos[0] += 1
                continue
            ind = indent_of(line)
            if ind <= parent_indent:
                break
            if block_indent is None:
                block_indent = ind
            collected.append(line[block_indent:])
            pos[0] += 1
        while collected and collected[-1] == "":
            collected.pop()
        if style.startswith(">"):
            return " ".join(c for c in collected if c)
        out = "\n".join(collected)
        return out if style.endswith("-") else out + "\n"

    def parse_block(min_indent: int) -> Any:
        skip_blank()
        if pos[0] >= len(lines):
            return None
        line = lines[pos[0]]
        ind = indent_of(line)
        if ind < min_indent:
            return None
        if line.lstrip().startswith("- ") or line.strip() == "-":
            return parse_seq(ind)
        return parse_map(ind)

    def parse_value_after_key(rest: str, ind: int) -> Any:
        rest = rest.strip()
        if rest in ("|", "|-", "|+", ">", ">-"):
            pos[0] += 1
            return block_scalar(rest, ind)
        if rest == "" or rest.startswith("#"):
            pos[0] += 1
            skip_blank()
            if pos[0] < len(lines):
                nxt = lines[pos[0]]
                nind = indent_of(nxt)
                if nind > ind or (nind == ind and nxt.lstrip().startswith("- ")):
                    return parse_block(nind)
            return None
        pos[0] += 1
        return scalar(rest)

    def parse_map(ind: int) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        while True:
            skip_blank()
            if pos[0] >= len(lines):
                break
            line = lines[pos[0]]
            cur = indent_of(line)
            if cur != ind or line.lstrip().startswith("- "):
                break
            key, rest = _split_key(line.strip())
            if key is None:
                pos[0] += 1
                continue
            result[key] = parse_value_after_key(rest, ind)
        return result

    def parse_seq(ind: int) -> List[Any]:
        items: List[Any] = []
        while True:
            skip_blank()
            if pos[0] >= len(lines):
                break
            line = lines[pos[0]]
            if indent_of(line) != ind or not (line.lstrip().startswith("- ") or line.strip() == "-"):
                break
            content = line.strip()[1:].strip()
            if content == "":
                pos[0] += 1
                items.append(parse_block(ind + 1))
                continue
            key, rest = _split_key(content)
            if key is not None and not content.startswith(("'", '"')):
                # mapping item: rewrite the current line as a mapping line at ind+2
                item_indent = ind + 2
                lines[pos[0]] = " " * item_indent + content
                items.append(parse_map(item_indent))
            else:
                pos[0] += 1
                items.append(scalar(content))
        return items

    return parse_block(0)


def _split_key(s: str) -> Tuple[Optional[str], str]:
    if s.startswith(("'", '"')):
        quote = s[0]
        end = s.find(quote, 1)
        if end > 0 and s[end + 1:end + 2] == ":":
            return s[1:end], s[end + 2:]
        return None, s
    m = re.match(r"^([^:#\s][^:]*?)\s*:(\s|$)(.*)$", s)
    if not m:
        return None, s
    return m.group(1).strip(), m.group(3)


def _split_flow(inner: str) -> List[str]:
    parts, depth, cur, quote = [], 0, "", None
    for ch in inner:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
            continue
        cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


# --------------------------------------------------------------------------- schema inference
def infer(value: Any) -> Dict[str, Any]:
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "bool"}
    if isinstance(value, int):
        return {"type": "int"}
    if isinstance(value, float):
        return {"type": "double"}
    if isinstance(value, str):
        fmt = None
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}([T ][\d:.]+(Z|[+-]\d{2}:?\d{2})?)?", value):
            fmt = "date-time" if len(value) > 10 else "date"
        elif re.fullmatch(r"[0-9a-fA-F-]{36}", value):
            fmt = "uuid"
        elif re.fullmatch(r"-?\d+(\.\d+)?", value):
            fmt = "numeric-string"
        out: Dict[str, Any] = {"type": "string"}
        if fmt:
            out["format"] = fmt
        return out
    if isinstance(value, list):
        item: Optional[Dict[str, Any]] = None
        for element in value:
            item = merge(item, infer(element))
        return {"type": "list", "items": item or {"type": "unknown"}}
    if isinstance(value, dict):
        return {"type": "object", "fields": {k: infer(v) for k, v in value.items()}}
    return {"type": "unknown"}


def merge(a: Optional[Dict[str, Any]], b: Dict[str, Any]) -> Dict[str, Any]:
    if a is None:
        return b
    nullable = a.get("nullable", False) or b.get("nullable", False)
    if a["type"] == "null" and b["type"] != "null":
        return dict(b, nullable=True)
    if b["type"] == "null" and a["type"] != "null":
        return dict(a, nullable=True)
    if {a["type"], b["type"]} == {"int", "double"}:
        return {"type": "num", "nullable": nullable, "note": "int and double seen"}
    if a["type"] != b["type"]:
        if "unknown" in (a["type"], b["type"]):
            return a if b["type"] == "unknown" else b
        return {"type": "mixed", "seen": sorted({a["type"], b["type"]}), "nullable": nullable}
    out = dict(a)
    out["nullable"] = nullable
    if a["type"] == "object":
        fields: Dict[str, Any] = {}
        keys = list(a["fields"].keys()) + [k for k in b["fields"] if k not in a["fields"]]
        for k in keys:
            if k in a["fields"] and k in b["fields"]:
                fields[k] = merge(a["fields"][k], b["fields"][k])
            else:
                present = a["fields"].get(k) or b["fields"].get(k)
                fields[k] = dict(present, optional=True)
        out["fields"] = fields
    elif a["type"] == "list":
        ai, bi = a.get("items"), b.get("items")
        out["items"] = merge(ai, bi) if ai and bi else (ai or bi)
    if not nullable:
        out.pop("nullable", None)
    return out


def schema_lines(schema: Optional[Dict[str, Any]], indent: int = 2) -> List[str]:
    if not schema:
        return [" " * indent + "(no body)"]
    lines: List[str] = []

    def label(s: Dict[str, Any]) -> str:
        t = s["type"]
        if t == "list":
            inner = s.get("items") or {"type": "unknown"}
            t = "list<%s>" % (inner["type"] if inner["type"] != "object" else "object")
        if s.get("format"):
            t += " (%s)" % s["format"]
        if s.get("type") == "mixed":
            t = "mixed(%s)" % "|".join(s.get("seen", []))
        if s.get("nullable"):
            t += "?"
        if s.get("optional"):
            t += "  [may be absent]"
        if s.get("note"):
            t += "  [%s]" % s["note"]
        return t

    def walk(s: Dict[str, Any], depth: int) -> None:
        pad = " " * (indent + depth * 2)
        target = s
        if s["type"] == "list" and s.get("items", {}).get("type") == "object":
            target = s["items"]
        if target["type"] == "object":
            if not target["fields"]:
                lines.append(pad + "{} (empty object)")
            for key, sub in target["fields"].items():
                lines.append("%s%s: %s" % (pad, key, label(sub)))
                if sub["type"] == "object" or (sub["type"] == "list" and sub.get("items", {}).get("type") == "object"):
                    walk(sub, depth + 1)
                if sub["type"] == "list" and sub.get("items", {}).get("type") == "unknown":
                    lines.append(pad + "  ⚠ empty list in every example: item type unknown (gap)")

    if schema["type"] in ("object", "list"):
        lines.append(" " * indent + "root: " + label(schema))
        walk(schema, 1)
    else:
        lines.append(" " * indent + "root: " + label(schema))
    return lines


# --------------------------------------------------------------------------- helpers
def try_json(text: Any) -> Any:
    if isinstance(text, (dict, list)):
        return text
    if not isinstance(text, str) or not text.strip():
        return None
    try:
        return json.loads(text)
    except ValueError:
        return None


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: (REDACTED if is_sensitive(k) and not isinstance(v, (dict, list)) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def relative_path(url: str) -> str:
    url = url.strip()
    url = re.sub(r"^\{\{\s*[^}]+\s*\}\}", "", url)          # leading {{base_url}}
    url = re.sub(r"^https?://[^/]+", "", url)
    url = url.split("?", 1)[0]
    url = re.sub(r"/:([A-Za-z_][A-Za-z0-9_]*)", r"/{\1}", url)
    url = VAR_REF.sub(lambda m: "{%s}" % m.group(1), url)
    return url.lstrip("/")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "endpoint"


def kv_list(items: Any) -> List[Dict[str, Any]]:
    out = []
    for it in items or []:
        if isinstance(it, dict) and it.get("key") and not it.get("disabled"):
            out.append(it)
    return out


def describe_value(key: str, value: Any) -> str:
    if value is None or value == "":
        return ""
    if is_sensitive(key) or VAR_REF.search(str(value)):
        return ""
    return str(value)


def new_endpoint(name: str, folder: List[str], method: str, url: str) -> Dict[str, Any]:
    return {
        "id": slug("_".join(folder[-1:] + [name])) if folder else slug(name),
        "name": name,
        "folder": "/".join(folder),
        "method": (method or "GET").upper(),
        "path": relative_path(url or ""),
        "path_params": [],
        "query": [],
        "headers": [],
        "auth": None,
        "request_body": None,
        "request_schema": None,
        "examples": [],
        "description": "",
    }


# --------------------------------------------------------------------------- Postman v2.1
def from_v21(doc: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    endpoints: List[Dict[str, Any]] = []
    root_auth = (doc.get("auth") or {}).get("type")

    def visit(items: List[Any], folder: List[str], inherited_auth: Optional[str]) -> None:
        for item in items or []:
            if "item" in item:
                auth = (item.get("auth") or {}).get("type") or inherited_auth
                visit(item["item"], folder + [item.get("name", "folder")], auth)
                continue
            req = item.get("request") or {}
            if isinstance(req, str):
                req = {"url": req, "method": "GET"}
            url = req.get("url") or {}
            raw = url if isinstance(url, str) else url.get("raw") or "/".join(url.get("path") or [])
            ep = new_endpoint(item.get("name", "request"), folder, req.get("method"), raw)
            if isinstance(url, dict):
                ep["path_params"] = [{"key": v.get("key"), "example": describe_value(v.get("key", ""), v.get("value"))} for v in kv_list(url.get("variable"))]
                ep["query"] = [{"key": q.get("key"), "example": describe_value(q.get("key", ""), q.get("value")), "description": _desc(q.get("description"))} for q in kv_list(url.get("query"))]
            ep["headers"] = [h.get("key") for h in kv_list(req.get("header"))]
            auth = req.get("auth")
            ep["auth"] = (auth or {}).get("type") if auth else (inherited_auth and inherited_auth + " (inherited)")
            ep["description"] = _desc(req.get("description"))
            body = req.get("body") or {}
            mode = body.get("mode")
            if mode == "raw":
                parsed = try_json(body.get("raw"))
                ep["request_body"] = "json" if parsed is not None else "raw"
                ep["request_schema"] = infer(parsed) if parsed is not None else None
                ep["_request_sample"] = parsed
            elif mode in ("urlencoded", "formdata"):
                ep["request_body"] = mode
                ep["request_schema"] = {"type": "object", "fields": {f.get("key"): {"type": "file" if f.get("type") == "file" else "string"} for f in kv_list(body.get(mode))}}
            elif mode == "graphql":
                ep["request_body"] = "graphql"
            for resp in item.get("response") or []:
                parsed = try_json(resp.get("body"))
                ep["examples"].append({
                    "name": resp.get("name") or "",
                    "status": resp.get("code"),
                    "schema": infer(parsed) if parsed is not None else None,
                    "_body": parsed,
                })
            endpoints.append(ep)

    visit(doc.get("item") or [], [], root_auth)
    variables = sorted({v.get("key") for v in doc.get("variable") or [] if v.get("key")})
    info = {"name": (doc.get("info") or {}).get("name"), "format": "postman-v2.1", "collection_variables": variables, "auth": root_auth}
    return endpoints, info


def _desc(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("content")
    return (value or "").strip().splitlines()[0][:200] if value else ""


# --------------------------------------------------------------------------- Postman v3
def _v3_request(entity: Dict[str, Any], name: str, folder: List[str], inherited_auth: Optional[str]) -> Dict[str, Any]:
    ep = new_endpoint(entity.get("name") or name, folder, entity.get("method"), entity.get("url") or "")
    ep["path_params"] = [{"key": p.get("key"), "example": describe_value(p.get("key", ""), p.get("value"))} for p in kv_list(entity.get("pathVariables"))]
    ep["query"] = [{"key": q.get("key"), "example": describe_value(q.get("key", ""), q.get("value")), "description": _desc(q.get("description"))} for q in kv_list(entity.get("queryParams"))]
    ep["headers"] = [h.get("key") for h in kv_list(entity.get("headers"))]
    auth = entity.get("auth")
    ep["auth"] = (auth.get("type") if isinstance(auth, dict) else None) or (inherited_auth and inherited_auth + " (inherited)")
    ep["description"] = _desc(entity.get("description"))
    body = entity.get("body") or {}
    btype = body.get("type")
    if btype == "json":
        parsed = try_json(body.get("content"))
        ep["request_body"] = "json"
        ep["request_schema"] = infer(parsed) if parsed is not None else None
        ep["_request_sample"] = parsed
    elif btype in ("formdata", "urlencoded"):
        ep["request_body"] = btype
        ep["request_schema"] = {"type": "object", "fields": {f.get("key"): {"type": "file" if f.get("type") == "file" else "string"} for f in kv_list(body.get("content"))}}
    elif btype and btype != "none":
        ep["request_body"] = btype
    return ep


def _v3_example(entity: Dict[str, Any], name: str) -> Dict[str, Any]:
    response = entity.get("response") or {}
    body = response.get("body") or {}
    parsed = try_json(body.get("content") if isinstance(body, dict) else body)
    return {"name": entity.get("name") or name, "status": response.get("statusCode"), "schema": infer(parsed) if parsed is not None else None, "_body": parsed}


def from_v3_json(doc: Any) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    endpoints: List[Dict[str, Any]] = []

    def visit(node: Any, folder: List[str], auth: Optional[str]) -> None:
        if isinstance(node, list):
            for child in node:
                visit(child, folder, auth)
            return
        if not isinstance(node, dict):
            return
        kind = node.get("$kind")
        if kind == "http-request":
            ep = _v3_request(node, node.get("name") or "request", folder, auth)
            for ex in _find_kind(node, "http-example"):
                ep["examples"].append(_v3_example(ex, ex.get("name") or ""))
            endpoints.append(ep)
            return
        next_folder = folder
        next_auth = auth
        if kind == "collection" or ("items" in node and node.get("name")):
            if node.get("name") and folder is not None and kind != "collection-root":
                next_folder = folder + [node["name"]] if folder or kind != "collection" else folder
            a = node.get("auth")
            next_auth = (a.get("type") if isinstance(a, dict) else None) or auth
        for key, value in node.items():
            if isinstance(value, (dict, list)) and key not in ("auth", "variables", "scripts"):
                visit(value, next_folder, next_auth)

    visit(doc, [], None)
    name = doc.get("name") if isinstance(doc, dict) else None
    variables = sorted({v.get("key") for v in (doc.get("variables") or [] if isinstance(doc, dict) else []) if isinstance(v, dict) and v.get("key")})
    return endpoints, {"name": name, "format": "postman-v3-json", "collection_variables": variables}


def _find_kind(node: Any, kind: str) -> List[Dict[str, Any]]:
    found: List[Dict[str, Any]] = []
    if isinstance(node, dict):
        if node.get("$kind") == kind:
            found.append(node)
        for value in node.values():
            found += _find_kind(value, kind)
    elif isinstance(node, list):
        for value in node:
            found += _find_kind(value, kind)
    return found


def from_v3_dir(root: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    endpoints: List[Dict[str, Any]] = []
    variables: set = set()
    collection_auth: Dict[str, Optional[str]] = {}

    def definition(path: str) -> Dict[str, Any]:
        p = os.path.join(path, ".resources", "definition.yaml")
        if not os.path.exists(p):
            return {}
        with open(p, encoding="utf-8") as fh:
            data = load_simple_yaml(fh.read()) or {}
        return data if isinstance(data, dict) else {}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d != ".resources")
        rel = os.path.relpath(dirpath, root)
        folder = [] if rel == "." else rel.replace(os.sep, "/").split("/")
        meta = definition(dirpath)
        for v in meta.get("variables") or []:
            if isinstance(v, dict) and v.get("key"):
                variables.add(v["key"])
        parent_auth = collection_auth.get(os.path.dirname(dirpath))
        auth = meta.get("auth")
        collection_auth[dirpath] = (auth.get("type") if isinstance(auth, dict) else None) or parent_auth
        for fname in sorted(filenames):
            if not fname.endswith(".request.yaml"):
                continue
            stem = fname[: -len(".request.yaml")]
            with open(os.path.join(dirpath, fname), encoding="utf-8") as fh:
                entity = load_simple_yaml(fh.read()) or {}
            ep = _v3_request(entity, stem, folder, collection_auth[dirpath])
            ex_dir = os.path.join(dirpath, ".resources", stem + ".resources", "examples")
            if os.path.isdir(ex_dir):
                for ex_name in sorted(os.listdir(ex_dir)):
                    if ex_name.endswith(".example.yaml"):
                        with open(os.path.join(ex_dir, ex_name), encoding="utf-8") as fh:
                            ex = load_simple_yaml(fh.read()) or {}
                        ep["examples"].append(_v3_example(ex, ex_name[: -len(".example.yaml")]))
            endpoints.append(ep)
    return endpoints, {"name": os.path.basename(os.path.abspath(root)), "format": "postman-v3-dir", "collection_variables": sorted(variables)}


# --------------------------------------------------------------------------- OpenAPI 3
def from_openapi(doc: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    endpoints: List[Dict[str, Any]] = []
    components = (doc.get("components") or {}).get("schemas") or {}

    def resolve(schema: Any, depth: int = 0) -> Optional[Dict[str, Any]]:
        if not isinstance(schema, dict) or depth > 12:
            return None
        if "$ref" in schema:
            ref = schema["$ref"].split("/")[-1]
            return resolve(components.get(ref), depth + 1)
        for combo in ("allOf", "oneOf", "anyOf"):
            if combo in schema:
                merged: Dict[str, Any] = {"type": "object", "fields": {}}
                for part in schema[combo]:
                    r = resolve(part, depth + 1)
                    if r and r.get("type") == "object":
                        merged["fields"].update(r["fields"])
                if combo != "allOf":
                    merged["note"] = combo + " (variants merged)"
                return merged
        t = schema.get("type")
        nullable = bool(schema.get("nullable")) or (isinstance(t, list) and "null" in t)
        if isinstance(t, list):
            t = next((x for x in t if x != "null"), "string")
        out: Dict[str, Any]
        if t == "object" or "properties" in schema:
            required = set(schema.get("required") or [])
            fields = {}
            for k, v in (schema.get("properties") or {}).items():
                sub = resolve(v, depth + 1) or {"type": "unknown"}
                if k not in required:
                    sub = dict(sub, optional=True)
                fields[k] = sub
            out = {"type": "object", "fields": fields}
        elif t == "array":
            out = {"type": "list", "items": resolve(schema.get("items"), depth + 1) or {"type": "unknown"}}
        elif t == "integer":
            out = {"type": "int"}
        elif t == "number":
            out = {"type": "num"}
        elif t == "boolean":
            out = {"type": "bool"}
        else:
            out = {"type": "string"}
            if schema.get("format"):
                out["format"] = schema["format"]
            if schema.get("enum"):
                out["note"] = "enum: " + ", ".join(map(str, schema["enum"]))
        if nullable:
            out["nullable"] = True
        return out

    for path, ops in (doc.get("paths") or {}).items():
        if not isinstance(ops, dict):
            continue
        shared_params = ops.get("parameters") or []
        for method, op in ops.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete", "head", "options") or not isinstance(op, dict):
                continue
            ep = new_endpoint(op.get("operationId") or op.get("summary") or "%s %s" % (method, path), [(op.get("tags") or [""])[0]] if op.get("tags") else [], method, path)
            ep["description"] = (op.get("summary") or op.get("description") or "").strip()[:200]
            for p in shared_params + (op.get("parameters") or []):
                if "$ref" in p:
                    p = (doc.get("components") or {}).get("parameters", {}).get(p["$ref"].split("/")[-1], {})
                entry = {"key": p.get("name"), "example": "", "description": (p.get("description") or "")[:120]}
                if p.get("in") == "path":
                    ep["path_params"].append(entry)
                elif p.get("in") == "query":
                    ep["query"].append(entry)
                elif p.get("in") == "header":
                    ep["headers"].append(p.get("name"))
            body = ((op.get("requestBody") or {}).get("content") or {})
            if body:
                ctype, media = next(iter(body.items()))
                ep["request_body"] = "json" if "json" in ctype else ctype
                ep["request_schema"] = resolve(media.get("schema"))
            security = op.get("security", doc.get("security"))
            ep["auth"] = ", ".join(sorted({k for s in security or [] for k in s})) or None
            for status, resp in (op.get("responses") or {}).items():
                content = (resp or {}).get("content") or {}
                media = content.get("application/json") or (next(iter(content.values())) if content else {})
                example = media.get("example") if isinstance(media, dict) else None
                if example is None and isinstance(media, dict) and media.get("examples"):
                    example = next(iter(media["examples"].values())).get("value")
                ep["examples"].append({
                    "name": (resp or {}).get("description", "")[:80],
                    "status": int(status) if str(status).isdigit() else status,
                    "schema": resolve(media.get("schema")) if isinstance(media, dict) and media.get("schema") else (infer(example) if example is not None else None),
                    "_body": example,
                })
            endpoints.append(ep)
    info = {"name": (doc.get("info") or {}).get("title"), "format": "openapi-%s" % doc.get("openapi", "3"), "collection_variables": [], "servers": len(doc.get("servers") or [])}
    return endpoints, info


# --------------------------------------------------------------------------- driver
def load_source(source: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if os.path.isdir(source):
        return from_v3_dir(source)
    with open(source, encoding="utf-8") as fh:
        text = fh.read()
    doc = try_json(text)
    if doc is None:
        doc = load_simple_yaml(text)
    if not isinstance(doc, dict):
        raise SystemExit("Unrecognized source: %s" % source)
    if "openapi" in doc or "swagger" in doc:
        return from_openapi(doc)
    if "item" in doc and "info" in doc:
        return from_v21(doc)
    if doc.get("collection") and isinstance(doc["collection"], dict) and "item" in doc["collection"]:
        return from_v21(doc["collection"])          # Postman API envelope
    if _find_kind(doc, "http-request"):
        return from_v3_json(doc)
    raise SystemExit("Unrecognized collection format: %s" % source)


def referenced_variables(endpoints: List[Dict[str, Any]], source_text: str) -> List[str]:
    return sorted({v for v in VAR_REF.findall(source_text) if not v.startswith("$")})


def write_fixtures(endpoints: List[Dict[str, Any]], directory: str) -> None:
    written: set = set()
    for ep in endpoints:
        feature = slug(ep["folder"].split("/")[-1]) if ep["folder"] else "api"
        target = os.path.join(directory, feature)
        for ex in ep["examples"]:
            body = ex.get("_body")
            if body is None:
                continue
            os.makedirs(target, exist_ok=True)
            fname = "%s_%s.json" % (slug(ep["name"]), ex.get("status") or "example")
            path = os.path.join(target, fname)
            if path in written:                      # several examples share a status code
                fname = "%s_%s_%s.json" % (slug(ep["name"]), ex.get("status") or "example", slug(ex.get("name") or "variant"))
                path = os.path.join(target, fname)
            written.add(path)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(redact(body), fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            ex["fixture"] = os.path.relpath(path).replace(os.sep, "/")
        sample = ep.get("_request_sample")
        if sample is not None:
            os.makedirs(target, exist_ok=True)
            path = os.path.join(target, "%s_request.json" % slug(ep["name"]))
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(redact(sample), fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            ep["request_fixture"] = os.path.relpath(path).replace(os.sep, "/")


def to_markdown(endpoints: List[Dict[str, Any]], info: Dict[str, Any], variables: List[str]) -> str:
    out = ["# API contract — %s" % (info.get("name") or "collection"), ""]
    out.append("Source format: `%s` · Endpoints: %d" % (info.get("format"), len(endpoints)))
    if variables:
        out.append("Variables referenced (names only; values live in environments): " + ", ".join("`%s`" % v for v in variables))
    out.append("")
    gaps = []
    for ep in endpoints:
        out.append("## %s `%s` — %s" % (ep["method"], ep["path"] or "/", ep["name"]))
        meta = []
        if ep["folder"]:
            meta.append("folder: %s" % ep["folder"])
        meta.append("auth: %s" % (ep["auth"] or "none declared"))
        if ep["headers"]:
            meta.append("headers: " + ", ".join(ep["headers"]))
        out.append(" · ".join(meta))
        if ep["description"]:
            out.append("> " + ep["description"])
        if ep["path_params"]:
            out.append("Path params: " + ", ".join(p["key"] for p in ep["path_params"]))
        if ep["query"]:
            out.append("Query: " + ", ".join(q["key"] + ("=" + q["example"] if q.get("example") else "") for q in ep["query"]))
        if ep["request_body"]:
            out.append("Request body (%s)%s:" % (ep["request_body"], " → " + ep["request_fixture"] if ep.get("request_fixture") else ""))
            out += schema_lines(ep["request_schema"])
        if not ep["examples"]:
            out.append("Responses: ⚠ no saved examples (gap: ask backend for a sample or an agreed mock)")
            gaps.append("%s %s: no response examples" % (ep["method"], ep["path"]))
        for status, group in group_by_status(ep["examples"]):
            names = ", ".join("\"%s\"" % ex["name"] for ex in group if ex.get("name"))
            fixtures = ", ".join(ex["fixture"] for ex in group if ex.get("fixture"))
            out.append("Response %s%s%s:" % (status or "?", " " + names if names else "", " → " + fixtures if fixtures else ""))
            merged = None
            for ex in group:
                if ex.get("schema"):
                    merged = merge(merged, ex["schema"])
            out += schema_lines(merged)
        statuses = {ex.get("status") for ex in ep["examples"]}
        if ep["examples"] and not any(isinstance(s, int) and s >= 400 for s in statuses):
            gaps.append("%s %s: no error example (4xx/5xx shape unknown)" % (ep["method"], ep["path"]))
        out.append("")
    if gaps:
        out.append("## Contract gaps")
        out += ["- " + g for g in gaps]
    return "\n".join(out) + "\n"


def group_by_status(examples: List[Dict[str, Any]]) -> List[Tuple[Any, List[Dict[str, Any]]]]:
    groups: Dict[Any, List[Dict[str, Any]]] = {}
    for ex in examples:
        groups.setdefault(ex.get("status"), []).append(ex)
    return list(groups.items())


def strip_private(endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    clean = []
    for ep in endpoints:
        e = {k: v for k, v in ep.items() if not k.startswith("_")}
        e["examples"] = [{k: v for k, v in ex.items() if not k.startswith("_")} for ex in ep["examples"]]
        merged_by_status = {}
        for status, group in group_by_status(ep["examples"]):
            merged = None
            for ex in group:
                if ex.get("schema"):
                    merged = merge(merged, ex["schema"])
            merged_by_status[str(status)] = merged
        e["response_schemas"] = merged_by_status
        clean.append(e)
    return clean


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source")
    parser.add_argument("--format", choices=["md", "json"], default="md")
    parser.add_argument("--out")
    parser.add_argument("--filter", action="append", default=[], help="keep endpoints whose name/path/folder contains TEXT (repeatable, OR)")
    parser.add_argument("--fixtures-dir", help="write redacted example bodies as JSON fixtures here")
    parser.add_argument("--list", action="store_true", help="only list endpoints (method, path, name, folder)")
    args = parser.parse_args(argv)

    endpoints, info = load_source(args.source)
    if args.filter:
        needles = [f.lower() for f in args.filter]
        endpoints = [e for e in endpoints if any(n in (e["name"] + " " + e["path"] + " " + e["folder"]).lower() for n in needles)]
    if args.list:
        for e in endpoints:
            print("%-7s %-50s %s%s" % (e["method"], e["path"] or "/", e["name"], "  [%s]" % e["folder"] if e["folder"] else ""))
        return 0
    source_text = ""
    if os.path.isfile(args.source):
        with open(args.source, encoding="utf-8") as fh:
            source_text = fh.read()
    variables = sorted(set(info.get("collection_variables") or []) | set(referenced_variables(endpoints, source_text)))
    if args.fixtures_dir:
        write_fixtures(endpoints, args.fixtures_dir)
    if args.format == "json":
        payload = json.dumps({"info": info, "variables": variables, "endpoints": strip_private(endpoints)}, indent=2, ensure_ascii=False)
    else:
        payload = to_markdown(endpoints, info, variables)
    if args.out:
        if os.path.dirname(args.out):
            os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload)
        print("wrote %s (%d endpoints)" % (args.out, len(endpoints)))
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
