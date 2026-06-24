# REVIEW

## Provided module review (deliverable)

Review of [`public/review/bubble_service.py`](public/review/bubble_service.py) and its test —
what's broken, why, and how to fix it. _To be written in story 7.2 (EP-7)._

## Open items to revisit before submission

Our own decisions flagged for a final pass — clear each once confirmed.

- [ ] **Auth session design (stories 2.1 / 2.2).** Stateless signed-cookie sessions. Confirm the
  token TTL is short, a random `jti` is included, logout clears the cookie, and the
  "logout can't revoke a copied token" tradeoff is covered in [THREATS.md](THREATS.md) (T1).
  Review once story 2.2 lands and clear if satisfied.
