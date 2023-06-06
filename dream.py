import os
import uuid
from typing import Union
import random
from fastapi import FastAPI
from pydantic import BaseModel 
from pathlib import Path
import requests , json , time
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client

load_dotenv('.env')

templates = Jinja2Templates(directory='templates')
app = FastAPI()


# supabase-py
# url: str = os.environ.get("SUPABASE_URL")
# print("SUPABASE_URL{}".format(url))
# key: str = os.environ.get("SUPABASE_KEY")
# supabase: Client = create_client(url, key)

class Generate(BaseModel):
    keyword: str
    generate_sentence: Union [str , None] = None
    Image : Union [Image , None] = None

api_key = os.getenv("DREAM_API_KEY")
verify = os.getenv("CERTIFICATE_PATH")
BASE_URL = "https://api.luan.tools/api/tasks/"
HEADERS = {
        'Authorization': f'bearer {api_key}',
        'Content-Type': 'application/json'
    }

@app.post("/dream")

def create_generate(generate: Generate):

    # 絵のスタイル、公式参照
    style_id = random.randint(1,21)
    # キーワード
    prompt = generate.keyword
    # 与える画像のパス、イメージを付けれる
    target_img_path=None

    post_payload = json.dumps({
        "use_target_image": bool(target_img_path)
    })
    post_response = requests.request(
        "POST", BASE_URL, headers=HEADERS, data=post_payload , verify=False)

    # Step 2) skip this step if you're not sending a target image otherwise,
    # upload the target image to the url provided in the response from the previous POST request.
    if target_img_path:
        target_image_url = post_response.json()["target_image_url"]
        with open(target_img_path, 'rb') as f:
            fields = target_image_url["fields"]
            fields ["file"] = f.read()
            requests.request("POST", url=target_image_url["url"], files=fields,verify=False)

    # Step 3) make a PUT request to https://api.luan.tools/api/tasks/{task_id}
    # where task id is provided in the response from the request in Step 1.

    # ...ponce.jsonの出力結果はjsonではないので注意 
    task_id = post_response.json()['id']
    task_id_url = f"{BASE_URL}{task_id}"
    put_payload = json.dumps({
        "input_spec": {
            "style": style_id,
            "prompt": prompt,
            "target_image_weight": 0.9,
            "width": 960,
            "height": 1560
    }
    })
    requests.request(
        "PUT", task_id_url, headers=HEADERS, data=put_payload)

    # Step 4) Keep polling for images until the generation completes
    while True:
        # apiのURLと、ヘッダーで宣言した値を日数にgetでリクエスト
        response_json = requests.request(
            "GET", task_id_url, headers=HEADERS).json()

        state = response_json["state"]
  
        #生成に成功したら
        if state == "completed":
            r = requests.request(
                "GET" , response_json["result"])
            # ファイルのパスを設定
            file_path = Path("自分のパスを設定")
            os.makedirs(str(file_path)+"\\" + generate.keyword , exist_ok = True)
            sample_id = uuid.uuid4()
            # 自分のファイルを保存
            # uuidを用いて上書きを防ぐ。
            with open("設置したフォルダのパスを記述" + generate.keyword +"\\" + generate.keyword + "{}({})".format(style_id,sample_id) + ".jpg", 'wb') as image_file:
                image_file.write(r.content)

                # ファイルのアップロード 
            # res = supabase.storage.from_('test').upload("test/images", os.path.abspath("C:\\プログラミング\\python\\back API\\back\\media\\images\\" + generate.keyword +"\\" + generate.keyword + "_I.jpg"))
            # with open("C:\\プログラミング\\python\\back API\\back\\media\\images\\" + generate.keyword +"\\" + generate.keyword + ".jpg", "wb") as image_file:
            
            generate.Image = image_file
            print("image saved successfully :)")
            return templates.TemplateResponse(
                "index.html",
                (
                    
                )
            )

        elif state =="failed":
            print("generation failed :(")
            break

        time.sleep(3)