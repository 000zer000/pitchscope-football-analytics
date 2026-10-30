# Separate source and software rights

Scope: FIFA World Cup 2022, competition 43 / season 106, 64 matches.
Official source: https://github.com/hudl/open-data
Pinned commit: `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`.

The repository README, five-page LICENSE.pdf (dated 8 September 2023), JSON files
and event specification v4 were inspected before implementation:

- https://github.com/hudl/open-data/blob/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/LICENSE.pdf
- https://github.com/hudl/open-data/blob/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/README.md
- https://github.com/hudl/open-data/blob/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/doc/Open%20Data%20Events%20v4.0.0.pdf

The README addresses sharing analysis with attribution and logo. The Public Data
User Agreement governs research use and restricts redistribution of data to third
parties (1.2.1) and commercial exploitation of data or derived analysis (1.2.2).
It requires the logo for publication (1.4) and requests user registration of
interest on the StatsBomb website (2.2). No form, account or legal acceptance was
submitted on the user's behalf.

Practical implementation:

- Original code is MIT licensed. StatsBomb data and brand assets are excluded.
- Raw JSON cache is local and excluded from Git, source archives, Docker images
  and CI fixtures. No database dump or public API was distributed.
- Event inspection is local. An eventual public/commercial demo needs a separate
  review of provider terms, particularly access to source attributes.
- The official logo comes from `img/SB - Icon Lockup - Colour positive.png` at
  the pinned commit. It appears in the UI and PDF. Its hash is recorded in
  `docs/asset-provenance.json`. It was not recreated or relicensed under MIT.
- Screenshots and the PDF are attributed descriptive analyses, not raw-data dumps.

The official media pack https://statsbomb.com/media-pack/ redirects to Bynder.
The logo supplied in the official repository was used. Provider availability and
accuracy are not guaranteed by PitchScope. No publication or deployment occurred.
