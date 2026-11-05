"""
Seed a realistic IN-PROGRESS demo project, for showcasing what the portal
looks like once it's been in active use for months.

Unlike the Excel import (which only creates a fresh, all-"Not Started"
project), this writes:
  - a project that started months ago and is mid-flight
  - tasks with mixed statuses (Complete / Active / Not Started) and
    partial completed quantities
  - expenditures across categories (~60% of budget burned)
  - daily progress entries on the active tasks
  - a few risks (Open / Mitigated)

Run it against whatever database DATABASE_URL points at:

    # local SQLite (default)
    python seed_demo_project.py

    # against your live Neon DB
    DATABASE_URL='postgresql://...your neon string...' python seed_demo_project.py

Safe to inspect first; it refuses to run twice for the same project number.
"""

import datetime
import sys

from app.core.bootstrap import bootstrap_db
from app.models.database import (
    DailyProgress,
    Expenditure,
    Project,
    Risk,
    SessionLocal,
    Task,
    User,
)

PROJECT_NUMBER = "RVM-2025-014"
TODAY = datetime.date(2026, 5, 15)


def d(year, month, day):
    return datetime.date(year, month, day)


def seed():
    # Make sure tables exist (no admin needed here).
    bootstrap_db(create_admin=False)

    db = SessionLocal()
    try:
        if db.query(Project).filter(Project.project_number == PROJECT_NUMBER).first():
            print(
                f"A project with number {PROJECT_NUMBER} already exists — "
                f"nothing to do. Delete it first if you want to re-seed."
            )
            return

        # Use the admin as PM/creator; fall back to any user; else make a demo PM.
        owner = db.query(User).filter(User.role == "admin").first()
        if not owner:
            owner = db.query(User).first()
        if not owner:
            print(
                "No users exist yet. Run init_db.py (or let the app boot) to "
                "create the admin user first, then re-run this script.",
                file=sys.stderr,
            )
            sys.exit(1)

        # ---- Project: started Sep 2025, runs to Mar 2027, ~60% through ----
        project = Project(
            project_name="Riverside Mall Expansion — Phase 2",
            project_number=PROJECT_NUMBER,
            client="Riverside Property Group",
            pm_user_id=owner.user_id,
            total_budget=18_000_000.00,
            start_date=d(2025, 9, 1),
            target_end_date=d(2027, 3, 31),
            status="active",
            created_by=owner.user_id,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        pid = project.project_id

        # ---- Tasks: mixed states, realistic for May 2026 ----
        # (name, status, p_start, p_finish, budget, unit, total_qty, done_qty)
        task_defs = [
            ("Design & Council Approvals", "Complete", d(2025, 9, 1), d(2025, 11, 30), 1_200_000, "LS", 1, 1),
            ("Site Establishment & Hoarding", "Complete", d(2025, 11, 1), d(2025, 12, 20), 850_000, "LS", 1, 1),
            ("Bulk Earthworks", "Complete", d(2025, 12, 1), d(2026, 2, 15), 2_400_000, "m3", 12000, 12000),
            ("Piling & Foundations", "Complete", d(2026, 2, 1), d(2026, 4, 10), 3_100_000, "piles", 86, 86),
            ("Structural Frame — Level 1-2", "Active", d(2026, 4, 1), d(2026, 6, 30), 3_600_000, "m3", 1800, 1100),
            ("Structural Frame — Level 3-4", "Active", d(2026, 5, 10), d(2026, 8, 15), 3_400_000, "m3", 1700, 240),
            ("MEP First Fix", "Not Started", d(2026, 7, 1), d(2026, 10, 31), 1_900_000, "LS", 1, 0),
            ("Facade & Glazing", "Not Started", d(2026, 9, 1), d(2026, 12, 15), 1_550_000, "m2", 4200, 0),
            ("Internal Fit-out", "Not Started", d(2026, 11, 1), d(2027, 2, 15), 1_400_000, "LS", 1, 0),
            ("Commissioning & Handover", "Not Started", d(2027, 2, 1), d(2027, 3, 31), 600_000, "LS", 1, 0),
        ]

        tasks = []
        for order, (name, status, ps, pf, budget, unit, tot, done) in enumerate(task_defs, start=1):
            t = Task(
                project_id=pid,
                activity_name=name,
                status=status,
                planned_start=ps,
                planned_finish=pf,
                budgeted_cost=float(budget),
                responsible_user_id=owner.user_id,
                expected_output=f"{name} — completed to specification and signed off.",
                depends_on=(order - 1) if order > 1 else None,
                sort_order=order,
                unit_of_measure=unit,
                total_quantity=float(tot),
                completed_quantity=float(done),
            )
            db.add(t)
            db.commit()
            db.refresh(t)
            tasks.append(t)

        # ---- Expenditures: ~ R 10.8M of the R 18M budget burned (~60%) ----
        exp = [
            (1, "Professional Fees", "Architect & engineering — design phase", 1_150_000, d(2025, 10, 15)),
            (2, "Equipment", "Site offices, hoarding, temporary power", 820_000, d(2025, 12, 5)),
            (3, "Plant Hire", "Excavators & haul trucks — bulk earthworks", 1_500_000, d(2026, 1, 20)),
            (3, "Materials", "Imported fill & compaction", 760_000, d(2026, 2, 10)),
            (4, "Subcontractor", "Piling subcontractor — progress claim 1", 1_800_000, d(2026, 3, 5)),
            (4, "Subcontractor", "Piling subcontractor — progress claim 2 (final)", 1_180_000, d(2026, 4, 12)),
            (5, "Materials", "Rebar & ready-mix concrete — L1-L2", 1_900_000, d(2026, 4, 28)),
            (5, "Labour", "Formwork & concrete crews — April", 920_000, d(2026, 4, 30)),
            (5, "Labour", "Formwork & concrete crews — May (partial)", 480_000, d(2026, 5, 12)),
            (6, "Materials", "Rebar delivery — L3-L4 (advance order)", 360_000, d(2026, 5, 8)),
        ]
        for task_idx, category, desc, amount, when in exp:
            db.add(
                Expenditure(
                    project_id=pid,
                    activity_id=tasks[task_idx - 1].activity_id,
                    category=category,
                    description=desc,
                    reference_id=f"INV-{when.strftime('%Y%m%d')}",
                    amount=float(amount),
                    spend_date=when,
                    recorded_by=owner.user_id,
                )
            )

        # ---- Daily progress on the two active tasks ----
        progress = [
            (5, 300, d(2026, 4, 6), "L1 columns poured, grid A-D."),
            (5, 350, d(2026, 4, 20), "L1 slab complete; L2 columns started."),
            (5, 250, d(2026, 5, 4), "L2 columns complete; slab formwork up."),
            (5, 200, d(2026, 5, 13), "L2 slab pour grid A-C."),
            (6, 140, d(2026, 5, 12), "L3 starter bars set; first columns formed."),
            (6, 100, d(2026, 5, 14), "L3 columns grid A-B poured."),
        ]
        for task_idx, qty, when, note in progress:
            db.add(
                DailyProgress(
                    activity_id=tasks[task_idx - 1].activity_id,
                    quantity=float(qty),
                    progress_date=when,
                    notes=note,
                    recorded_by=owner.user_id,
                )
            )

        # ---- Risks ----
        risks = [
            (
                5,
                "Concrete supply delays from primary batching plant could slow the frame.",
                "M",
                "Mitigated",
                "Second supplier onboarded as backup; weekly delivery schedule locked.",
                d(2026, 4, 9),
            ),
            (
                6,
                "Winter rainfall may disrupt L3-L4 pours from June onward.",
                "H",
                "Open",
                "Temporary weather covers procured; pour schedule front-loaded where possible.",
                d(2026, 5, 6),
            ),
            (
                7,
                "Long-lead MEP switchgear has a 14-week procurement window.",
                "H",
                "Open",
                "Purchase order to be placed by end of May to protect the program.",
                d(2026, 5, 10),
            ),
        ]
        for task_idx, desc, impact, status, mitigation, when in risks:
            db.add(
                Risk(
                    project_id=pid,
                    activity_id=tasks[task_idx - 1].activity_id,
                    description=desc,
                    impact=impact,
                    status=status,
                    mitigation_action=mitigation,
                    date_identified=when,
                    recorded_by=owner.user_id,
                )
            )

        db.commit()

        spent = sum(e[3] for e in exp)
        print("Demo project seeded successfully.")
        print(f"  Project   : {project.project_name} ({PROJECT_NUMBER})")
        print(f"  Budget    : R {project.total_budget:,.0f}")
        print(f"  Spent     : R {spent:,.0f}  (~{spent / project.total_budget * 100:.0f}% of budget)")
        print(f"  Tasks     : {len(tasks)}  (4 complete, 2 active, 4 not started)")
        print(f"  Risks     : {len(risks)}  |  Progress entries: {len(progress)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
