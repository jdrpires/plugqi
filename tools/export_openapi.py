"""Fetch OpenAPI JSON from a running FastAPI server and save to docs/openapi.json.

Usage:
    python tools/export_openapi.py --url http://127.0.0.1:8000/openapi.json --out docs/openapi.json
"""
import argparse
import sys
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', required=True, help='Full URL to openapi.json')
    p.add_argument('--out', required=True, help='Output file path (e.g. docs/openapi.json)')
    args = p.parse_args()

    try:
        resp = requests.get(args.url)
        resp.raise_for_status()
    except Exception as e:
        print(f'Error fetching {args.url}: {e}', file=sys.stderr)
        sys.exit(2)

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(resp.text)

    print(f'Wrote {args.out}')


if __name__ == '__main__':
    main()
