#!/usr/bin/env python3
"""Parse OpinRank hotel reviews and save each review as a JSON document."""

import argparse
import json
import logging
import mmh3
import os
import sqlite3
import sys

def eprint(*args, **kwargs):
    """Print to stderr.
    
    Ref: https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    """
    print(*args, file=sys.stderr, **kwargs)

def main(args):
    if not os.path.isfile(args.input_file):
        eprint(f"{args.input_file} does not exist.")
        sys.exit(1)

    con = sqlite3.connect(args.sqlite_out)
    cur = con.cursor()
    init_db(cur)

    with open(args.input_file, encoding="utf8", errors="ignore") as infile:
        num_written = 0
        for line in infile:
            parts = line.split("\t")

            doc_id = mmh3.hash128(line, 42, True)  # True is the x64 version
            date, title, text = parts[0], parts[1], parts[2]
            if not text:  # Skip empty reviews
                continue
            num_written += 1

            hotel = os.path.basename(args.input_file)
            if hotel.startswith("usa_san_francisco"):
                hotel = hotel[18:]

            json_doc = {
                "documentId": str(doc_id),
                "title": title,
                "metadataJson": '{"date": "%s", "hotel": "%s"}' % (date, hotel),
                "section": [
                    { "text": text }
                ]
            }
            doc = json.dumps(json_doc, sort_keys=True, indent=4)

            outfile = os.path.join(args.output_dir, str(doc_id)) + ".json"
            with open(outfile, 'w') as outfile:
                outfile.write(doc)
            
            cur.execute("insert or ignore into reviews values (?, ?, ?, ?, ?)",
                        (str(doc_id), title, date, hotel, text))

        print(f"Wrote {num_written} reviews to {args.output_dir} "
              f"and {args.sqlite_out}.")
        con.commit()
        con.close()


def init_db(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            doc_id text primary key,
            title text,
            date text,
            hotel text,
            review text)
    ''')


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Extract OpinRank hotel reviews.")

  parser.add_argument("--input-file", dest="input_file",
                      help="Location of the input file.",
                      metavar="FILE")
  parser.add_argument("--output-dir", dest="output_dir",
                      default="./out",
                      help="Location where hotel reviews will be exported as JSON.",
                      metavar="DIR")
  parser.add_argument("--sqlite", dest="sqlite_out",
                      default="./out/reviews.db",
                      help="Database file for hotel reviews.",
                      metavar="FILE")
  args = parser.parse_args()

  root = logging.getLogger()
  root.setLevel(logging.DEBUG)

  logging.basicConfig(
      format="%(asctime)s %(thread)-4d:%(levelname)-8s %(message)s",
      level=logging.INFO)
  main(args)

