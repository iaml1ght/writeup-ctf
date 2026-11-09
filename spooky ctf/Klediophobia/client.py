"""Player client for the fictional audit service (Python standard library only)."""
import argparse
import json
from urllib.request import Request, urlopen


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--server", default="http://127.0.0.1:8000")
    sub = p.add_subparsers(dest="action", required=True)
    sub.add_parser("challenge")
    submit = sub.add_parser("submit")
    submit.add_argument("session_id")
    submit.add_argument("signature_base64")
    args = p.parse_args()
    if args.action == "challenge":
        url, body = args.server.rstrip("/") + "/challenge", None
    else:
        url = args.server.rstrip("/") + "/verify"
        body = json.dumps({"session_id": args.session_id, "signature": args.signature_base64}).encode()
    req = Request(url, data=body, headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=10) as response:
        print(response.read().decode())


if __name__ == "__main__":
    main()
