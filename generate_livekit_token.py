#!/usr/bin/env python3
"""
Generate a LiveKit access token for connecting to the spelling tutor agent.

Usage:
    python3 generate_livekit_token.py
    python3 generate_livekit_token.py --room my-room --identity emma
    python3 generate_livekit_token.py --room my-room --child-id 1 --word-list week2
"""
import argparse
import os
from datetime import datetime, timedelta
from livekit import api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_token(
    room_name: str,
    participant_identity: str,
    child_id: int = 1,
    word_list_name: str = "week1",
    ttl_hours: int = 24
) -> str:
    """
    Generate a LiveKit access token.

    Args:
        room_name: Name of the room to join
        participant_identity: Identity of the participant (e.g., "emma", "user123")
        child_id: Child profile ID (default: 1)
        word_list_name: Name of the word list to use (default: "week1")
        ttl_hours: Token validity in hours (default: 24)

    Returns:
        str: Access token
    """
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not api_key or not api_secret:
        raise ValueError(
            "LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env file"
        )

    # Create metadata with child_id and word_list_name
    metadata = f"child_id={child_id},word_list_name={word_list_name}"

    # Create token with VideoGrant
    token = api.AccessToken(api_key, api_secret)
    token.with_identity(participant_identity)
    token.with_name(participant_identity)
    token.with_metadata(metadata)
    token.with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        )
    )

    # Set expiration
    token.with_ttl(timedelta(hours=ttl_hours))

    return token.to_jwt()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate LiveKit access token for spelling tutor agent"
    )
    parser.add_argument(
        "--room",
        type=str,
        default=f"spelling-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        help="Room name (default: auto-generated)",
    )
    parser.add_argument(
        "--identity",
        type=str,
        default="student",
        help="Participant identity (default: 'student')",
    )
    parser.add_argument(
        "--child-id",
        type=int,
        default=1,
        help="Child profile ID (default: 1 for Emma)",
    )
    parser.add_argument(
        "--word-list",
        type=str,
        default="week1",
        help="Word list name (default: 'week1')",
    )
    parser.add_argument(
        "--ttl",
        type=int,
        default=24,
        help="Token validity in hours (default: 24)",
    )

    args = parser.parse_args()

    try:
        token = generate_token(
            room_name=args.room,
            participant_identity=args.identity,
            child_id=args.child_id,
            word_list_name=args.word_list,
            ttl_hours=args.ttl,
        )

        livekit_url = os.getenv("LIVEKIT_URL")

        print("=" * 70)
        print("LiveKit Access Token Generated Successfully!")
        print("=" * 70)
        print(f"\nRoom Name:      {args.room}")
        print(f"Identity:       {args.identity}")
        print(f"Child ID:       {args.child_id}")
        print(f"Word List:      {args.word_list}")
        print(f"Valid for:      {args.ttl} hours")
        print(f"\nLiveKit URL:    {livekit_url}")
        print(f"\nAccess Token:\n{token}")
        print("\n" + "=" * 70)
        print("\nTo use this token:")
        print("1. Copy the token above")
        print("2. Use it with your LiveKit client SDK")
        print("3. Connect to the room using the LiveKit URL and token")
        print("\nExample (JavaScript):")
        print(f'  const room = new Room();')
        print(f'  await room.connect("{livekit_url}", "{token[:20]}...");')
        print("=" * 70)

        # Also save to file for convenience
        with open("livekit_token.txt", "w") as f:
            f.write(f"Room: {args.room}\n")
            f.write(f"URL: {livekit_url}\n")
            f.write(f"Token: {token}\n")

        print("\n✅ Token also saved to: livekit_token.txt")

    except Exception as e:
        print(f"Error generating token: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
