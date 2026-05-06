from backend.rag.ingest import ingest_document

sample_set = [
    {'doc_id': 'gold-J.P.-Morgan',
     'source_type': 'pdf',
     'source_path': "../oxford-data-pack/Gold - Sample Set/The case against gold and why it’s wrong _ J.P. Morgan Private Bank U.S.pdf",
     'tags': ['gold']},

     {'doc_id': 'gold-UBP-Moves',
     'source_type': 'pdf',
     'source_path': '../oxford-data-pack/Gold - Sample Set/UBP Moves - Strategic - Gold - Volatility creates buying opportunity.pdf',
     'tags': ['gold']}
]

for sample in sample_set:
    print(ingest_document(sample['doc_id'], sample['source_type'], sample['source_path'], sample['tags']))