"""Cross-project learning aggregation.

This module provides functionality to share learnings across all projects
by maintaining a global pattern database and syncing patterns bidirectionally.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime


logger = logging.getLogger(__name__)


class CrossProjectLearningStore:
    """Aggregate and share learnings across all projects."""

    def __init__(self, global_learning_dir: Path):
        """Initialize cross-project learning store.

        Args:
            global_learning_dir: Path to global learning directory
                                (e.g., ~/agentic-coding-library/.tac/learning/global/)
        """
        self.global_dir = global_learning_dir
        self.global_dir.mkdir(parents=True, exist_ok=True)

        self.global_patterns_file = self.global_dir / "global_pattern_database.json"
        self.global_weights_file = self.global_dir / "global_decision_weights.json"
        self.project_registry_file = self.global_dir / "project_registry.json"

    def aggregate_from_project(self, project_name: str, local_learning_dir: Path) -> None:
        """Aggregate learnings from a project into global store.

        Args:
            project_name: Name of the project (e.g., "my-web-app")
            local_learning_dir: Path to project's .tac/learning/ directory
        """
        # 1. Load global pattern database
        global_db = self._load_global_patterns()

        # 2. Load project's pattern database
        project_patterns_file = local_learning_dir / "pattern_database.json"
        if not project_patterns_file.exists():
            logger.debug(f"No pattern database found for project {project_name}")
            return

        with open(project_patterns_file) as f:
            project_db = json.load(f)

        # 3. Merge patterns
        patterns_added = 0
        patterns_updated = 0

        for pattern in project_db.get("patterns", []):
            pattern_id = pattern.get("pattern_name")
            if not pattern_id:
                continue

            # Add project source
            pattern["source_project"] = project_name
            pattern["last_updated"] = datetime.now().isoformat()

            # Find existing pattern
            existing = next(
                (p for p in global_db["patterns"] if p.get("pattern_name") == pattern_id),
                None
            )

            if existing:
                # Update existing pattern: average success rates, sum use counts
                old_success = existing.get("success_rate", 0.5)
                new_success = pattern.get("success_rate", 0.5)
                old_count = existing.get("use_count", 1)
                new_count = pattern.get("use_count", 1)

                # Weighted average based on use counts
                total_count = old_count + new_count
                weighted_success = (old_success * old_count + new_success * new_count) / total_count

                existing["success_rate"] = weighted_success
                existing["use_count"] = total_count
                existing["last_updated"] = datetime.now().isoformat()

                # Track contributing projects
                if "contributing_projects" not in existing:
                    existing["contributing_projects"] = []
                if project_name not in existing["contributing_projects"]:
                    existing["contributing_projects"].append(project_name)

                patterns_updated += 1
            else:
                # Add new pattern
                pattern["contributing_projects"] = [project_name]
                global_db["patterns"].append(pattern)
                patterns_added += 1

        # 4. Save global database
        self._save_global_patterns(global_db)

        # 5. Update project registry
        self._register_project(project_name, local_learning_dir)

        logger.info(
            f"Aggregated patterns from {project_name}: "
            f"{patterns_added} added, {patterns_updated} updated"
        )

    def sync_to_project(self, local_learning_dir: Path) -> None:
        """Sync global learnings back to a project.

        Only syncs patterns with higher success rates than local versions.

        Args:
            local_learning_dir: Path to project's .tac/learning/ directory
        """
        # Load global patterns
        global_db = self._load_global_patterns()

        # Load project patterns
        project_patterns_file = local_learning_dir / "pattern_database.json"
        if project_patterns_file.exists():
            with open(project_patterns_file) as f:
                project_db = json.load(f)
        else:
            project_db = {"patterns": [], "total_patterns": 0}

        # Merge global patterns into project (only higher success rates)
        patterns_synced = 0

        for global_pattern in global_db["patterns"]:
            pattern_id = global_pattern.get("pattern_name")
            if not pattern_id:
                continue

            existing = next(
                (p for p in project_db["patterns"] if p.get("pattern_name") == pattern_id),
                None
            )

            # Replace with better global pattern
            if not existing or global_pattern.get("success_rate", 0) > existing.get("success_rate", 0):
                if existing:
                    project_db["patterns"].remove(existing)
                    logger.debug(f"Replaced pattern {pattern_id} with global version")
                else:
                    logger.debug(f"Added new pattern {pattern_id} from global")

                project_db["patterns"].append(global_pattern.copy())
                patterns_synced += 1

        project_db["total_patterns"] = len(project_db["patterns"])
        project_db["last_global_sync"] = datetime.now().isoformat()

        # Save updated project database
        local_learning_dir.mkdir(parents=True, exist_ok=True)
        with open(project_patterns_file, 'w') as f:
            json.dump(project_db, f, indent=2)

        logger.info(f"Synced {patterns_synced} patterns from global to project")

    def get_global_insights(self) -> Dict[str, Any]:
        """Get aggregated insights across all projects.

        Returns:
            Dict with global statistics and insights
        """
        global_db = self._load_global_patterns()

        # Calculate statistics
        total_patterns = len(global_db["patterns"])

        if total_patterns == 0:
            return {
                "total_patterns": 0,
                "average_success_rate": 0.0,
                "top_patterns": [],
                "patterns_by_project": {},
                "total_projects": 0,
            }

        avg_success_rate = sum(
            p.get("success_rate", 0) for p in global_db["patterns"]
        ) / total_patterns

        # Top performing patterns
        top_patterns = sorted(
            global_db["patterns"],
            key=lambda p: p.get("success_rate", 0),
            reverse=True
        )[:10]

        # Patterns by project
        by_project = defaultdict(int)
        for pattern in global_db["patterns"]:
            source = pattern.get("source_project", "unknown")
            by_project[source] += 1

        # Load project registry
        registry = self._load_project_registry()
        total_projects = len(registry.get("projects", []))

        return {
            "total_patterns": total_patterns,
            "average_success_rate": avg_success_rate,
            "top_patterns": [
                {
                    "name": p.get("pattern_name"),
                    "success_rate": p.get("success_rate", 0),
                    "use_count": p.get("use_count", 0)
                }
                for p in top_patterns
            ],
            "patterns_by_project": dict(by_project),
            "total_projects": total_projects,
        }

    def _load_global_patterns(self) -> Dict[str, Any]:
        """Load global pattern database.

        Returns:
            Dict with patterns array and metadata
        """
        if self.global_patterns_file.exists():
            with open(self.global_patterns_file) as f:
                return json.load(f)

        return {
            "patterns": [],
            "total_patterns": 0,
            "last_updated": datetime.now().isoformat(),
        }

    def _save_global_patterns(self, db: Dict[str, Any]) -> None:
        """Save global pattern database.

        Args:
            db: Pattern database dict
        """
        db["total_patterns"] = len(db["patterns"])
        db["last_updated"] = datetime.now().isoformat()

        with open(self.global_patterns_file, 'w') as f:
            json.dump(db, f, indent=2)

        logger.debug(f"Saved global pattern database with {db['total_patterns']} patterns")

    def _load_project_registry(self) -> Dict[str, Any]:
        """Load project registry.

        Returns:
            Dict with registered projects
        """
        if self.project_registry_file.exists():
            with open(self.project_registry_file) as f:
                return json.load(f)

        return {"projects": []}

    def _register_project(self, project_name: str, local_dir: Path) -> None:
        """Register project in global registry.

        Args:
            project_name: Name of the project
            local_dir: Path to project's learning directory
        """
        registry = self._load_project_registry()

        # Add or update project
        existing = next(
            (p for p in registry["projects"] if p["name"] == project_name),
            None
        )

        if not existing:
            registry["projects"].append({
                "name": project_name,
                "learning_dir": str(local_dir),
                "registered_at": datetime.now().isoformat(),
                "last_sync": datetime.now().isoformat(),
            })
            logger.info(f"Registered new project: {project_name}")
        else:
            existing["last_sync"] = datetime.now().isoformat()
            logger.debug(f"Updated project registry: {project_name}")

        with open(self.project_registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
