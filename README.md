# Readme

The source code in this repository shows a simple example of how to build
semantic search applications with ZIR Semantic Search.

## Data

`/src/main/resources`, Contains customer reviews for three San Francisco hotels.

## Programs

## opinrank2json.py

This program converts reviews from Opinrank's tab-separated into documents that
can be dragged and dropped into the ZIR Console. It also saves the documents in
a SQLite database which is used when running queries.

```bash
declare -a files=(
  "usa_san_francisco_best_western_tuscan_inn_fisherman_s_wharf_a_kimpton_hotel"
  "usa_san_francisco_sheraton_fisherman_s_wharf_hotel"
  "usa_san_francisco_the_westin_st_francis")

for FILE in "${files[@]}"
do
  ./src/main/opinrank2json.py\
      --input-file src/main/resources/${FILE}\
      --output-dir ./out\
      --sqlite ./out/reviews.db
done
```

## hotels.py

This program provides a line-oriented interpreter for running queries against a
corpus of hotel reviews. Here's a sample session:

```
$ ./src/main/hotels.py\
    --customer-id 1526022105\
    --corpus-id 14\
    --app-client-id 20hestglli47sd563mbq01ha9e\
    --auth-domain https://zir-prod-1526022105.auth.us-west-2.amazoncognito.com
App Client Secret:
Welcome to hotel search. Ask a question and get an answer.
(hotel) are the rooms spacious?

Very Nice --Would recommend to my friends
in a convenient location. The Tuscan Inn fit that well. Very
comfortable stay and got a good deal on Orbitz to boot. Only drawback
is room size. We started w/ a king w/ sofa bed for my son but we were
tripping on each other so we upgraded to a suite. We also moved from a
Best Western Fishermans Wharf reviewed on Apr 12 2008

Loved the Tuscan Inn
We did it all. Hotel was Very nicely furnished, staff was Very
helpful. The rooms are just a tad bit small---but we didn't spend much
time in our room. Very well cleaned. I will continue to recommend this
property.
Best Western Fishermans Wharf reviewed on Jan 10 2007

Fun Hotel in the Heart of Everything
staff was very nice. The lobby has a good vibe. We had a room on the
top floor with dormer windows. I would request these rooms, because
they feel bigger. The bathroom was standard issue on the small side.
We really enjoyed the pool. It is hard to find an outdoor pool in
Sheraton Fisherman's Wharf Hotel reviewed on Jul 15 2009


Returned 3 results in 0.213 secs.
```
