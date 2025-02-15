"""
Database seeder for populating the database with realistic test data.
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional
import faker
from sqlalchemy.orm import Session
from app.models.metadata import MetadataField, DocumentType, MetadataType
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.database import SessionLocal

fake = faker.Faker()

def create_metadata_fields(db: Session) -> List[MetadataField]:
    """Create a variety of metadata fields"""
    # Check if default metadata fields already exist
    existing = db.query(MetadataField).all()
    if existing:
        return existing

    fields = [
        MetadataField(
            name="department",
            description="Department that owns the document",
            field_type=MetadataType.ENUM,
            enum_values="HR,Finance,Legal,Engineering,Marketing",
            validation_rules='{"required": true}'
        ),
        MetadataField(
            name="document_date",
            description="Date of document creation",
            field_type=MetadataType.DATE,
            validation_rules='{"required": true}'
        ),
        MetadataField(
            name="confidential",
            description="Whether the document is confidential",
            field_type=MetadataType.BOOLEAN,
            default_value="false"
        ),
        MetadataField(
            name="tags",
            description="Document tags",
            field_type=MetadataType.TEXT,
            is_multi_valued=True
        ),
        MetadataField(
            name="revision_number",
            description="Document revision number",
            field_type=MetadataType.INTEGER,
            default_value="1"
        )
    ]
    
    for field in fields:
        db.add(field)
    db.commit()
    
    return fields

def create_document_types(db: Session, metadata_fields: List[MetadataField]) -> List[DocumentType]:
    # Check if document types already exist to avoid duplicate insertion
    existing = db.query(DocumentType).all()
    if existing:
        return existing

    doc_types = [
        {
            "name": "Contract",
            "description": "Legal contracts and agreements",
            "required_fields": ["department", "document_date", "confidential"]
        },
        {
            "name": "Report",
            "description": "Business reports and analytics",
            "required_fields": ["department", "document_date", "tags"]
        },
        {
            "name": "Policy",
            "description": "Company policies and procedures",
            "required_fields": ["department", "revision_number", "confidential"]
        }
    ]
    
    created_types = []
    field_dict = {field.name: field for field in metadata_fields}
    
    for doc_type in doc_types:
        dt = DocumentType(
            name=doc_type["name"],
            description=doc_type["description"]
        )
        db.add(dt)
        db.flush()  # Get the ID without committing
        
        # Associate metadata fields
        for field_name in doc_type["required_fields"]:
            if field_name in field_dict:
                dt.metadata_fields.append(field_dict[field_name])
        
        created_types.append(dt)
    
    db.commit()
    return created_types

def create_sample_documents(db: Session, document_types: List[DocumentType], num_documents: int = 50):
    """Create sample documents with metadata and versions"""
    tags = ["important", "draft", "reviewed", "archived", "pending", "approved"]
    
    for _ in range(num_documents):
        doc_type = random.choice(document_types)
        
        # Generate metadata based on document type
        metadata_values = {}
        for field in doc_type.metadata_fields:
            if field.field_type == MetadataType.ENUM:
                metadata_values[field.name] = random.choice(field.enum_values.split(','))
            elif field.field_type == MetadataType.DATE:
                metadata_values[field.name] = (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
            elif field.field_type == MetadataType.BOOLEAN:
                metadata_values[field.name] = random.choice([True, False])
            elif field.field_type == MetadataType.INTEGER:
                metadata_values[field.name] = random.randint(1, 10)
            elif field.field_type == MetadataType.TEXT and field.is_multi_valued:
                metadata_values[field.name] = random.sample(tags, random.randint(1, 3))
        
        # Create document
        doc = Document(
            title=fake.catch_phrase(),
            content=fake.text(max_nb_chars=1000),
            file_name=f"{fake.uuid4()}.txt",
            file_path=f"uploads/{fake.uuid4()}.txt",
            file_size=random.randint(1000, 1000000),
            document_type_id=doc_type.id,
            metadata_values=metadata_values
        )
        db.add(doc)
        db.flush()
        
        # Create 1-3 versions for each document
        for version_num in range(1, random.randint(2, 4)):
            version = DocumentVersion(
                document_id=doc.id,
                version_number=version_num,
                title=doc.title,
                content=fake.text(max_nb_chars=1000),
                file_name=f"{fake.uuid4()}_v{version_num}.txt",
                file_path=f"uploads/{fake.uuid4()}_v{version_num}.txt",
                file_size=random.randint(1000, 1000000)
            )
            db.add(version)
    
    db.commit()

def seed_database(num_documents: int = 50, db: Optional[Session] = None):
    """Main function to seed the database with test data"""
    # Use provided db session (useful for tests) or create a new one
    if not db:
        db = SessionLocal()
    try:
        # Create metadata fields
        print("Creating metadata fields...")
        metadata_fields = create_metadata_fields(db)
        
        # Create document types
        print("Creating document types...")
        document_types = create_document_types(db, metadata_fields)
        
        # Create sample documents
        print(f"Creating {num_documents} sample documents...")
        create_sample_documents(db, document_types, num_documents)
        
        print("Database seeding completed successfully!")
        
        # Return counts for verification
        return {
            "metadata_fields": len(metadata_fields),
            "document_types": len(document_types),
            "documents": num_documents
        }
    
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()