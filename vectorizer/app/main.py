from vectorizer.app.core.logger import logger
from vectorizer.app.vectordb.vectordb import VectorDB
from vectorizer.app.core.settings import get_settings

settings = get_settings()

def create_collections():
    # Define all available collections
    # FAQ collection works with external data, others require SQLite database
    collections = [
        ("faq", "faq_collection"),                 # Uses external FAQ data from web - always works
        ("flights", "flights_collection"),         # Requires SQLite DB with flights table
        ("hotels", "hotels_collection"),           # Requires SQLite DB with hotels table  
        ("car_rentals", "car_rentals_collection"), # Requires SQLite DB with car_rentals table
        ("trip_recommendations", "excursions_collection")    # Requires SQLite DB with trip_recommendations table
    ]
    
    logger.info(f"Starting vectorizer with {len(collections)} collections to process")
    logger.info(f"Collections: {[f'{table}->{collection}' for table, collection in collections]}")
    
    # Test embedding API connection first
    logger.info("Testing embedding API connection...")
    test_vectordb = VectorDB("test", "test_collection", create_collection=False)
    import asyncio
    connection_ok = asyncio.run(test_vectordb.test_openai_connection())
    
    if not connection_ok:
        logger.error("Embedding API connection failed. Please check your configuration.")
        logger.error("See EMBEDDING_SETUP.md for configuration instructions.")
        return
    
    # Track successful and failed collections
    successful_collections = []
    failed_collections = []

    for table_name, collection_name in collections:
        try:
            logger.info(f"\n" + "="*80)
            logger.info(f"Processing: {table_name} -> {collection_name}")
            logger.info(f"="*80)
            
            logger.info(f"Starting the vector database service for {table_name}")
            vectordb = VectorDB(table_name=table_name, collection_name=collection_name, create_collection=True)
            
            logger.info(f"Starting embedding creation for {collection_name}...")
            vectordb.create_embeddings()
            
            logger.info(f"✅ Embedding generation and storage completed for {collection_name}")
            successful_collections.append((table_name, collection_name))
            
        except Exception as e:
            logger.error(f"❌ An error occurred while processing {table_name}: {type(e).__name__}: {str(e)}")
            logger.exception("Detailed error information:")
            failed_collections.append((table_name, collection_name, str(e)))
            
            # For database-dependent collections, log helpful message
            if table_name != "faq":
                logger.info(f"💡 Note: {table_name} collection requires SQLite database with {table_name} table. "
                           f"If the database is empty or missing, this collection will be skipped.")
    
    # Summary report
    logger.info(f"\n" + "="*80)
    logger.info(f"VECTORIZATION SUMMARY")
    logger.info(f"="*80)
    
    if successful_collections:
        logger.info(f"✅ Successfully processed {len(successful_collections)} collections:")
        for table, collection in successful_collections:
            logger.info(f"   • {table} -> {collection}")
    
    if failed_collections:
        logger.warning(f"❌ Failed to process {len(failed_collections)} collections:")
        for table, collection, error in failed_collections:
            logger.warning(f"   • {table} -> {collection}: {error[:100]}...")
    
    logger.info(f"\n🎯 System is ready with {len(successful_collections)} active collections!")
    
    if not successful_collections:
        logger.error(f"⚠️ No collections were successfully created. Check your configuration and database setup.")

if __name__ == "__main__":
    create_collections()
    logger.info(f"\n🚀 Note: To populate other collections (flights, hotels, car_rentals, excursions), "
               f"ensure the SQLite database at {settings.SQLITE_DB_PATH} contains the required tables with data.")
