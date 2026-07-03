import uuid
from datetime import UTC

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.backend.models.compliance import (
    ComplianceChecklistItem,
    ComplianceStandard,
    ProjectComplianceItem,
)

SEED_STANDARDS = [
    {"name": "NBC", "version": "2016", "description": "National Building Code of India"},
    {"name": "ECBC", "version": "2017", "description": "Energy Conservation Building Code"},
    {"name": "IGBC", "version": "2011", "description": "Indian Green Building Council"},
    {"name": "IS", "version": "2021", "description": "Indian Standards — Fire Codes"},
]

CHECKLIST_SEEDS = {
    "NBC": [
        {"category": "Structural", "requirement": "Structural safety as per NBC Part 6", "is_mandatory": True},
        {"category": "Fire Safety", "requirement": "Fire safety provisions as per NBC Part 4", "is_mandatory": True},
        {"category": "Accessibility", "requirement": "Accessibility for differently-abled as per NBC Part 3", "is_mandatory": True},
        {"category": "Ventilation", "requirement": "Natural/mechanical ventilation as per NBC Part 10", "is_mandatory": True},
        {"category": "Sanitation", "requirement": "Sanitary and plumbing provisions as per NBC Part 10", "is_mandatory": True},
        {"category": "Lighting", "requirement": "Natural and artificial lighting as per NBC Part 8", "is_mandatory": True},
        {"category": "Water Supply", "requirement": "Rainwater harvesting provisions as per NBC Part 11", "is_mandatory": True},
        {"category": "Circulation", "requirement": "Staircase width and handrail compliance as per NBC Part 2", "is_mandatory": True},
    ],
    "ECBC": [
        {"category": "Envelope", "requirement": "Building envelope performance (U-value, SHGC)", "is_mandatory": True},
        {"category": "HVAC", "requirement": "HVAC system efficiency (EER, COP)", "is_mandatory": True},
        {"category": "Lighting", "requirement": "Lighting power density (LPD) limits", "is_mandatory": True},
        {"category": "Water Heating", "requirement": "Water heating system efficiency", "is_mandatory": False},
        {"category": "Rating", "requirement": "Building energy rating compliance", "is_mandatory": False},
    ],
    "IGBC": [
        {"category": "Energy", "requirement": "Energy efficiency measures", "is_mandatory": True},
        {"category": "Water", "requirement": "Water conservation and recycling", "is_mandatory": True},
        {"category": "Materials", "requirement": "Sustainable material sourcing", "is_mandatory": False},
        {"category": "Indoor Environment", "requirement": "Indoor environmental quality (IEQ)", "is_mandatory": True},
        {"category": "Site Planning", "requirement": "Site planning and landscape requirements", "is_mandatory": False},
    ],
    "IS": [
        {"category": "Fire Resistance", "requirement": "Fire resistance of structural elements", "is_mandatory": True},
        {"category": "Exits", "requirement": "Exit provisions and width requirements", "is_mandatory": True},
        {"category": "Smoke Control", "requirement": "Smoke control and ventilation systems", "is_mandatory": True},
        {"category": "Fire Equipment", "requirement": "Fire extinguisher placement and type", "is_mandatory": True},
        {"category": "Emergency Lighting", "requirement": "Emergency lighting and signage", "is_mandatory": True},
    ],
}


def seed_standards(db: Session) -> list[ComplianceStandard]:
    existing = db.query(ComplianceStandard).count()
    if existing > 0:
        return db.query(ComplianceStandard).all()
    standards = []
    for data in SEED_STANDARDS:
        std = ComplianceStandard(**data)
        db.add(std)
        standards.append(std)
    db.commit()
    for std in standards:
        db.refresh(std)
    return standards


def seed_checklist_items(db: Session, standard_id: uuid.UUID, items: list[dict]) -> list[ComplianceChecklistItem]:
    existing = db.query(ComplianceChecklistItem).filter(
        ComplianceChecklistItem.standard_id == standard_id
    ).count()
    if existing > 0:
        return db.query(ComplianceChecklistItem).filter(
            ComplianceChecklistItem.standard_id == standard_id
        ).all()
    created = []
    for item in items:
        obj = ComplianceChecklistItem(standard_id=standard_id, **item)
        db.add(obj)
        created.append(obj)
    db.commit()
    for obj in created:
        db.refresh(obj)
    return created


def get_standards(db: Session) -> list[ComplianceStandard]:
    return db.query(ComplianceStandard).order_by(ComplianceStandard.name).all()


def get_checklist_items_by_standard(db: Session, standard_id: uuid.UUID) -> list[ComplianceChecklistItem]:
    return db.query(ComplianceChecklistItem).filter(
        ComplianceChecklistItem.standard_id == standard_id
    ).order_by(ComplianceChecklistItem.category).all()


def get_checklist_item_by_id(db: Session, checklist_item_id: uuid.UUID) -> ComplianceChecklistItem | None:
    return db.query(ComplianceChecklistItem).filter(
        ComplianceChecklistItem.id == checklist_item_id
    ).first()


def get_standard_by_id(db: Session, standard_id: uuid.UUID) -> ComplianceStandard | None:
    return db.query(ComplianceStandard).filter(ComplianceStandard.id == standard_id).first()


def get_standard_by_name(db: Session, name: str) -> ComplianceStandard | None:
    return db.query(ComplianceStandard).filter(ComplianceStandard.name == name).first()


