# -*- coding: utf-8 -*-
from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel 
import openai
import os
from pathlib import Path
# .envから
from dotenv import load_dotenv
load_dotenv('.env')
class Generate(BaseModel):
    keyword: str
    generate_sentence: Union [str , None] = None
    Image : Union [str , None] = None

# インスタンス作成
app = FastAPI() 
# api_keyが存在しない場合はNoneを返す

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Model.list()

@app.post("/gpt")

async def create_generate(generate: Generate):
    # htmlのmethodを参照
    
        # htmlでname=formから取得
        # 自動でjsonにしてくれる
        key = generate.keyword

        response = openai.Completion.create(
        model="text-davinci-003",
        # 入力されたキーワードを引数に
        prompt= generate_prompt(key),
        # 0~2 数値が高いと幅広く解答し、低いと詳細な回答をする
        temperature=1,
        max_tokens = 25
        )

        # imagesまでのパス
        file_path = Path("C:\\プログラミング\\python\\back API\\back\\media\\images")
        # images//keyのディレクトリを作成
        os.makedirs(str(file_path)+"\\" + key , exist_ok = True)
        # ファイル名をキーワードに、中に文字列を記載 
        # 注意！パスの区切りは必ず\\でやること
        file_path = Path("C:\\プログラミング\\python\\back API\\back\\media\\images\\"+ key + "\\" + key + ".txt")
        # a+でファイルが無い場合、生成して中に生成文字を書き込み
        f = open(file_path, mode='a+',encoding="shift-jis")
        response_text = response.choices[0].text.replace('\n','')
        response_text = response.choices[0].text.strip()        
        f.write(response_text)
        # 改行
        f.write("\n")
        f.close() 

        generate.keyword = key
        # 生成文を格納
        generate.generate_sentence = response_text

        # json形式で中のデータを全て返す
        print("generation complete")
        return generate.dict()
 



def generate_prompt(key):

    result = """5文字・7文字・5文字の日本語の塊からできた文章を俳句と呼びます。
    この俳句を出力してください。
    与えられる文字を以下、テーマと呼びます。
    テーマは、アルファベット又は記号から構成されています。
    以下は日本語で書かれた例です。

    テーマ: docker
    たまげたな　コンテナしんしゅつ　docker

    テーマ: python
    pythonの　科学技術は　とてもすごい

    このとき、以下の指示に従って出力してください。

・ 5文字・7文字・5文字の日本語で書かれた塊をそれぞれ、a,b,cとします。
・ a,b,cは完全に5文字・7文字・5文字でなくてもいいですが、それくらいの文字で収めてください。
・ 文字を5・7・5のいずれかの節に配置してください。
・ 俳句のテーマは{}です。必ずこの単語と関連している言葉や、内容を含んだ俳句を出力してください。
・ 文章を分けずに一行で出力してください。
・「分かりました」などの余計な文章は出力せず、俳句だけを出力してください。
・ 俳句は1つのみ生成してください。
・ 必ず1行で出力してください。""" .format(key)# formで入力したキーワードを、プロンプト中の{}に設定
    # プロンプトとして渡す
    return result

