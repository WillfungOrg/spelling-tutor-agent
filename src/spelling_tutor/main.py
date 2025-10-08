import asyncio
import sys
from datetime import datetime
from typing import Optional

import click

# Local imports
from .config import load_config, get_db_path
from .database import (
    init_database, create_child_profile, get_child_profile,
    list_word_lists, get_word_list, get_child_sessions,
    create_session, record_word_attempt, complete_session
)
from .word_manager import upload_word_list


@click.group()
def cli():
    """
    Spelling Tutor Voice Agent CLI.

    A command-line interface for managing the AI-powered spelling tutor
    with voice interaction capabilities using LiveKit.
    """
    pass


@cli.command()
@click.option('--name', required=True, help='Name of the child')
@click.option('--age', required=True, type=int, help='Age of the child')
def setup(name: str, age: int):
    """
    Set up a new child profile for spelling practice.

    Creates a new child profile in the database and initializes
    the database if it doesn't exist.

    Examples:
        python -m spelling_tutor.main setup --name "Alice" --age 8
        python -m spelling_tutor.main setup --name "Bob" --age 10
    """
    try:
        # Initialize database
        db_path = get_db_path()
        init_database(db_path)
        click.echo(f"Database initialized at: {db_path}")

        # Create child profile
        child = create_child_profile(name, age)

        click.echo(f"✅ Successfully created child profile!")
        click.echo(f"   Child ID: {child.id}")
        click.echo(f"   Name: {child.name}")
        click.echo(f"   Age: {child.age}")
        click.echo(f"   Created: {child.created_at}")

    except Exception as e:
        click.echo(f"❌ Error creating child profile: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--name', required=True, help='Name for the word list')
@click.option('--file', 'file_path', required=True, type=click.Path(exists=True),
              help='Path to text file containing words (one per line)')
def upload(name: str, file_path: str):
    """
    Upload a word list from a text file.

    Reads words from a text file (one word per line) and creates
    a new word list in the database with automatic difficulty detection.

    Examples:
        python -m spelling_tutor.main upload --name "Grade 1 Words" --file words.txt
        python -m spelling_tutor.main upload --name "Sight Words" --file data/word_lists/sight_words.txt
    """
    try:
        # Upload word list
        word_list = upload_word_list(name, file_path)

        # Get word count
        _, words = get_word_list(word_list.id)
        word_count = len(words)

        click.echo(f"✅ Successfully uploaded word list!")
        click.echo(f"   Word List ID: {word_list.id}")
        click.echo(f"   Name: {word_list.name}")
        click.echo(f"   Word Count: {word_count}")
        click.echo(f"   Created: {word_list.created_at}")

    except Exception as e:
        click.echo(f"❌ Error uploading word list: {e}", err=True)
        sys.exit(1)


@cli.command('list-words')
def list_words():
    """
    List all available word lists.

    Displays a table of all word lists in the database with their
    IDs, names, and creation dates.

    Examples:
        python -m spelling_tutor.main list-words
    """
    try:
        word_lists = list_word_lists()

        if not word_lists:
            click.echo("No word lists found. Use 'upload' command to add word lists.")
            return

        # Print table header
        click.echo("\n📚 Available Word Lists:")
        click.echo("=" * 70)
        click.echo(f"{'ID':<5} {'Name':<30} {'Created':<20}")
        click.echo("-" * 70)

        # Print word list data
        for word_list in word_lists:
            # Format date for display
            try:
                created_date = datetime.fromisoformat(word_list.created_at).strftime('%Y-%m-%d %H:%M')
            except:
                created_date = word_list.created_at[:16]  # Fallback formatting

            click.echo(f"{word_list.id:<5} {word_list.name[:29]:<30} {created_date:<20}")

        click.echo("=" * 70)
        click.echo(f"Total: {len(word_lists)} word lists")

    except Exception as e:
        click.echo(f"❌ Error listing word lists: {e}", err=True)
        sys.exit(1)


# Note: To start the voice agent, run:
#   python -m spelling_tutor.agent_worker


@cli.command('show-progress')
@click.option('--child-id', required=True, type=int, help='ID of the child')
def show_progress(child_id: int):
    """
    Show progress and session history for a child.

    Displays all spelling practice sessions for the specified child,
    including dates, word lists used, and completion status.

    Examples:
        python -m spelling_tutor.main show-progress --child-id 1
        python -m spelling_tutor.main show-progress --child-id 2
    """
    try:
        # Validate child exists
        child = get_child_profile(child_id)
        if not child:
            click.echo(f"❌ Child with ID {child_id} not found", err=True)
            sys.exit(1)

        # Get sessions
        sessions = get_child_sessions(child_id)

        if not sessions:
            click.echo(f"📊 No practice sessions found for {child.name}")
            click.echo("Use 'start' command to begin a spelling practice session.")
            return

        # Display child info
        click.echo(f"\n📊 Progress for {child.name} (age {child.age})")
        click.echo("=" * 80)

        # Display sessions table
        click.echo(f"{'Session':<10} {'Date':<16} {'Word List':<25} {'Status':<15}")
        click.echo("-" * 80)

        for session in sessions:
            # Format start date
            try:
                start_date = datetime.fromisoformat(session.started_at).strftime('%Y-%m-%d %H:%M')
            except:
                start_date = session.started_at[:16]

            # Get word list name
            try:
                word_list, _ = get_word_list(session.word_list_id)
                word_list_name = word_list.name[:24]
            except:
                word_list_name = f"Word List {session.word_list_id}"

            # Determine status
            status = "✅ Completed" if session.completed_at else "🔄 In Progress"

            click.echo(f"{session.id:<10} {start_date:<16} {word_list_name:<25} {status:<15}")

        click.echo("=" * 80)
        completed_count = sum(1 for s in sessions if s.completed_at)
        click.echo(f"Total Sessions: {len(sessions)} | Completed: {completed_count} | In Progress: {len(sessions) - completed_count}")

    except Exception as e:
        click.echo(f"❌ Error showing progress: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()