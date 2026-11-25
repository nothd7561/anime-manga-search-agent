import operator
import sqlite3
import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parents[3]
db_path = project_dir / 'data' / 'processed' / 'aniscope.db'

OPS = {'==': operator.eq, '<=': operator.le}

# (description, sql returning one number, comparison, expected)
CHECKS = [
    ('anime count',
     "SELECT COUNT(*) FROM media WHERE type = 'ANIME'", '==', 2000),
    ('manga (JP) count',
     "SELECT COUNT(*) FROM media WHERE type = 'MANGA' AND country = 'JP'", '==', 3000),
    ('manhwa (KR) count',
     "SELECT COUNT(*) FROM media WHERE type = 'MANGA' AND country = 'KR'", '==', 2000),
    ('releasing manga marked length-known',
     "SELECT COUNT(*) FROM media WHERE type = 'MANGA' AND status = 'RELEASING' AND length_known = 1", '==', 0),
    ('scores outside 0-100',
     "SELECT COUNT(*) FROM media WHERE average_score NOT BETWEEN 0 AND 100", '==', 0),
    ('empty-string descriptions',
     "SELECT COUNT(*) FROM media WHERE description_clean = ''", '==', 0),
    ('titles with no genres (max 0.1% of 7,000)',
     "SELECT COUNT(*) FROM media WHERE id NOT IN (SELECT media_id FROM genres)", '<=', 7),
]


def run_checks(db_path):
    failures = 0
    connection = sqlite3.connect(db_path)
    try:
        for description, sql, comparison, expected in CHECKS:
            actual = connection.execute(sql).fetchone()[0]
            passed = OPS[comparison](actual, expected)
            print(f"{'PASS' if passed else 'FAIL'}: {description} "
                  f"(got {actual}, expected {comparison} {expected})")
            failures += not passed

        broken = connection.execute('PRAGMA foreign_key_check').fetchall()
        passed = broken == []
        print(f"{'PASS' if passed else 'FAIL'}: foreign keys (broken links: {len(broken)})")
        failures += not passed
    finally:
        connection.close()
    return failures


if __name__ == '__main__':
    failures = run_checks(db_path)
    total = len(CHECKS) + 1
    print(f'{total - failures}/{total} checks passed')
    sys.exit(1 if failures else 0)