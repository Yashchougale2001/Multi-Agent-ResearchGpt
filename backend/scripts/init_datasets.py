import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.dataset_loader import dataset_loader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize ChromaDB with sample datasets"""
    logger.info("Starting dataset initialization...")
    
    try:
        dataset_loader.load_all_datasets()
        logger.info("✅ Dataset initialization complete!")
        
        # Show stats
        from app.services.chromadb_service import chroma_service
        stats = chroma_service.get_collection_stats()
        logger.info(f"📊 Total documents in ChromaDB: {stats['total_documents']}")
        
    except Exception as e:
        logger.error(f"❌ Dataset initialization failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()