"""
Database seeder for populating the database with realistic test data.
"""
import os
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import faker
from sqlalchemy.orm import Session
from app.models.metadata import MetadataField, DocumentType, MetadataType
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.category import Category
from app.database import SessionLocal, Base, engine

fake = faker.Faker()

def create_document_file(file_path: str, is_markdown: bool = False) -> int:
    """Create a physical document file and return its size"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    content = []
    if is_markdown:
        content = [
            f"# {fake.catch_phrase()}",
            "",
            f"## Overview",
            fake.text(max_nb_chars=200),
            "",
            f"## Details",
            fake.text(max_nb_chars=300),
            "",
            "### Key Points",
            "- " + fake.sentence(),
            "- " + fake.sentence(),
            "- " + fake.sentence(),
            "",
            f"## Notes",
            fake.text(max_nb_chars=200)
        ]
    else:
        content = [
            fake.catch_phrase(),
            "",
            fake.text(max_nb_chars=800)
        ]
    
    content = "\n".join(content)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return len(content.encode('utf-8'))

def cleanup_uploads():
    """Clean up all files in the uploads directory"""
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

def truncate_database(db: Session):
    """Truncate all tables in the database"""
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        db.commit()
    except Exception as e:
        print(f"Error truncating database: {e}")
        db.rollback()
        raise

def create_metadata_fields(db: Session) -> List[MetadataField]:
    """Create a variety of metadata fields"""
    # Check if default metadata fields already exist
    existing = db.query(MetadataField).all()
    if existing:
        return existing

    fields = [
        MetadataField(
            name="department",
            display_name="Department",
            description="Department that owns the document",
            field_type=MetadataType.ENUM,
            enum_values="HR,Finance,Legal,Engineering,Marketing",
            validation_rules='{"required": true}'
        ),
        MetadataField(
            name="document_date",
            display_name="Document Date",
            description="Date of document creation",
            field_type=MetadataType.DATE,
            validation_rules='{"required": true}'
        ),
        MetadataField(
            name="confidential",
            display_name="Confidential",
            description="Whether the document is confidential",
            field_type=MetadataType.BOOLEAN,
            default_value="false"
        ),
        MetadataField(
            name="tags",
            display_name="Tags",
            description="Document tags",
            field_type=MetadataType.TEXT,
            is_multi_valued=True
        ),
        MetadataField(
            name="revision_number",
            display_name="Revision Number",
            description="Document revision number",
            field_type=MetadataType.INTEGER,
            default_value="1"
        )
    ]
    
    for field in fields:
        db.add(field)
    db.commit()
    
    return fields

def create_categories(db: Session) -> List[Category]:
    """Create hierarchical categories"""
    # Check if categories already exist
    existing = db.query(Category).all()
    if existing:
        return existing

    # Define base categories
    categories = [
        {
            "name": "Legal",
            "description": "Legal documents",
            "subcategories": [
                {"name": "Contracts", "description": "Legal contracts and agreements"},
                {"name": "Compliance", "description": "Regulatory compliance documents"},
                {"name": "Patents", "description": "Patent documents"}
            ]
        },
        {
            "name": "HR",
            "description": "Human Resources documents",
            "subcategories": [
                {"name": "Policies", "description": "HR policies"},
                {"name": "Employee Records", "description": "Employee documentation"}
            ]
        },
        {
            "name": "Finance",
            "description": "Financial documents",
            "subcategories": [
                {"name": "Reports", "description": "Financial reports"},
                {"name": "Budgets", "description": "Budget documents"},
                {"name": "Invoices", "description": "Invoice documents"}
            ]
        }
    ]
    
    created_categories = []
    
    # Create main categories and their subcategories
    for cat_data in categories:
        # Create main category
        try:
            main_cat = Category(name=cat_data["name"], description=cat_data["description"])
            db.add(main_cat)
            db.flush()  # Get ID without committing
            created_categories.append(main_cat)
            
            # Create subcategories
            for sub_data in cat_data["subcategories"]:
                sub_cat = Category(name=sub_data["name"], description=sub_data["description"])
                db.add(sub_cat)
                db.flush()  # Get ID without committing
                # Set up hierarchy
                main_cat.children.append(sub_cat)
                created_categories.append(sub_cat)
        except Exception as e:
            print(f"Error creating category {cat_data['name']}: {str(e)}")
            db.rollback()
            raise
    
    try:
        db.commit()
    except Exception as e:
        print(f"Error committing categories: {str(e)}")
        db.rollback()
        raise
    
    return created_categories

def create_document_types(db: Session, metadata_fields: List[MetadataField]) -> List[DocumentType]:
    """Create document types with metadata field and category associations"""
    # Check if document types already exist
    existing = db.query(DocumentType).all()
    if existing:
        return existing

    # Get categories
    categories = db.query(Category).all()
    cat_dict = {cat.name: cat for cat in categories}

    doc_types = [
        {
            "name": "Contract",
            "description": "Legal contracts and agreements",
            "required_fields": ["department", "document_date", "confidential"],
            "categories": ["Legal", "Contracts"]
        },
        {
            "name": "Report",
            "description": "Business reports and analytics",
            "required_fields": ["department", "document_date", "tags"],
            "categories": ["Finance", "Reports"]
        },
        {
            "name": "Policy",
            "description": "Company policies and procedures",
            "required_fields": ["department", "revision_number", "confidential"],
            "categories": ["HR", "Policies"]
        }
    ]
    
    created_types = []
    field_dict = {field.name: field for field in metadata_fields}
    
    for doc_type in doc_types:
        try:
            dt = DocumentType(
                name=doc_type["name"],
                description=doc_type["description"]
            )
            db.add(dt)
            db.flush()  # Get ID without committing
            
            # Associate metadata fields
            for field_name in doc_type["required_fields"]:
                if field_name in field_dict:
                    dt.metadata_fields.append(field_dict[field_name])
            
            # Associate categories
            for cat_name in doc_type["categories"]:
                if cat_name in cat_dict:
                    dt.categories.append(cat_dict[cat_name])
            
            created_types.append(dt)
        except Exception as e:
            print(f"Error creating document type {doc_type['name']}: {str(e)}")
            db.rollback()
            raise
    
    try:
        db.commit()
    except Exception as e:
        print(f"Error committing document types: {str(e)}")
        db.rollback()
        raise
    
    return created_types

def create_sample_documents(db: Session, document_types: List[DocumentType], num_documents: int = 50) -> None:
    """Create sample documents with metadata and versions"""
    tags = ["important", "draft", "reviewed", "archived", "pending", "approved"]
    
    try:
        for _ in range(num_documents):
            doc_type = random.choice(document_types)
            is_markdown = random.choice([True, False])
            file_ext = ".md" if is_markdown else ".txt"
            
            # Generate metadata based on document type
            metadata_values: Dict = {}
            for field in doc_type.metadata_fields:
                if field.field_type == MetadataType.ENUM and field.enum_values:
                    metadata_values[field.name] = random.choice(field.enum_values.split(','))
                elif field.field_type == MetadataType.DATE:
                    metadata_values[field.name] = (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
                elif field.field_type == MetadataType.BOOLEAN:
                    metadata_values[field.name] = random.choice([True, False])
                elif field.field_type == MetadataType.INTEGER:
                    metadata_values[field.name] = random.randint(1, 10)
                elif field.field_type == MetadataType.TEXT and field.is_multi_valued:
                    metadata_values[field.name] = random.sample(tags, random.randint(1, 3))
            
            # Create main document file
            file_id = fake.uuid4()
            file_name = f"{file_id}{file_ext}"
            file_path = os.path.join("uploads", file_name)
            file_size = create_document_file(file_path, is_markdown)
            
            # Create document
            doc = Document(
                title=fake.catch_phrase(),
                content=fake.text(max_nb_chars=1000),
                file_name=file_name,
                file_path=file_path,
                file_size=file_size,
                document_type_id=doc_type.id,
                metadata_values=metadata_values
            )
            db.add(doc)
            db.flush()  # Get ID without committing
            
            # Create 1-3 versions for each document
            for version_num in range(1, random.randint(2, 4)):
                version_file_name = f"{file_id}_v{version_num}{file_ext}"
                version_file_path = os.path.join("uploads", version_file_name)
                version_file_size = create_document_file(version_file_path, is_markdown)
                
                version = DocumentVersion(
                    document_id=doc.id,
                    version_number=version_num,
                    title=doc.title,
                    content=fake.text(max_nb_chars=1000),
                    file_name=version_file_name,
                    file_path=version_file_path,
                    file_size=version_file_size
                )
                db.add(version)
        
        db.commit()
    except Exception as e:
        print(f"Error creating sample documents: {str(e)}")
        db.rollback()
        raise

def seed_database(num_documents: int = 50, db: Optional[Session] = None) -> Dict[str, int]:
    """Main function to seed the database with test data"""
    # Use provided db session (useful for tests) or create a new one
    if not db:
        db = SessionLocal()
    try:
        print("Cleaning up existing data...")
        truncate_database(db)
        cleanup_uploads()
        
        # Create metadata fields
        print("Creating metadata fields...")
        metadata_fields = create_metadata_fields(db)
        
        # Create categories
        print("Creating categories...")
        categories = create_categories(db)
        
        # Create document types with category associations
        print("Creating document types...")
        document_types = create_document_types(db, metadata_fields)
        
        # Create sample documents
        print(f"Creating {num_documents} sample documents...")
        create_sample_documents(db, document_types, num_documents)
        
        print("Database seeding completed successfully!")
        
        # Return counts for verification
        return {
            "metadata_fields": len(metadata_fields),
            "categories": len(categories),
            "document_types": len(document_types),
            "documents": num_documents
        }
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        if not db:  # Only close if we created the session
            db.close()

if __name__ == "__main__":
    seed_database()