# Lint helper only for an already-built Dudley factory image.
# Do not add package installation or overlay logic here; image contents
# come from BuildStream elements and OCI assembly `.bst` files.
FROM ghcr.io/joshyorko/dudley-bluefin:testing

RUN bootc container lint || true
