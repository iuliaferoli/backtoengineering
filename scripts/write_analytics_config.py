#!/usr/bin/env python3
"""Write the public analytics config consumed by docs/js/site-analytics.js."""

from __future__ import annotations

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "docs" / "js" / "analytics-config.js"


def main() -> None:
    config = {
        "scriptUrl": os.getenv("UMAMI_SCRIPT_URL", ""),
        "websiteId": os.getenv("UMAMI_WEBSITE_ID", ""),
        "domains": os.getenv(
            "UMAMI_DOMAINS",
            "www.backtoengineering.com,backtoengineering.com",
        ),
    }
    OUTPUT_FILE.write_text(
        "window.B2E_ANALYTICS = "
        + json.dumps(config, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    if config["scriptUrl"] and config["websiteId"]:
        print("Analytics config enabled")
    else:
        print("Analytics config disabled; UMAMI_SCRIPT_URL or UMAMI_WEBSITE_ID is missing")


if __name__ == "__main__":
    main()
