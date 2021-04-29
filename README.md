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

