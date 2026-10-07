from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.skill import CandidateSkill, SkillEvidence
from app.engines.skill_taxonomy import normalize_skill


def record_skill_performance(
    db: Session,
    user_id: int,
    skill_name: str,
    performance_score: float,  # 0 to 100
    source_type: str,           # "resume", "dsa", "interview", "project"
    source_id: Optional[str] = None,
    evidence_weight: float = 0.3, # Bounded learning rate (0.1 - 0.4)
    notes: Optional[str] = None
) -> CandidateSkill:
    """
    Applies bounded evidence-based updates to a candidate skill.
    Prevents volatile score jumps while reflecting proven mastery.
    """
    canonical = normalize_skill(skill_name)
    now = datetime.now(timezone.utc)

    # Find or create candidate skill
    cand_skill = db.query(CandidateSkill).filter(
        CandidateSkill.user_id == user_id,
        CandidateSkill.canonical_name == canonical
    ).first()

    if not cand_skill:
        # Initial score starts gently weighted
        initial_score = performance_score
        confidence = "Low"
        cand_skill = CandidateSkill(
            user_id=user_id,
            canonical_name=canonical,
            score=round(initial_score, 1),
            confidence=confidence,
            target_score=75.0,
            trend="Stable",
            updated_at=now
        )
        db.add(cand_skill)
        db.flush()
    else:
        # Bounded exponential moving update: new_score = old * (1 - alpha) + observed * alpha
        old_score = cand_skill.score
        new_score = (old_score * (1.0 - evidence_weight)) + (performance_score * evidence_weight)
        cand_skill.score = round(new_score, 1)

        # Update trend
        if new_score > old_score + 2.0:
            cand_skill.trend = "Improving"
        elif new_score < old_score - 2.0:
            cand_skill.trend = "Regressing"
        else:
            cand_skill.trend = "Stable"

        cand_skill.updated_at = now

    # Record persistent evidence
    evidence = SkillEvidence(
        candidate_skill_id=cand_skill.id,
        source_type=source_type,
        source_id=source_id,
        score=performance_score,
        confidence=evidence_weight,
        notes=notes or f"Performance in {source_type} ({performance_score:.0f}/100)",
        created_at=now
    )
    db.add(evidence)
    db.flush()

    # Update confidence tier based on number of evidence items
    evidence_count = db.query(SkillEvidence).filter(SkillEvidence.candidate_skill_id == cand_skill.id).count()
    if evidence_count >= 3:
        cand_skill.confidence = "High"
    elif evidence_count >= 2:
        cand_skill.confidence = "Medium"
    else:
        cand_skill.confidence = "Low"

    db.commit()
    db.refresh(cand_skill)
    return cand_skill
