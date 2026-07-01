import uuid
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.backend.models.document import Document, DocumentFolder


def get_by_id(db: Session, document_id: uuid.UUID) -> Document | None:
    return db.query(Document).filter(
        Document.id == document_id,
        Document.is_active.is_(True),
    ).first()


def create_document(db: Session, data: dict[str, Any]) -> Document:
    doc = Document(**data)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def list_documents(
    db: Session,
    project_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    folder_id: uuid.UUID | None = None,
) -> tuple[list[Document], int, int, int]:
    query = db.query(Document).filter(
        Document.project_id == project_id,
        Document.is_active.is_(True),
    )
    if folder_id is not None:
        query = query.filter(Document.folder_id == folder_id)
    else:
        query = query.filter(Document.folder_id.is_(None))

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Document.created_at.desc()).offset(offset).limit(page_size).all()

    return items, total, page, page_size


def search_documents(
    db: Session,
    project_id: uuid.UUID,
    q: str | None = None,
    tags: str | None = None,
    folder_id: uuid.UUID | None = None,
) -> list[Document]:
    query = db.query(Document).filter(
        Document.project_id == project_id,
        Document.is_active.is_(True),
    )
    if q:
        search_term = f"%{q}%"
        query = query.filter(Document.name.ilike(search_term))
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            tag_filters = [Document.tags.ilike(f"%{tag}%") for tag in tag_list]
            query = query.filter(or_(*tag_filters))
    if folder_id is not None:
        query = query.filter(Document.folder_id == folder_id)

    return query.order_by(Document.created_at.desc()).all()


def update_document(db: Session, document_id: uuid.UUID, **kwargs: Any) -> Document | None:
    doc = get_by_id(db, document_id)
    if not doc:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(doc, key, value)
    db.commit()
    db.refresh(doc)
    return doc


def get_latest_version(db: Session, project_id: uuid.UUID, name: str) -> Document | None:
    return db.query(Document).filter(
        Document.project_id == project_id,
        Document.name == name,
        Document.is_active.is_(True),
    ).order_by(Document.version_number.desc()).first()


def count_versions(db: Session, project_id: uuid.UUID, name: str) -> int:
    return db.query(Document).filter(
        Document.project_id == project_id,
        Document.name == name,
        Document.is_active.is_(True),
    ).count()


def get_version_chain(db: Session, project_id: uuid.UUID, name: str) -> list[Document]:
    return db.query(Document).filter(
        Document.project_id == project_id,
        Document.name == name,
        Document.is_active.is_(True),
    ).order_by(Document.version_number.asc()).all()


def move_documents(db: Session, document_ids: list[uuid.UUID], target_folder_id: uuid.UUID | None) -> int:
    docs = db.query(Document).filter(
        Document.id.in_(document_ids),
        Document.is_active.is_(True),
    ).all()
    count = 0
    for doc in docs:
        doc.folder_id = target_folder_id
        count += 1
    db.commit()
    return count


def get_folder_by_id(db: Session, folder_id: uuid.UUID) -> DocumentFolder | None:
    return db.query(DocumentFolder).filter(DocumentFolder.id == folder_id).first()


def create_folder(db: Session, data: dict[str, Any]) -> DocumentFolder:
    folder = DocumentFolder(**data)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


def list_folders(db: Session, project_id: uuid.UUID, parent_id: uuid.UUID | None = None) -> list[DocumentFolder]:
    query = db.query(DocumentFolder).filter(DocumentFolder.project_id == project_id)
    if parent_id is not None:
        query = query.filter(DocumentFolder.parent_id == parent_id)
    else:
        query = query.filter(DocumentFolder.parent_id.is_(None))
    return query.order_by(DocumentFolder.name.asc()).all()


def delete_folder(db: Session, folder_id: uuid.UUID) -> bool:
    folder = get_folder_by_id(db, folder_id)
    if not folder:
        return False
    db.delete(folder)
    db.commit()
    return True


def rename_folder(db: Session, folder_id: uuid.UUID, new_name: str) -> DocumentFolder | None:
    folder = get_folder_by_id(db, folder_id)
    if not folder:
        return None
    folder.name = new_name
    db.commit()
    db.refresh(folder)
    return folder
