#!/usr/bin/env python3
"""
LeetCode Solution Tracker
Run this script after solving a problem on LeetCode.
It updates README.md and commits the change to GitHub automatically.

Usage:
    python add_solution.py
"""

import re
import subprocess
from datetime import date


def get_difficulty():
    while True:
        d = input("Difficulty (Easy / Medium / Hard): ").strip().capitalize()
        if d in ("Easy", "Medium", "Hard"):
            return d
        print("  Please enter Easy, Medium, or Hard.")


def parse_existing_rows(content):
    """Return list of problem numbers already in the table."""
    return set(re.findall(r"^\|\s*(\d+)\s*\|", content, re.MULTILINE))


def build_row(number, title, lc_link, solution_link, difficulty):
    return f"| {number} | [{title}]({lc_link}) | {difficulty} | [View Solution]({solution_link}) |"


def update_readme(number, title, lc_link, solution_link, difficulty):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    existing = parse_existing_rows(content)
    if number in existing:
        print(f"\n⚠️  Problem {number} already exists in README. Skipping.")
        return False

    new_row = build_row(number, title, lc_link, solution_link, difficulty)

    # Insert row in sorted order inside the table
    lines = content.splitlines()
    table_rows = []
    insert_idx = None

    for i, line in enumerate(lines):
        m = re.match(r"^\|\s*(\d+)\s*\|", line)
        if m:
            table_rows.append((int(m.group(1)), i))

    if table_rows:
        # Find correct sorted position
        for prob_num, line_idx in table_rows:
            if int(number) < prob_num:
                insert_idx = line_idx
                break
        if insert_idx is None:
            # Append after last row
            insert_idx = table_rows[-1][1] + 1
        lines.insert(insert_idx, new_row)
    else:
        # No rows yet — append after the header separator line
        for i, line in enumerate(lines):
            if re.match(r"^\|[-| ]+\|$", line):
                lines.insert(i + 1, new_row)
                break

    # Update solved count badge
    total = len(table_rows) + 1
    updated = "\n".join(lines)
    updated = re.sub(
        r"(SQL|Python)%20Problems%20Solved-\d+-",
        lambda m: m.group(0).replace(
            m.group(0).split("-")[1], str(total)
        ),
        updated,
    )

    # Update last updated date
    updated = re.sub(
        r"\*Last updated:.*?\*",
        f"*Last updated: {date.today()}*",
        updated,
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"\n✅ README.md updated with problem {number}.")
    return True


def git_commit(number, title):
    try:
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Add {number}. {title}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        print("🚀 Pushed to GitHub successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Git error: {e}")
        print("   Make sure you're inside a git repo and have push access.")


def main():
    print("=" * 45)
    print("   LeetCode Solution Tracker")
    print("=" * 45)

    number   = input("Problem number (e.g. 175): ").strip()
    title    = input("Problem title  (e.g. Combine Two Tables): ").strip()
    lc_link  = input("LeetCode URL   (e.g. https://leetcode.com/problems/...): ").strip()
    sol_link = input("Your submission URL (paste from LeetCode): ").strip()
    diff     = get_difficulty()

    updated = update_readme(number, title, lc_link, sol_link, diff)

    if updated:
        push = input("\nPush to GitHub now? (y/n): ").strip().lower()
        if push == "y":
            git_commit(number, title)
        else:
            print("📝 README updated locally. Run `git push` when ready.")

    print("\nDone! 🎉")


if __name__ == "__main__":
    main()
