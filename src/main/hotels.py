#!/usr/bin/env python3
"""A simple command line interface for running queries against hotel reviews.

The following command line shows how to invoke the program. You can find your
Customer ID in the upper right corner of the admin console when you are logged
in. The Corpus ID is found by clicking the corpus containing the hotel reviews.
The App Client ID can be found on the App Client tab of the Authentication
Screen, and the authentication domain is in the same place.

    python3 src/main/hotels.py\
        --customer-id $CUSTOMER_ID\
        --corpus-id $CORPUS_ID\
        --app-client-id $APP_CLIENT_ID\
        --auth-domain $AUTH_DOMAIN
"""

import argparse
import cmd
import getpass
import json
import os
import sqlite3
import sys
import textwrap
import timeit
from types import SimpleNamespace

from authlib.integrations.requests_client import OAuth2Session
from colorama import init, Style, Fore
import requests


class HotelShell(cmd.Cmd):
    """A shell for interactively running semantic searches on hotel reviews."""

    intro = "Welcome to hotel search. Ask a question and get an answer.\n"
    prompt = "(hotel) "
    url = ""

    def __init__(self, token, corpus_id, customer_id, cursor):
        super().__init__()
        self.token = token
        self.url = "https://h.serving.zir-ai.io:443/v1/query"
        self.corpus_id = corpus_id
        self.customer_id = customer_id
        self.sqlite_cursor = cursor

    def default(self, line):
        data = """
        {
            "query": [
                {
                    "query": "%s",
                    "num_results": 3,
                    "corpus_key": [
                    {
                        "customer_id": %s,
                        "corpus_id": %s
                    }
                    ]
                }
            ]
        }
        """ % (line, self.customer_id, self.corpus_id)

        # Send the request to the server.
        start_time = timeit.default_timer()
        response = requests.post(
            self.url,
            headers={
                "authorization": "Bearer %s" % self.token["access_token"],
                "customer-id": str(self.customer_id)
            },
            data=data)
        elapsed = timeit.default_timer() - start_time
        if response.status_code != 200:
            print("Server returned status code %d." % response.status_code)
        else:
            results = json.loads(
                response.text, object_hook=lambda d: SimpleNamespace(**d))
            response_set = results.responseSet[0]
            print()
            print_responses(response_set, self.sqlite_cursor)
            print(f"\nReturned {len(response_set.response)} results "
                  f"in {elapsed:.3f} secs.\n")


def print_responses(response_set, sqlite_cursor):
    """Print responses to the console."""
    for result in response_set.response:
        doc = response_set.document[result.documentIndex]
        query =  f"""
            SELECT title, date, hotel, review FROM reviews
                WHERE doc_id="{doc.id}"
        """
        for row in sqlite_cursor.execute(query):
            title, date, hotel, fulltext = row
            print(Style.BRIGHT + title)
            if is_title(result):
                print(f"{Style.RESET_ALL}{head(fulltext)}")
            else:
                print(f"{Style.RESET_ALL}{highlight(fulltext, result.text)}")
            print(Style.RESET_ALL + Style.DIM +
                  f"{hotel_name(hotel)} reviewed on {date}" +
                  Style.RESET_ALL)
            print()
            break


def hotel_name(hotel):
    """Returns a human-readable name for a hotel."""
    if hotel == "sheraton_fisherman_s_wharf_hotel":
        return "Sheraton Fisherman's Wharf Hotel"
    if hotel == "the_westin_st_francis":
        return "The Westin St. Francis San Francisco on Union Square"
    if hotel == "best_western_tuscan_inn_fisherman_s_wharf_a_kimpton_hotel":
        return "Best Western Fishermans Wharf"
    return hotel


def highlight(fulltext, snippet):
    """Return a result snippet with context, suitable for terminal display."""
    if snippet in fulltext:
        start = fulltext.index(snippet)
        end = start + len(snippet)

        lines = textwrap.wrap(fulltext)
        start_line = 0
        end_line = len(lines)
        pos = 0

        # Figure out which lines to display, and insert ANSI
        # code to highlight the actual snippet.
        for x, line in enumerate(lines):
            next_pos = pos + len(line)

            color_start = pos <= start < next_pos
            color_end = pos <= end < next_pos

            if color_start and color_end:
                start_line = end_line = x
                ips = start - pos - x   # insertion point
                ipe = end - pos - x     # insertion point
                lines[x] = line[:ips] + Fore.YELLOW + line[ips:ipe] + \
                           Style.RESET_ALL + line[ipe:]
            elif color_start:
                start_line = x
                ip = start - pos - x    # insertion point
                lines[x] = line[:ip] + Fore.YELLOW + line[ip:]
            elif color_end:
                end_line = x
                ip = end - pos - x    # insertion point
                lines[x] = line[:ip] + Style.RESET_ALL + line[ip:]

            pos = next_pos

        # Widen the line selection to include a bit of context.
        if start_line > 0:
            start_line -= 1
        end_line += 2
        return prettify('\n'.join(lines[start_line:end_line]))
    return prettify(snippet)


def head(fulltext):
    """Returns the first three lines of the review."""
    lines = textwrap.wrap(fulltext)
    return prettify('\n'.join(lines[0:3]) + '...')


def is_title(result):
    """Returns true if the result is a title match."""
    for metadatum in result.metadata:
        if metadatum.name == "is_title":
            return metadatum.value == "true"
    return False


def prettify(text):
    """Clean up the text to make it more suitable for display."""
    return text.replace("&amp;", "&").replace("&quot;", "\"")


def token_ep(auth_domain):
    """Construct the token endpoint URL, given the authentication domain."""
    if auth_domain.endswith("/"):
        return "%soauth2/token" % auth_domain
    return "%s/oauth2/token" % auth_domain


def eprint(*args, **kwargs):
    """Print to stderr.

    Ref: https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    """
    print(*args, file=sys.stderr, **kwargs)


def main(args):
    if not os.path.isfile(args.sqlite_out):
        eprint(f"{args.sqlite_out} does not exist.")
        sys.exit(1)

    app_secret = getpass.getpass(prompt='App Client Secret: ')

    # Connect to the SQLite database created by opinrank2json.py.
    con = sqlite3.connect(args.sqlite_out)
    cur = con.cursor()

    # Get the JWT Token
    session = OAuth2Session(args.app_id, app_secret, scope="")
    try:
        token = session.fetch_token(
            token_ep(args.auth_domain), grant_type="client_credentials")
    except:
        eprint("Error obtaining JWT token. Aborting.")
        return

    shell = HotelShell(token, args.corpus_id, args.customer_id, cur)
    shell.cmdloop()    # Start the REPL loop.

if __name__ == "__main__":
    init()
    parser = argparse.ArgumentParser(
        description="Search hotel reviews for information.")

    parser.add_argument("--customer-id", dest="customer_id", required=True,
                        help="Customer ID.",
                        metavar="ID")
    parser.add_argument("--corpus-id", dest="corpus_id", required=True,
                        help="Corpus ID.",
                        metavar="ID")
    parser.add_argument("--app-client-id", dest="app_id", required=True,
                        help="App Client ID.",
                        metavar="ID")
    parser.add_argument("--auth-domain", dest="auth_domain", required=True,
                        help="Authentication domain.",
                        metavar="URL")
    parser.add_argument("--sqlite", dest="sqlite_out",
                        default="./out/reviews.db",
                        help="Database file for hotel reviews.",
                        metavar="FILE")
    args = parser.parse_args()

    main(args)
