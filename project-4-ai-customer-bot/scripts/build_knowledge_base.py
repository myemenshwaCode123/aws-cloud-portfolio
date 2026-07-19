import boto3
import json

bedrock  = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table    = dynamodb.Table('KnowledgeBase')

def get_embedding(text):
    body = json.dumps({"inputText": text})
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v2:0',
        body=body, 
        contentType='application/json', 
        accept='application/json'
    )
    return json.loads(response['body'].read())['embedding']

with open('../lambda/faq.json') as f:
    faqs = json.load(f)

for i, faq in enumerate(faqs):
    embedding = get_embedding(faq['answer'])
    table.put_item(Item={
        'faq_id': f'faq-{i+1}',
        'question': faq['question'],
        'answer': faq['answer'],
        'embedding': json.dumps(embedding)
    })
    print(f"Indexed: {faq['question']}")

print(f"\n✅ Indexed {len(faqs)} FAQs into KnowledgeBase table.")
