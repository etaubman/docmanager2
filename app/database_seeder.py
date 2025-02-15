"""
Database seeder for populating the database with realistic test data.
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import faker
from sqlalchemy.orm import Session
from app.models.metadata import MetadataField, DocumentType, MetadataType
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.category import Category
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
            db.flush()  # Get ID without committing
            
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