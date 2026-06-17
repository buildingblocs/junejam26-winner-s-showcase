#!/usr/bin/env python3
"""Move a rebuilt Unity game's wasm/data to R2 and point its index.html there.

Usage: python3 tools/r2_finalize.py <slug> [<slug> ...]
For each slug it: uploads public/play/<slug>/Build/<slug>.wasm and .data to R2
(overwriting the keys), repoints index.html to the R2 URLs with a ?v= cache
buster (content changed), and deletes the local wasm/data so they leave the
deploy. Forces IPv4 (the IPv6 path to R2 fails TLS on this network)."""
import socket, sys, os, re, boto3
from botocore.config import Config

_orig = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _orig(*a, **k) if r[0] == socket.AF_INET]

creds = dict(l.strip().split("=", 1) for l in open(".r2_creds") if "=" in l)
s3 = boto3.client("s3", endpoint_url=creds["R2_ENDPOINT"],
    aws_access_key_id=creds["R2_ACCESS_KEY_ID"], aws_secret_access_key=creds["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", region_name="auto"))
BUCKET = "junejam-showcase"
PUBLIC = "https://pub-be8869d68a2b4911bc34532d32ceb12b.r2.dev"
VER = "r2"   # cache-buster query value

for g in sys.argv[1:]:
    bd = f"site/public/play/{g}/Build"
    for fn, ct in [(f"{g}.wasm", "application/wasm"), (f"{g}.data", "application/octet-stream")]:
        key = f"play/{g}/Build/{fn}"
        s3.upload_file(os.path.join(bd, fn), BUCKET, key, ExtraArgs={"ContentType": ct})
        print("uploaded", key)
    wasm_url = f"{PUBLIC}/play/{g}/Build/{g}.wasm?v={VER}"
    data_url = f"{PUBLIC}/play/{g}/Build/{g}.data?v={VER}"
    idx = f"site/public/play/{g}/index.html"
    c = open(idx).read()
    c = c.replace(f'codeUrl: buildUrl + "/{g}.wasm",', f'codeUrl: "{wasm_url}",')
    c = c.replace(f'dataUrl: buildUrl + "/{g}.data",', f'dataUrl: "{data_url}",')
    assert wasm_url in c and data_url in c, f"{g}: repoint failed"
    open(idx, "w").write(c)
    os.remove(os.path.join(bd, f"{g}.wasm"))
    os.remove(os.path.join(bd, f"{g}.data"))
    print(f"{g}: repointed to R2 (?v={VER}) and removed local wasm/data")
print("DONE")
