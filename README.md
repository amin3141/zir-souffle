# Readme

The source code in this repository shows a simple example of how to build
semantic search applications with ZIR Semantic Search.

## Data

`/src/main/resources`, Contains customer reviews for three San Francisco hotels.

## Programs

## opinrank2json.py

```bash
FILE=usa_san_francisco_best_western_tuscan_inn_fisherman_s_wharf_a_kimpton_hotel

./src/main/opinrank2json.py\
    --input-file src/main/resources/${FILE}\
    --output-dir ./out\
    --sqlite ./out/reviews.db
```