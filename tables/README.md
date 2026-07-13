# Tables

This directory contains generated LaTeX table assets and matching CSV exports. Tables I, II, IV, V-matrix, and VI are used by the manuscript. The full static exposure table and full 15-row integrated profile table are retained as supplemental/generated report assets, not duplicated in the main text. Regenerate all table assets with:

```bash
python scripts/generate_publication_assets.py
```

The generator reads the final ScytaleDroid integrated static-runtime alignment bundle and writes source-data/checksum artifacts under `generated/source_data/`.
