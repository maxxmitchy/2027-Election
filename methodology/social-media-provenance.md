# Social Media Provenance

Social-media records require provenance stronger than a screenshot alone.

## Source forms

- `original_post`: directly inspected platform record.
- `repost`: a repost/retweet/share of another post; preserve both the reposting account and original-post reference where available.
- `quoted_post`: a post containing a quotation/repost of another post; preserve the quoted object separately.
- `screenshot`: image evidence without direct platform provenance; never equivalent to an original platform record.
- `archive_capture`: independently archived capture; preserve archive URL, capture date and original URL when known.
- `third_party_quotation`: another source quoting a social-media statement without direct access to the original.
- `deleted_post`: original record no longer publicly available; use archive or contemporaneous evidence where possible and label the deletion state.

## Authenticity

Account authenticity is recorded separately from content truth. A verified/authenticated account increases confidence that the account belongs to the attributed person or organization; it does not establish that the post's underlying claim is true.

## Date certainty

Preserve exact timestamp when available. If only a date, month, or approximate period is known, record the lower precision rather than inventing a timestamp.

## Statement versus truth

A source can establish `Person X said Y` through direct or well-provenanced evidence. A separate claim must be evaluated to determine whether `Y is true`.

## Screenshots

Screenshots should preserve capture provenance, file/hash identity where implemented, surrounding context, claimed URL, claimed account and any archive reference. They should be classified as lower-directness evidence unless independently corroborated.
