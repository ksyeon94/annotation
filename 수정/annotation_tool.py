import json
import re


단어_dict={}
숫자_dict={}
단어_file=["무기체계.json", "함급.json", "훈련.json", "조직_직책.json", "위치.json"]
###################################################다운받고 이부분 수정###################################################
용어_dir='/Users/gimseung-yeon/연습/annotation/용어정리/' #다운받은폴더위치
텍스트파일='gukbangnews.txt'  #국방기사 파일이름(용어_dir 폴더 하위로 옮겨주세요)
###################################################다운받고 이부분 수정###################################################
def open_json(file, dict):  #파일을 열어서 읽은뒤 dict에 저장
    with open(file=file, mode='r', encoding='utf-8') as f:
        read_file=json.load(f)
        for i in read_file:
            dict[i]=read_file[i]
    return dict

for i in 단어_file:        # 단어 dict 생성
    open_json(용어_dir+i, 단어_dict)

open_json(용어_dir+"단위.json", 숫자_dict)    #숫자 dict 생성

def 합치기(dict):
    len_entity=len(dict['entities'])
    new_json_dict=dict
    #"entities": [{"id": 50, "label": "EX", "start_offset": 12, "end_offset": 14}, {"id": 51, "label": "EX", "start_offset": 8, "end_offset": 12}, {"id": 52, "label": "EX", "start_offset": 47, "end_offset": 49}, {"id": 53, "label": "직책", "start_offset": 17, "end_offset": 20}], "relation": []}
    for pre_entity in dict['entities']:
        #valid_list.append([entity["start_offset"],entity["end_offset"]]) #[[12,14], [8,12],[47,49], [14,20]]
        for next_entity in dict['entities']:
            if pre_entity["end_offset"]==next_entity["start_offset"]:
                new_entity=next_entity
                new_entity["start_offset"]=pre_entity["start_offset"]
                new_json_dict['entities'].remove(pre_entity)
                new_json_dict['entities'].remove(next_entity)
                new_json_dict['entities'].append(new_entity)
                new_id=0
                for i in range(len(dict['entities'])):
                    dict['entities'][i]["id"]=new_id
                    new_id+=1
    return new_json_dict

def new_합치기(entity_dict):
    new_entity_dict = entity_dict.copy()
    entities = new_entity_dict['entities'][:]
    remove_indices = []
    for i, pre_entity in enumerate(entities):
        for j, next_entity in enumerate(entities):
            if i == j:
                continue
            if next_entity["end_offset"] > pre_entity["end_offset"] > next_entity["start_offset"]:
                remove_indices.append(i)
                if j not in remove_indices:
                    remove_indices.append(j)
    new_entity_dict['entities'] = [entity for i, entity in enumerate(entities) if i not in remove_indices]
    return new_entity_dict




def 겹치는것(entity_dict):
    new_entity_dict = entity_dict.copy()
    entities = new_entity_dict['entities'][:]
    remove_indices = []
    for i, pre_entity in enumerate(entities):
        for j, next_entity in enumerate(entities):
            if i == j:
                continue
            if pre_entity["end_offset"] == next_entity["end_offset"] :
                if pre_entity["start_offset"] > next_entity["start_offset"]:
                    remove_indices.append(i)
                else:
                    remove_indices.append(j)
            elif pre_entity["start_offset"]==next_entity["start_offset"]:
                if pre_entity["end_offset"] > next_entity["end_offset"]:
                    remove_indices.append(j)
                else:
                    remove_indices.append(i)
                
    new_entity_dict['entities'] = [entity for i, entity in enumerate(entities) if i not in remove_indices]
    return new_entity_dict


def auto_annotate(file_name):
    with open(file=file_name, encoding='utf-8', mode='r') as f:
        with open(file='/Users/gimseung-yeon/연습/annotation/결과.json', encoding='utf-8', mode='w') as d:
            entity_id=0
            num=0
            for text in f.readlines():
                json_dict={}
                json_dict["id"]=num
                json_dict["text"]=text.strip('\n')
                json_dict["entities"]=[]
                json_dict["relation"]=[]
                for 클래스 in 단어_dict:
                    for 인스턴스 in 단어_dict[클래스]: #"해군"
                        entity_dict={}
                        indices = [i.start() for i in re.finditer(인스턴스, text)] #"해군", "텍스트"
                        for entity_start in indices:
                            entity_dict={}
                            entity_id=entity_id+1
                            entity_dict["id"]=entity_id
                            entity_dict['label']=클래스
                            entity_dict['start_offset']=entity_start
                            entity_dict['end_offset']=entity_start+len(인스턴스)         
                            json_dict["entities"].append(entity_dict)
                

                for 클래스 in 숫자_dict:
                    for 인스턴스 in 숫자_dict[클래스]:
                        if 인스턴스 in text:
                            텍스트_숫자 = re.findall(r'\d+', text)
                            added_combinations = []  # 이미 추가한 숫자와 인스턴스의 조합을 저장하는 리스트
                            for i in 텍스트_숫자:
                                숫자_인스턴스 = i + 인스턴스
                                if 숫자_인스턴스 in text and 숫자_인스턴스 not in added_combinations:
                                    entity_dict = {}
                                    entity_id += 1
                                    entity_dict["id"] = entity_id
                                    entity_dict['label'] = 클래스
                                    entity_dict['start_offset'] = text.index(숫자_인스턴스)
                                    entity_dict['end_offset'] = text.index(숫자_인스턴스) + len(숫자_인스턴스)         
                                    json_dict["entities"].append(entity_dict)
                                    added_combinations.append(숫자_인스턴스)  # 조합을 추가한 후 리스트에 저장

                num+=1
                
                for i in range(3):
                    json_dict=겹치는것(json_dict)
                for i in range(3):
                    합치기(json_dict)
                    json_dict=겹치는것(json_dict)
            
                json.dump(json_dict, d, ensure_ascii=False)
                d.write('\n')          

auto_annotate(용어_dir+텍스트파일)
