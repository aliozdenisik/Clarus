#!/usr/bin/env python3
"""
Migrate users from legacy auth (users_legacy) to Better Auth tables.

Features:
- Dry-run by default (--execute flag to actually migrate)
- --rollback flag to reverse migration
- Batch processing with configurable batch size
- Rich console output with progress tracking
- Error handling: skip failed users, continue processing
- Summary report: migrated/failed/skipped counts

Usage:
    python migrate_users_to_better_auth.py                # Dry-run (shows what would happen)
    python migrate_users_to_better_auth.py --execute      # Execute migration
    python migrate_users_to_better_auth.py --rollback     # Rollback migration
    python migrate_users_to_better_auth.py --batch-size 50  # Custom batch size
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Ensure backend/ is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
)
from rich.table import Table

console = Console()

# Database connection string
DATABASE_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

# Tracking migrated user IDs for rollback
MIGRATED_USER_IDS = []


def get_connection():
    """Create and return database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        console.print(f"[red]❌ Failed to connect to database:[/red] {e}")
        sys.exit(1)


def fetch_legacy_users(conn):
    """Fetch all users from users_legacy table."""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT
                id,
                email,
                name,
                hashed_password,
                google_id,
                created_at,
                query_count_today,
                last_query_date,
                refresh_token
            FROM users_legacy
            ORDER BY id
        """)
        return cursor.fetchall()


def migrate_user(
    conn, user: dict, dry_run: bool = True
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Migrate a single user to Better Auth tables.

    Returns:
        (success: bool, new_user_id: Optional[str], error_msg: Optional[str])
    """
    try:
        with conn.cursor() as cursor:
            # Generate new UUID for Better Auth user
            cursor.execute("SELECT gen_random_uuid()::text AS new_id")
            new_user_id = cursor.fetchone()[0]

            # Prepare timestamp values
            created_at = user["created_at"] or datetime.now(timezone.utc)
            updated_at = datetime.now(timezone.utc)

            # 1. INSERT into user table
            user_sql = """
                INSERT INTO "user" (
                    id, name, email, "emailVerified", image, "createdAt", "updatedAt"
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            user_values = (
                new_user_id,
                user["name"],
                user["email"],
                False,  # emailVerified - default to False for migrated users
                None,  # image - no image in legacy
                created_at,
                updated_at,
            )

            if not dry_run:
                cursor.execute(user_sql, user_values)

            # 2. INSERT into account table (for password or Google OAuth)
            account_id_suffix = 0

            # Password account (credential provider)
            if user.get("hashed_password"):
                cursor.execute("SELECT gen_random_uuid()::text AS account_id")
                account_id = cursor.fetchone()[0]

                account_sql = """
                    INSERT INTO account (
                        id, "userId", "accountId", "providerId", password,
                        "createdAt", "updatedAt"
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                account_values = (
                    account_id,
                    new_user_id,
                    user["email"],  # accountId = email for credential provider
                    "credential",
                    user["hashed_password"],  # bcrypt hash (cost=12)
                    created_at,
                    updated_at,
                )

                if not dry_run:
                    cursor.execute(account_sql, account_values)
                account_id_suffix += 1

            # Google OAuth account
            if user.get("google_id"):
                cursor.execute("SELECT gen_random_uuid()::text AS account_id")
                account_id = cursor.fetchone()[0]

                account_sql = """
                    INSERT INTO account (
                        id, "userId", "accountId", "providerId",
                        "refreshToken", "createdAt", "updatedAt"
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                account_values = (
                    account_id,
                    new_user_id,
                    user["google_id"],  # accountId = google_id for OAuth
                    "google",
                    user.get("refresh_token"),  # preserve refresh token if exists
                    created_at,
                    updated_at,
                )

                if not dry_run:
                    cursor.execute(account_sql, account_values)
                account_id_suffix += 1

            # 3. INSERT into user_stats table
            cursor.execute("SELECT gen_random_uuid()::text AS stats_id")
            stats_id = cursor.fetchone()[0]

            # Convert datetime to date if needed
            last_query_date = None
            if user.get("last_query_date"):
                if isinstance(user["last_query_date"], datetime):
                    last_query_date = user["last_query_date"].date()
                else:
                    last_query_date = user["last_query_date"]

            stats_sql = """
                INSERT INTO user_stats (
                    id, user_id, query_count_today, last_query_date,
                    created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            stats_values = (
                stats_id,
                new_user_id,
                user.get("query_count_today", 0),
                last_query_date,
                created_at,
                updated_at,
            )

            if not dry_run:
                cursor.execute(stats_sql, stats_values)
                conn.commit()
                MIGRATED_USER_IDS.append(new_user_id)

            return (True, new_user_id, None)

    except Exception as e:
        if not dry_run:
            conn.rollback()
        return (False, None, str(e))


def migrate_all_users(dry_run: bool = True, batch_size: int = 100):
    """
    Migrate all users from users_legacy to Better Auth tables.

    Args:
        dry_run: If True, only shows what would happen without making changes
        batch_size: Number of users to process in each batch (for progress display)
    """
    conn = get_connection()

    try:
        # Fetch all legacy users
        console.print("\n[yellow]📊 Fetching users from users_legacy...[/yellow]")
        users = fetch_legacy_users(conn)
        total_users = len(users)

        if total_users == 0:
            console.print("[yellow]⚠️  No users found in users_legacy table[/yellow]")
            return

        console.print(f"[green]✅ Found {total_users} users to migrate[/green]\n")

        # Show mode
        mode = (
            "[bold red]DRY-RUN MODE[/bold red]"
            if dry_run
            else "[bold green]EXECUTION MODE[/bold green]"
        )
        console.print(
            Panel(
                f"{mode}\n\n"
                + (
                    "No changes will be made to the database"
                    if dry_run
                    else "Changes WILL be made to the database"
                ),
                title="Migration Mode",
                border_style="yellow" if dry_run else "green",
            )
        )

        # Migration tracking
        migrated_count = 0
        failed_count = 0
        failed_users = []

        # Progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"[cyan]{'Simulating' if dry_run else 'Migrating'} users...",
                total=total_users,
            )

            for user in users:
                success, new_user_id, error_msg = migrate_user(conn, user, dry_run)

                if success:
                    migrated_count += 1
                else:
                    failed_count += 1
                    failed_users.append(
                        {"id": user["id"], "email": user["email"], "error": error_msg}
                    )

                progress.update(task, advance=1)

        # Summary report
        console.print("\n" + "=" * 70)
        console.print(
            Panel(
                f"[bold]Migration {'Simulation' if dry_run else 'Execution'} Complete[/bold]\n\n"
                + (
                    f"[green]✅ Successfully {'simulated' if dry_run else 'migrated'}: "
                    f"{migrated_count}[/green]\n"
                )
                + f"[red]❌ Failed: {failed_count}[/red]\n"
                f"[yellow]📊 Total processed: {total_users}[/yellow]",
                title="Summary",
                border_style="green" if failed_count == 0 else "yellow",
            )
        )

        # Show failed users if any
        if failed_users:
            console.print("\n[red]Failed Users:[/red]")
            table = Table(show_header=True, header_style="bold red")
            table.add_column("ID", style="dim")
            table.add_column("Email")
            table.add_column("Error", style="red")

            for failed in failed_users:
                table.add_row(
                    str(failed["id"]),
                    failed["email"],
                    failed["error"][:80] + "..." if len(failed["error"]) > 80 else failed["error"],
                )

            console.print(table)

        # Next steps
        if dry_run and failed_count == 0:
            console.print("\n[bold green]✨ Dry-run successful! No errors detected.[/bold green]")
            console.print("[yellow]To execute the migration, run:[/yellow]")
            console.print("    [cyan]python migrate_users_to_better_auth.py --execute[/cyan]")
        elif not dry_run and failed_count == 0:
            console.print(
                "\n[bold green]✨ Migration complete! All users migrated successfully.[/bold green]"
            )
            console.print(f"[dim]Migrated user IDs tracked: {len(MIGRATED_USER_IDS)}[/dim]")
        elif not dry_run:
            console.print(
                "\n[yellow]⚠️  Migration completed with errors. Review failed users above.[/yellow]"
            )

    except Exception as e:
        console.print(f"\n[red]❌ Fatal error during migration:[/red] {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


def rollback_migration():
    """
    Rollback migration by deleting all records from Better Auth tables.

    WARNING: This deletes ALL users in Better Auth tables, not just migrated ones.
    Use with caution.
    """
    console.print(
        Panel(
            "[bold red]⚠️  ROLLBACK MODE[/bold red]\n\n"
            "This will DELETE all users from Better Auth tables:\n"
            "  • user_stats\n"
            "  • account\n"
            "  • user\n\n"
            "[yellow]This action cannot be undone![/yellow]",
            title="Rollback Warning",
            border_style="red",
        )
    )

    response = console.input("\n[bold]Type 'YES' to confirm rollback: [/bold]")

    if response != "YES":
        console.print("[yellow]Rollback cancelled.[/yellow]")
        return

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            # Count records before deletion
            cursor.execute("SELECT COUNT(*) FROM user_stats")
            stats_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM account")
            account_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM "user"')
            user_count = cursor.fetchone()[0]

            console.print("\n[yellow]Records to delete:[/yellow]")
            console.print(f"  user_stats: {stats_count}")
            console.print(f"  account: {account_count}")
            console.print(f"  user: {user_count}")

            # Delete in correct order (children first due to FK constraints)
            console.print("\n[red]Deleting records...[/red]")

            cursor.execute("DELETE FROM user_stats")
            console.print(f"  ✓ Deleted {cursor.rowcount} records from user_stats")

            cursor.execute("DELETE FROM account")
            console.print(f"  ✓ Deleted {cursor.rowcount} records from account")

            cursor.execute('DELETE FROM "user"')
            console.print(f"  ✓ Deleted {cursor.rowcount} records from user")

            conn.commit()

            console.print(
                "\n[bold green]✅ Rollback complete. All Better Auth records deleted.[/bold green]"
            )

    except Exception as e:
        conn.rollback()
        console.print(f"\n[red]❌ Rollback failed:[/red] {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


def show_status():
    """Show current status of both legacy and Better Auth tables."""
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            # Legacy users count
            cursor.execute("SELECT COUNT(*) FROM users_legacy")
            legacy_count = cursor.fetchone()[0]

            # Better Auth users count
            cursor.execute('SELECT COUNT(*) FROM "user"')
            user_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM account")
            account_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM user_stats")
            stats_count = cursor.fetchone()[0]

            # Create status table
            table = Table(title="Migration Status", show_header=True, header_style="bold cyan")
            table.add_column("Table", style="dim")
            table.add_column("Count", justify="right")

            table.add_row("[yellow]users_legacy[/yellow]", f"[yellow]{legacy_count}[/yellow]")
            table.add_row("user (Better Auth)", str(user_count))
            table.add_row("account (Better Auth)", str(account_count))
            table.add_row("user_stats (Better Auth)", str(stats_count))

            console.print()
            console.print(table)
            console.print()

            if user_count > 0:
                console.print("[green]✅ Better Auth tables contain data[/green]")
                console.print(
                    f"[dim]Looks like migration has been run ({user_count} users migrated)[/dim]"
                )
            else:
                console.print("[yellow]⚠️  Better Auth tables are empty[/yellow]")
                console.print("[dim]Migration has not been run yet[/dim]")

    except Exception as e:
        console.print(f"[red]❌ Failed to fetch status:[/red] {e}")
        sys.exit(1)
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate users from legacy auth to Better Auth tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (default - shows what would happen)
  python migrate_users_to_better_auth.py

  # Execute migration
  python migrate_users_to_better_auth.py --execute

  # Rollback migration (deletes all Better Auth users)
  python migrate_users_to_better_auth.py --rollback

  # Show current status
  python migrate_users_to_better_auth.py --status

  # Custom batch size
  python migrate_users_to_better_auth.py --execute --batch-size 50
        """,
    )

    parser.add_argument(
        "--execute", action="store_true", help="Execute migration (default is dry-run)"
    )

    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback migration (delete all Better Auth users)",
    )

    parser.add_argument("--status", action="store_true", help="Show current migration status")

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for processing (default: 100)",
    )

    args = parser.parse_args()

    # Show header
    console.print(
        Panel(
            "[bold cyan]User Migration Tool[/bold cyan]\nLegacy Auth → Better Auth",
            border_style="cyan",
        )
    )

    # Handle different modes
    if args.status:
        show_status()
    elif args.rollback:
        rollback_migration()
    else:
        # Migration mode (dry-run or execute)
        dry_run = not args.execute
        migrate_all_users(dry_run=dry_run, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
