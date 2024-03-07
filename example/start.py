#!/usr/bin/env python3
import os, sys
from dotenv import load_dotenv
from pathlib import Path

# Work-around to import api package for dev testing
sys.path.insert(0, str(Path(__file__).parent.parent))
from api import create_app
from api.neo4j import init_driver, get_driver, close_driver

# Load credentials from '.env' file
load_dotenv(override=True)
database_uri = os.environ['NEO4J_URI']
username = os.environ['NEO4J_USERNAME']
password = os.environ['NEO4J_PASSWORD']

# Create a new Driver instance
app = create_app()

with app.app_context():
    init_driver(database_uri, username, password)
    print("[LOG] Driver connected to", database_uri)

    cypher_query = '''
    MATCH (m:Movie {title:$movie})<-[:RATED]-(u:User)-[:RATED]->(rec:Movie)
    RETURN distinct rec.title AS recommendation LIMIT 20
    '''

    driver = get_driver()
    with driver.session(database="neo4j") as session:
        results = session.execute_read(
            lambda tx: tx.run(cypher_query, movie="Crimson Tide").data()
        )
        for record in results:
            print(record['recommendation'])

    close_driver()
    print("[LOG] Driver disconnected, exit.")