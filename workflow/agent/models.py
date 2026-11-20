"""Model ids for the three roles. ADR-006."""

ANALYST = "claude-haiku-4-5"
BUILDER = "claude-sonnet-4-6"
REVIEWER = "claude-sonnet-4-5"
MONOLITH = "claude-sonnet-4-6"

# A healthy TinyDB change in A2 was under about 320_000 tokens.
# The cap sits above a spec, a design, a build and a review, and stops a loop.
TOKEN_CAP = 500_000
MAX_TOKENS = 4096
