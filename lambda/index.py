# lambda/index.py
import json
import os
import re  # 正規表現モジュールをインポート
import urllib.request

# FastAPIのURL
FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://9aff-34-142-222-135.ngrok-free.app/generate")


def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
        print("Using model:", FASTAPI_URL)
        
        # Fast API用のリクエストペイロード
        request_payload = json.dumps({
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }).encode("utf-8")
        
        # Fast APIへリクエスト送信
        req = urllib.request.Request(
                FASTAPI_URL,
                data=request_payload,
                headers={"Content-Type": "application/json"},
                method="POST"
        )
        
        # Fast APIからの応答を処理
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
            print("FastAPI raw response:", response_body)
            response_json = json.loads(response_body)

        # 応答の検証
        if "generated_text" not in response_json:
            raise Exception("No generated_text found in FastAPI response")

        assistant_response = response_json["generated_text"]
        
        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                 "success": True,
                 "response": assistant_response
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
