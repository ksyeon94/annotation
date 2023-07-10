import json
import re


단어_dict={}
숫자_dict={}
단어_file=["무기체계.json", "함급.json", "훈련_1.json"]
def open_json(file, dict):
    with open(file=file, mode='r', encoding='utf-8') as f:
        read_file=json.load(f)
        for i in read_file:
            dict[i]=read_file[i]
    return dict

for i in 단어_file:        
    open_json(i, 단어_dict)

open_json("단위.json", 숫자_dict)    


with open(file='/home/rlatmddus159/ner/국방/gukbang (1) copy.txt', encoding='utf-8', mode='r') as f:
    entity_id=0
    num=0
    for text in f.readlines():
        json_dict={}
        json_dict["id"]=num
        json_dict["text"]=text
        json_dict["entities"]=[]
        json_dict["relation"]=[]
        for 클래스 in 단어_dict:
            for 인스턴스 in 단어_dict[클래스]:
                entity_dict={}
                if 인스턴스 in text:
                    entity_id=entity_id+1
                    entity_dict["id"]=entity_id
                    entity_dict['label']=클래스
                    entity_dict['start_offset']=text.index(인스턴스)
                    entity_dict['end_offset']=text.index(인스턴스)+len(인스턴스)
                    json_dict["entities"].append(entity_dict)
            
        json_dict={}
        json_dict["id"]=num
        json_dict["text"]=text.strip('\n')
        json_dict["entities"]=[]
        json_dict["relation"]=[]
        num+=1
        print(json_dict)
                    
'''  for 클래스 in 숫자_dict:
            for 인스턴스 in 숫자_dict[클래스]:
                if 인스턴스 in text:
                    텍스트_숫자 = re.findall(r'\d+', text)
                    for i in 텍스트_숫자:
                        가정한_숫자=i+인스턴스
                        if 가정한_숫자 in text:'''