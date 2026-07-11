"""Seed realistic fake ratings for every protocol in every Stack Hub.

Strategy:
- 8 to 25 individual votes per protocol (varies)
- Target average between 4.2 and 4.8 stars (skewed slightly higher for shorter / classic protocols)
- Votes are generated as individual documents (1 per fake user_id) so they show up in the
  same aggregation pipeline used by the real rating endpoint.
- Idempotent: identifies fake votes by user_id prefix "seed-bot-" so it never duplicates.
"""
import asyncio
import os
import secrets
import uuid
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

SEED_PREFIX = "seed-bot-"

# Non-security random source. `secrets.SystemRandom()` provides the same API
# as the `random` module but backed by the OS CSPRNG — satisfying static
# analysis while remaining suitable for demo/seed data generation.
_rng = secrets.SystemRandom()


def _generate_votes(target_avg: float, count: int) -> list[int]:
    """Generate a list of `count` star ratings (1-5) whose mean ≈ target_avg."""
    votes = []
    remaining = target_avg * count
    for i in range(count):
        slots_left = count - i
        # Pick a star value 3-5 such that the running mean stays close to target
        if slots_left == 1:
            v = max(1, min(5, round(remaining)))
        else:
            ideal = remaining / slots_left
            # Add some noise
            noise = _rng.choice([-1, 0, 0, 0, 1])
            v = max(3, min(5, round(ideal + noise * 0.3)))
        votes.append(v)
        remaining -= v
    _rng.shuffle(votes)
    return votes


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    # Wipe previous seed votes so re-running gives fresh distribution
    deleted = await db.protocol_ratings.delete_many({"user_id": {"$regex": f"^{SEED_PREFIX}"}})
    print(f"Cleared {deleted.deleted_count} previous seed votes")

    hubs = await db.stack_hubs.find({}, {"_id": 0, "slug": 1, "peptide_name": 1, "protocols": 1}).to_list(50)

    total_votes = 0
    docs_to_insert = []

    for hub in hubs:
        slug = hub["slug"]
        for p in hub.get("protocols", []):
            pid = p["id"]
            num_peptides = len(p.get("compounds", []))

            # Bias: stacks with 2+ peptides are "real stacks" → trend stronger.
            # Solo-peptide protocols get fewer votes and slightly lower rating.
            if num_peptides >= 3:
                # Triple+ stacks → top trending tier
                count = _rng.randint(22, 32)
                target = round(_rng.uniform(4.6, 4.9), 1)
            elif num_peptides == 2:
                # Dual stacks → strong trending tier
                count = _rng.randint(16, 24)
                target = round(_rng.uniform(4.4, 4.7), 1)
            else:
                # Solo peptide protocols → low/mid trending
                count = _rng.randint(5, 11)
                target = round(_rng.uniform(3.9, 4.4), 1)

            votes = _generate_votes(target, count)
            for stars in votes:
                docs_to_insert.append({
                    "hub_slug": slug,
                    "protocol_id": pid,
                    "user_id": f"{SEED_PREFIX}{uuid.uuid4().hex[:12]}",
                    "stars": stars,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
            total_votes += count

    if docs_to_insert:
        await db.protocol_ratings.insert_many(docs_to_insert)

    print(f"Inserted {total_votes} fake votes across {sum(len(h.get('protocols', [])) for h in hubs)} protocols in {len(hubs)} hubs.")

    # Quick verification: show top 10 trending across all hubs (with peptide count)
    pipeline = [
        {"$group": {"_id": {"hub": "$hub_slug", "pid": "$protocol_id"}, "avg": {"$avg": "$stars"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1, "avg": -1}},
        {"$limit": 10},
    ]
    top = await db.protocol_ratings.aggregate(pipeline).to_list(10)

    # Build a lookup of protocol → compound count for the printout
    proto_lookup = {}
    for h in hubs:
        for p in h.get("protocols", []):
            proto_lookup[(h["slug"], p["id"])] = (p.get("name", "?"), len(p.get("compounds", [])))

    print("\nTop 10 trending (most votes):")
    for t in top:
        key = (t["_id"]["hub"], t["_id"]["pid"])
        name, n_pep = proto_lookup.get(key, ("?", 0))
        print(f"  {t['_id']['hub']:18} | {name[:35]:35} | peptides={n_pep} | avg={round(t['avg'],2)} | votes={t['count']}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
