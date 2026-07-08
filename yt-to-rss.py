#!/usr/bin/env python3
"""
use this to convert a yt takeout subscriptions.csv export into an OPML file for easy importing into RSS readers :3

Usage:
    python3 youtube_subs_to_opml.py subscriptions.csv subscriptions.opml

as takeout csv typically has columns: Channel Id, Channel Url, Channel Title,
(header row present). script designed to be tolerant of column order/casing.
"""

import csv
import sys
import html


def find_column(fieldnames, *candidates):
    lower_map = {f.lower(): f for f in fieldnames}
    for c in candidates:
        if c.lower() in lower_map:
            return lower_map[c.lower()]
    return None


def main():
    if len(sys.argv) != 3:
        print("how 2 use: python3 youtube_subs_to_opml.py <input.csv> <output.opml>")
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    with open(in_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("couldn't read csv header :(")
            sys.exit(1)

        id_col = find_column(reader.fieldnames, "Channel Id", "channel_id", "ChannelId")
        title_col = find_column(reader.fieldnames, "Channel Title", "channel_title", "Title")

        if not id_col:
            print(f"couldn't find a channel ID column :(. Found columns: {reader.fieldnames}")
            sys.exit(1)

        entries = []
        for row in reader:
            channel_id = row.get(id_col, "").strip()
            title = row.get(title_col, "").strip() if title_col else channel_id
            if not channel_id:
                continue
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            html_url = f"https://www.youtube.com/channel/{channel_id}"
            entries.append((title or channel_id, feed_url, html_url))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<opml version="1.0">\n')
        f.write("  <head>\n    <title>YouTube Subscriptions</title>\n  </head>\n")
        f.write("  <body>\n")
        f.write('    <outline text="YouTube Subscriptions" title="YouTube Subscriptions">\n')
        for title, feed_url, html_url in entries:
            safe_title = html.escape(title, quote=True)
            f.write(
                f'      <outline type="rss" text="{safe_title}" title="{safe_title}" '
                f'xmlUrl="{feed_url}" htmlUrl="{html_url}"/>\n'
            )
        f.write("    </outline>\n")
        f.write("  </body>\n")
        f.write("</opml>\n")

    print(f"wrote {len(entries)} channels to {out_path} :3. hope u enjoy!")


if __name__ == "__main__":
    main()