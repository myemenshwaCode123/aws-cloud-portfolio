import json
import boto3
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock    = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb   = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

CONVERSATIONS_TABLE = os.environ['CONVERSATIONS_TABLE']
KB_TABLE             = os.environ['KNOWLEDGE_BASE_TABLE']
SNS_TOPIC_ARN        = os.environ['SNS_TOPIC_ARN']
CHAT_MODEL_ID        = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'
EMBED_MODEL_ID       = 'amazon.titan-embed-text-v2:0'

conv_table = dynamodb.Table(CONVERSATIONS_TABLE)
kb_table   = dynamodb.Table(KB_TABLE)

SYSTEM_PROMPT = """You are Aria, a helpful customer service rep for TechCorp.
RULES:
- Be polite, concise, helpful. Under 150 words.
- If you cannot resolve an issue, start your response with "ESCALATE_TO_HUMAN"
- Use the [Knowledge Base Context] provided, if any, to ground your answer accurately
- Do not discuss competitors or promise unreleased features
"""


def put_metric(name, value, unit='Count'):
    cloudwatch.put_metric_data(Namespace='AICustomerBot', MetricData=[{'MetricName': name, 'Value': value, 'Unit': unit}])


def get_embedding(text: str) -> list:
    body = json.dumps({"inputText": text})
    response = bedrock.invoke_model(modelId=EMBED_MODEL_ID, body=body, contentType='application/json', accept='application/json')
    return json.loads(response['body'].read())['embedding']


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0


def get_relevant_context(user_message: str, top_k: int = 2, min_score: float = 0.5) -> str:
    """RAG retrieval: embed the question, find the closest FAQ answers via cosine similarity."""
    query_embedding = get_embedding(user_message)
    items = kb_table.scan().get('Items', [])

    scored = []
    for item in items:
        embedding = json.loads(item['embedding'])
        score = cosine_similarity(query_embedding, embedding)
        scored.append((score, item['question'], item['answer']))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_matches = [m for m in scored[:top_k] if m[0] >= min_score]

    if not top_matches:
        return ""
    return "\n\n".join([f"Q: {q}\nA: {a}" for _, q, a in top_matches])


def get_conversation_history(session_id: str, limit: int = 10) -> list:
    response = conv_table.query(
        KeyConditionExpression='session_id = :sid',
        ExpressionAttributeValues={':sid': session_id},
        ScanIndexForward=False, Limit=limit
    )
    items = sorted(response.get('Items', []), key=lambda x: x['timestamp'])
    return [{'role': i['role'], 'content': i['content']} for i in items]


def save_message(session_id, role, content):
    conv_table.put_item(Item={
        'session_id': session_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'role': role, 'content': content
    })


def call_bedrock(messages):
    body = json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 512,
        'system': SYSTEM_PROMPT,
        'messages': messages
    })
    response = bedrock.invoke_model(modelId=CHAT_MODEL_ID, body=body, contentType='application/json', accept='application/json')
    return json.loads(response['body'].read())['content'][0]['text']


def lambda_handler(event, context):
    start_time = datetime.now(timezone.utc)
    try:
        body       = json.loads(event.get('body', '{}'))
        session_id = body.get('session_id', 'default-session')
        user_msg   = body.get('message', '').strip()

        if not user_msg:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Message cannot be empty'})}

        history = get_conversation_history(session_id)
        kb_context = get_relevant_context(user_msg)

        messages_for_model = history.copy()
        if kb_context:
            messages_for_model.append({
                'role': 'user',
                'content': f"[Knowledge Base Context]\n{kb_context}\n\n[Customer Message]\n{user_msg}"
            })
            put_metric('RAGContextUsed', 1)
        else:
            messages_for_model.append({'role': 'user', 'content': user_msg})

        ai_response = call_bedrock(messages_for_model)

        needs_escalation = ai_response.upper().startswith('ESCALATE_TO_HUMAN')
        if needs_escalation:
            ai_response = ai_response.replace('ESCALATE_TO_HUMAN', '').strip()
            put_metric('HumanEscalations', 1)
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"🔔 AI Bot: Escalation needed | Session {session_id}",
                Message=f"User: {user_msg}\nBot: {ai_response}"
            )

        save_message(session_id, 'user', user_msg)
        save_message(session_id, 'assistant', ai_response)

        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        put_metric('MessageProcessed', 1)
        put_metric('ResponseTimeMs', duration_ms, 'Milliseconds')

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'response': ai_response, 'session_id': session_id,
                'needs_escalation': needs_escalation,
                'used_knowledge_base': bool(kb_context),
                'response_time_ms': duration_ms
            })
        }

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        put_metric('BotErrors', 1)
        return {'statusCode': 500, 'body': json.dumps({'error': 'Internal server error'})}
