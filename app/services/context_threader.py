"""
Context Threader (CT) - Thread State Management & Persistence.

Manages attack thread state across stages:
- Aggregates evidence and context for each stage
- Persists thread state with versioning
- Reconciles new stage results with existing thread
- Provides continuity validation across stages
"""

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ThreadState:
    """Represents the complete state of an attack thread."""
    
    thread_id: str
    asset_id: str
    current_stage: int
    status: str  # "in_progress", "completed", "failed", "awaiting_review"
    
    # Context accumulation
    reconnaissance: str
    previous_techniques: List[Dict[str, Any]]  # List of executed techniques
    evidence: List[str]  # Accumulated evidence/observations
    assumptions: List[str]  # Working assumptions
    
    # Confidence tracking
    confidence_scores: Dict[str, float]  # Per-stage confidence
    overall_confidence: float
    
    # Metadata
    created_at: str
    updated_at: str
    version: int
    
    # Constraints
    constraints: Dict[str, Any]  # OS compatibility, tool restrictions, etc.
    objective_reached: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class ContextThreader:
    """
    Context Threader (CT) - Thread State Manager.
    
    Responsibilities:
    1. Initialize new attack threads
    2. Aggregate context for next stage (NextStageContext)
    3. Reconcile and persist stage results
    4. Validate continuity across stages
    5. Provide thread snapshots
    """
    
    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize Context Threader.
        
        Args:
            storage_backend: Database/storage backend for persistence
                           (defaults to in-memory for now)
        """
        self.storage = storage_backend or InMemoryStorage()
    
    def initialize_thread(
        self, 
        asset_id: str,
        reconnaissance: str,
        constraints: Dict[str, Any]
    ) -> ThreadState:
        """
        Initialize a new attack thread.
        
        Args:
            asset_id: Unique asset identifier
            reconnaissance: Initial recon summary
            constraints: OS compatibility, tool restrictions, etc.
            
        Returns:
            New ThreadState object
        """
        thread_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        thread_state = ThreadState(
            thread_id=thread_id,
            asset_id=asset_id,
            current_stage=0,
            status="in_progress",
            reconnaissance=reconnaissance,
            previous_techniques=[],
            evidence=[],
            assumptions=[],
            confidence_scores={},
            overall_confidence=0.0,
            created_at=now,
            updated_at=now,
            version=1,
            constraints=constraints,
            objective_reached=False
        )
        
        self.storage.save(thread_id, thread_state)
        return thread_state
    
    def get_next_stage_context(
        self,
        thread_id: str,
        stage_index: int
    ) -> Dict[str, Any]:
        """
        Build context payload for next stage (NextStageContext(N)).
        
        This is called by orchestrator before prompting LLM.
        
        Args:
            thread_id: Attack thread identifier
            stage_index: Next stage number to generate
            
        Returns:
            Context dictionary with:
            - thread_state: Current thread snapshot
            - evidence: Accumulated observations
            - previous_techniques: Executed techniques
            - constraints: OS/tool compatibility rules
            - confidence_scores: Per-stage confidence
        """
        thread_state = self.storage.load(thread_id)
        
        if thread_state is None:
            raise ValueError(f"Thread {thread_id} not found")
        
        if thread_state.objective_reached:
            raise ValueError(f"Thread {thread_id} objective already reached")
        
        # Build aggregated context
        context = {
            "thread_id": thread_id,
            "stage_index": stage_index,
            "reconnaissance": thread_state.reconnaissance,
            "previous_techniques": thread_state.previous_techniques,
            "evidence": thread_state.evidence,
            "assumptions": thread_state.assumptions,
            "constraints": thread_state.constraints,
            "confidence_scores": thread_state.confidence_scores,
            "overall_confidence": thread_state.overall_confidence,
            "current_stage": thread_state.current_stage,
            "version": thread_state.version
        }
        
        return context
    
    def reconcile_and_persist(
        self,
        thread_id: str,
        stage_index: int,
        stage_result: Dict[str, Any],
        merge_strategy: str = "append"
    ) -> Dict[str, Any]:
        """
        Reconcile new stage result with existing thread and persist.
        
        Args:
            thread_id: Attack thread identifier
            stage_index: Stage number that was executed
            stage_result: Validated output from LLM (parsed and validated)
            merge_strategy: How to merge ("append", "overwrite", "merge")
            
        Returns:
            Updated thread state snapshot with version and confidence
        """
        thread_state = self.storage.load(thread_id)
        
        if thread_state is None:
            raise ValueError(f"Thread {thread_id} not found")
        
        # Update stage
        thread_state.current_stage = stage_index
        thread_state.updated_at = datetime.utcnow().isoformat()
        thread_state.version += 1
        
        # Reconcile based on merge strategy
        if merge_strategy == "append":
            # Append new technique
            thread_state.previous_techniques.append({
                "stage": stage_index,
                "technique": stage_result.get("technique"),
                "action": stage_result.get("action"),
                "expected_outcome": stage_result.get("expected_outcome"),
                "probability": stage_result.get("probability"),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Append evidence
            if "evidence" in stage_result:
                thread_state.evidence.extend(stage_result["evidence"])
            
            # Update confidence
            if "confidence" in stage_result:
                thread_state.confidence_scores[f"stage_{stage_index}"] = stage_result["confidence"]
                thread_state.overall_confidence = sum(thread_state.confidence_scores.values()) / len(thread_state.confidence_scores)
        
        # Check if objective reached
        if stage_result.get("objective_status") == "achieved":
            thread_state.objective_reached = True
            thread_state.status = "completed"
        
        # Persist updated state
        self.storage.save(thread_id, thread_state)
        
        return {
            "thread_state_snapshot": thread_state.to_dict(),
            "version": thread_state.version,
            "confidence": thread_state.overall_confidence,
            "objective_reached": thread_state.objective_reached
        }
    
    def get_thread_snapshot(self, thread_id: str) -> Optional[Dict]:
        """Get current thread state snapshot."""
        thread_state = self.storage.load(thread_id)
        return thread_state.to_dict() if thread_state else None


class InMemoryStorage:
    """In-memory storage backend (for development/testing)."""
    
    def __init__(self):
        self._store: Dict[str, ThreadState] = {}
    
    def save(self, thread_id: str, thread_state: ThreadState):
        """Save thread state."""
        self._store[thread_id] = thread_state
    
    def load(self, thread_id: str) -> Optional[ThreadState]:
        """Load thread state."""
        return self._store.get(thread_id)
    
    def delete(self, thread_id: str):
        """Delete thread state."""
        if thread_id in self._store:
            del self._store[thread_id]
