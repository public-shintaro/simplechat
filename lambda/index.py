import json
import re
import urllib.error
import urllib.parse
import urllib.request


def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
    match = re.search("arn:aws:lambda:([^:]+):", arn)
    if match:
        return match.group(1)
    return "us-east-1"  # デフォルト値


# オリジナルの実装（コメントアウト）
"""
def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        region = None
        if context:
            region = extract_region_from_arn(context.invoked_function_arn)
        else:
            region = "us-east-1"

        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=region,
        )

        prompt_config = {
            "prompt": message,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        body = json.dumps(prompt_config)

        response = bedrock.invoke_model(
            body=body,
            modelId="anthropic.claude-v2",
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response.get('body').read())
        assistant_response = response_body.get('completion')

        messages = conversation_history.copy()
        messages.append({
            "role": "user",
            "content": message
        })
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })

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
                "response": assistant_response,
                "conversationHistory": messages
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
"""


# 新しい実装（FastAPI対応）
def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # リクエストボディの解析
        body = json.loads(event["body"])
        message = body["message"]
        conversation_history = body.get("conversationHistory", [])

        # FastAPI エンドポイントのURL
        api_url = "https://e25a-34-19-51-187.ngrok-free.app/generate"

        # リクエストデータの準備
        request_data = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        # JSONデータをエンコード
        json_data = json.dumps(request_data).encode("utf-8")

        # リクエストオブジェクトの作成
        req = urllib.request.Request(
            api_url,
            data=json_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            # APIリクエストの送信
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode("utf-8"))

                # 応答の取得
                assistant_response = response_data["generated_text"]

                # 会話履歴の更新
                messages = conversation_history.copy()
                messages.append({"role": "user", "content": message})
                messages.append({"role": "assistant", "content": assistant_response})

                # 成功レスポンスの返却
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                        "Access-Control-Allow-Methods": "OPTIONS,POST",
                    },
                    "body": json.dumps(
                        {
                            "success": True,
                            "response": assistant_response,
                            "conversationHistory": messages,
                        }
                    ),
                }

        except urllib.error.URLError as e:
            print("Error calling FastAPI:", str(e))
            raise Exception(f"Failed to call FastAPI: {str(e)}")

    except Exception as error:
        print("Error:", str(error))

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
            },
            "body": json.dumps({"success": False, "error": str(error)}),
        }
