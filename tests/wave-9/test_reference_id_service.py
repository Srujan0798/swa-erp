import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime

from src.backend.services.reference_id_service import (
    generate_reference_id,
    get_current_seq,
)
from tests.conftest import TestingSessionLocal


def _make_session():
    return TestingSessionLocal()


class TestBasicGeneration:
    def test_first_id_for_new_type_is_seq_001(self, db_session):
        rid = generate_reference_id(db_session, "TST")
        year = datetime.now(UTC).year
        assert rid == f"SWA-{year}-TST-001"

    def test_increments_monotonically(self, db_session):
        year = datetime.now(UTC).year
        ids = [generate_reference_id(db_session, "TST") for _ in range(5)]
        expected = [f"SWA-{year}-TST-{i:03d}" for i in range(1, 6)]
        assert ids == expected

    def test_format_matches_swa_year_type_seq(self, db_session):
        rid = generate_reference_id(db_session, "TST")
        assert re.match(r"^SWA-\d{4}-TST-\d{3}$", rid), f"bad format: {rid}"

    def test_get_current_seq_starts_at_zero(self, db_session):
        assert get_current_seq(db_session, "TST") == 0

    def test_get_current_seq_reflects_increments(self, db_session):
        generate_reference_id(db_session, "TST")
        generate_reference_id(db_session, "TST")
        assert get_current_seq(db_session, "TST") == 2


class TestIsolationBetweenEntityTypes:
    def test_two_types_have_independent_counters(self, db_session):
        year = datetime.now(UTC).year
        a = generate_reference_id(db_session, "AAA")
        b = generate_reference_id(db_session, "BBB")
        a2 = generate_reference_id(db_session, "AAA")
        b2 = generate_reference_id(db_session, "BBB")
        assert a == f"SWA-{year}-AAA-001"
        assert b == f"SWA-{year}-BBB-001"
        assert a2 == f"SWA-{year}-AAA-002"
        assert b2 == f"SWA-{year}-BBB-002"

    def test_counter_never_collides_across_types(self, db_session):
        seen = set()
        for t in ("AAA", "BBB", "CCC"):
            for _ in range(10):
                rid = generate_reference_id(db_session, t)
                assert rid not in seen, f"collision: {rid}"
                seen.add(rid)


class TestYearKeying:
    def test_year_is_part_of_format(self, db_session):
        year = datetime.now(UTC).year
        rid = generate_reference_id(db_session, "TST")
        assert f"SWA-{year}-" in rid

    def test_counter_is_per_year(self, db_session):
        generate_reference_id(db_session, "TST")
        assert get_current_seq(db_session, "TST") == 1
        assert get_current_seq(db_session, "TST", year=2099) == 0


class TestConcurrency:
    def test_50_parallel_calls_yield_gapless_sequential_ids(self):
        n = 50
        entity_type = "TKN"

        def worker(_i):
            s = _make_session()
            try:
                return generate_reference_id(s, entity_type)
            finally:
                s.close()

        with ThreadPoolExecutor(max_workers=n) as ex:
            futures = [ex.submit(worker, i) for i in range(n)]
            ids = [f.result() for f in as_completed(futures)]

        year = datetime.now(UTC).year
        assert len(ids) == n
        assert len(set(ids)) == n, f"duplicate ids produced: {ids}"

        suffix_set = set()
        for rid in ids:
            assert rid.startswith(f"SWA-{year}-{entity_type}-")
            suffix = rid.split("-")[-1]
            suffix_set.add(suffix)
        assert len(suffix_set) == n, f"got suffixes {sorted(suffix_set)}"

        seqs = sorted(int(rid.split("-")[-1]) for rid in ids)
        assert seqs == list(range(1, n + 1)), f"expected 1..{n}, got {seqs}"

        verify = _make_session()
        try:
            final = get_current_seq(verify, entity_type)
        finally:
            verify.close()
        assert final == n