def check_duplicate_compliance_item(
    db: Session, project_id: uuid.UUID, checklist_item_id: uuid.UUID
) -> ProjectComplianceItem | None:
    return db.query(ProjectComplianceItem).filter(
        ProjectComplianceItem.project_id == project_id,
        ProjectComplianceItem.checklist_item_id == checklist_item_id,
    ).first()


def create_project_compliance_item(
    db: Session, project_id: uuid.UUID, checklist_item_id: uuid.UUID
) -> ProjectComplianceItem:
    item = ProjectComplianceItem(
        project_id=project_id,
        checklist_item_id=checklist_item_id,
        status="pending",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def bulk_create_project_items(
    db: Session, project_id: uuid.UUID, standard_id: uuid.UUID
) -> list[ProjectComplianceItem]:
    items = get_checklist_items_by_standard(db, standard_id)
    existing = {
        pci.checklist_item_id
        for pci in db.query(ProjectComplianceItem).filter(
            ProjectComplianceItem.project_id == project_id,
            ProjectComplianceItem.checklist_item_id.in_([i.id for i in items]),
        ).all()
    }
    created = []
    for item in items:
        if item.id not in existing:
            pci = ProjectComplianceItem(
                project_id=project_id,
                checklist_item_id=item.id,
                status="pending",
            )
            db.add(pci)
            created.append(pci)
    db.commit()
    for pci in created:
        db.refresh(pci)
    return created


def get_project_compliance_items(
    db: Session, project_id: uuid.UUID, standard_id: uuid.UUID | None = None
) -> list[dict]:
    query = (
        db.query(ProjectComplianceItem, ComplianceChecklistItem, ComplianceStandard)
        .join(
            ComplianceChecklistItem,
            ProjectComplianceItem.checklist_item_id == ComplianceChecklistItem.id,
        )
        .join(
            ComplianceStandard,
            ComplianceChecklistItem.standard_id == ComplianceStandard.id,
        )
        .filter(ProjectComplianceItem.project_id == project_id)
    )
    if standard_id:
        query = query.filter(ComplianceChecklistItem.standard_id == standard_id)
    rows = query.order_by(ProjectComplianceItem.created_at.desc()).all()
    result = []
    for pci, cci, cs in rows:
        result.append({
            "id": pci.id,
            "project_id": pci.project_id,
            "checklist_item_id": pci.checklist_item_id,
            "status": pci.status,
            "evidence_document_id": pci.evidence_document_id,
            "notes": pci.notes,
            "reviewed_by": pci.reviewed_by,
            "reviewed_at": pci.reviewed_at,
            "created_at": pci.created_at,
            "updated_at": pci.updated_at,
            "standard_name": cs.name,
            "category": cci.category,
            "requirement": cci.requirement,
            "is_mandatory": cci.is_mandatory,
        })
    return result


def get_project_compliance_item(
    db: Session,
    item_id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    checklist_item_id: uuid.UUID | None = None
) -> ProjectComplianceItem | None:
    query = db.query(ProjectComplianceItem)
    if item_id:
        query = query.filter(ProjectComplianceItem.id == item_id)
    if project_id:
        query = query.filter(ProjectComplianceItem.project_id == project_id)
    if checklist_item_id:
        query = query.filter(ProjectComplianceItem.checklist_item_id == checklist_item_id)
    return query.first()


def update_project_compliance_item(
    db: Session, item_id: uuid.UUID, **kwargs
) -> ProjectComplianceItem | None:
    item = get_project_compliance_item(db, item_id)
    if not item:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def review_project_compliance_item(
    db: Session, item_id: uuid.UUID, reviewed_by: uuid.UUID
) -> ProjectComplianceItem | None:
    from datetime import datetime

    item = get_project_compliance_item(db, item_id)
    if not item:
        return None
    item.reviewed_by = reviewed_by
    item.reviewed_at = datetime.now(UTC)
    db.commit()
    db.refresh(item)
    return item


def get_compliance_summary(db: Session, project_id: uuid.UUID) -> list[dict]:
    rows = (
        db.query(
            ComplianceStandard.name,
            func.count(ProjectComplianceItem.id).label("total_items"),
            func.count(ProjectComplianceItem.id).filter(
                ProjectComplianceItem.status == "compliant"
            ).label("compliant_count"),
            func.count(ProjectComplianceItem.id).filter(
                ProjectComplianceItem.status == "non_compliant"
            ).label("non_compliant_count"),
            func.count(ProjectComplianceItem.id).filter(
                ProjectComplianceItem.status == "pending"
            ).label("pending_count"),
            func.count(ProjectComplianceItem.id).filter(
                ProjectComplianceItem.status == "na"
            ).label("na_count"),
        )
        .join(
            ComplianceChecklistItem,
            ProjectComplianceItem.checklist_item_id == ComplianceChecklistItem.id,
        )
        .join(
            ComplianceStandard,
            ComplianceChecklistItem.standard_id == ComplianceStandard.id,
        )
        .filter(ProjectComplianceItem.project_id == project_id)
        .group_by(ComplianceStandard.name)
        .order_by(ComplianceStandard.name)
        .all()
    )
    result = []
    for name, total, compliant, non_compliant, pending, na in rows:
        applicable = total - na
        pct = (compliant / applicable * 100) if applicable > 0 else 0.0
        result.append({
            "standard_name": name,
            "total_items": total,
            "compliant_count": compliant,
            "non_compliant_count": non_compliant,
            "pending_count": pending,
            "na_count": na,
            "compliance_percentage": round(pct, 2),
        })
    return result
