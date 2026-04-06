from uuid import UUID
from sqlmodel import Session, select
from app.digests.model import Digest


def get_user_digests(user_id: UUID, db: Session) -> list[Digest]:
    return db.exec(
        select(Digest)
        .where(Digest.user_id == user_id)
        .order_by(Digest.created_at.desc())
    ).all()


def get_digest(digest_id: UUID, user_id: UUID, db: Session) -> Digest:
    digest = db.get(Digest, digest_id)
    if not digest or digest.user_id != user_id:
        raise ValueError("Digest not found")
    return digest
