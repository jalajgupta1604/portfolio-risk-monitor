"""Sector concentration risk scoring using a normalized Herfindahl index."""


def sector_concentration_score(sector_weights: dict[str, float]) -> float:
    """Compute sector concentration score (0–100) from a normalized Herfindahl index.

    The Herfindahl-Hirschman Index (HHI) is the sum of squared market shares.
    - Perfectly diversified (N equal sectors): HHI = 1/N
    - Fully concentrated (1 sector = 100%): HHI = 1.0

    We normalize so that:
    - 0 = perfectly diversified across many sectors
    - 100 = fully concentrated in a single sector
    """
    if not sector_weights:
        return 0.0

    n = len(sector_weights)
    if n <= 1:
        return 100.0

    hhi = sum(w ** 2 for w in sector_weights.values())

    # Normalize: HHI ranges from 1/n (equal) to 1.0 (concentrated)
    min_hhi = 1.0 / n
    if hhi <= min_hhi:
        return 0.0

    normalized = (hhi - min_hhi) / (1.0 - min_hhi)
    return min(normalized * 100.0, 100.0)
