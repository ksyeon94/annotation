###########################################################################
label_text_file='/home/rlatmddus159/re/결과물/label.txt'
text_json_file='/home/rlatmddus159/re/활용.json'
###########################################################################
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("rlatmddus159/re")
model = AutoModelForSequenceClassification.from_pretrained("rlatmddus159/re")

# Add "<subj>", "</subj>" to both ends of the subject object and "<obj>", "</obj>" to both ends of the object object.


def 라벨만들기(파일경로):
    label_list=[]
    with open(파일경로, mode='r', encoding='utf-8') as f:
        for label in f.readlines():
            label_list.append(label.strip('\n'))
            
    return label_list
            


def 결과출력(sentence, label_list):
    encodings = tokenizer(sentence, 
                        max_length=128, 
                        truncation=True, 
                        padding="max_length", 
                        return_tensors="pt")
    outputs = model(**encodings)

    logits = outputs['logits']

    preds = torch.argmax(logits, dim=1)
    return(label_list[preds])
    
def read_klue_re(file): #텍스트와 엔티티로 subject, object을 만들고 관계를 각각 만들어내는 코드 / 리스트로 반환
    with open(file, mode='r', encoding='utf-8') as f:
        sentences=[]
        인스턴스_sub=[]
        인스턴스_ob=[]
        for sentence in f.readlines():
            dict=eval(sentence)
            텍스트 = dict["text"] #"해군 함정중에 충무공이순신급이 있는데 길이가 130m이다"
            엔티티 = dict["entities"]
            target_txt = []#["해군", "충무공이순신급", "130m"]
            target_offset =[]
            
            #"해군 함정중에 <s>충무공이순신급</s>이 있는데 길이가 <o>130m</o>이다"
            
            for entity in 엔티티:
                target_txt.append(텍스트[entity['start_offset']:entity['end_offset']]) 
                target_offset.append([entity['start_offset'], entity['end_offset']])
            
            if len(target_txt)>=2:
                for 인스턴스1_idx, 인스턴스1 in enumerate(target_txt):
                    for 인스턴스2_idx, 인스턴스2 in enumerate(target_txt):
                        if 인스턴스2_idx == 인스턴스1_idx:
                            continue 
                        elif 인스턴스1 != 인스턴스2:
                                텍스트1 = 텍스트.replace(인스턴스1, "<subject>" + 인스턴스1 + "</subject>")
                                텍스트1 = 텍스트1.replace(인스턴스2, "<object>" + 인스턴스2 + "</object>")
                                인스턴스_sub.append(인스턴스1)
                                인스턴스_ob.append(인스턴스2)
                                sentences.append(텍스트1)
                                
                        else:
                            밀기=len(인스턴스1)
                            텍스트1=텍스트.replace(텍스트[target_offset[인스턴스1_idx][0]:target_offset[인스턴스1_idx][1]], "<subject>" + 인스턴스1 + "</subject>")
                            텍스트1=텍스트1.replace(텍스트[target_offset[인스턴스1_idx][0]+밀기:target_offset[인스턴스1_idx][1]+밀기], "<object>" + 인스턴스2 + "</object>")
                            인스턴스_sub.append(인스턴스1)
                            인스턴스_ob.append(인스턴스2)
                            sentences.append(텍스트1)
    return sentences, 인스턴스_sub, 인스턴스_ob


label_list=라벨만들기(label_text_file)
sentences, instance_sub, instance_ob= read_klue_re(text_json_file)
print(len(sentences), len(instance_sub), len(instance_ob))

for i in range(len(sentences)):
    print(instance_sub[i], instance_ob[i], 결과출력(sentences[i], label_list))
