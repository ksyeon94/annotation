# -*- coding: utf-8 -*-
"""klue-re-workspace.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1W6UnM8jTokPtXA693BPTJnObezRXWleR
"""

import torch
import torch.nn as nn
import sklearn.metrics

from tqdm import tqdm
from datasets import load_dataset
from datasets.arrow_dataset import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW
from torch.utils.data import DataLoader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

dataset = load_dataset('rlatmddus159/anmu')
result_folder='/home/rlatmddus159/re/결과물'

label_count = {}
label_list=["0"]
label_dict={}
for data in dataset['train']:
    relations = data['relations']
    for relation in relations:
      label= relation['type']
      if label not in label_count:
          label_count[label] = 1
      else:
          label_count[label] += 1
for data in dataset['test']:
    relations = data['relations']
    for relation in relations:
      label= relation['type']
      if label not in label_count:
          label_count[label] = 1
      else:
          label_count[label] += 1

label_count = dict(sorted(label_count.items(), key=lambda x: x[0]))
for i in label_count.items():
  label_list.append(i[0])

label_dict={label:i for i, label in enumerate(label_list)}
label_dict2={i:label for i, label in enumerate(label_list)}
len_label=len(label_dict.keys())

def 라벨저장(라벨리스트, 폴더이름):
    with open(폴더이름+'/label.txt', 'w', encoding='utf-8') as f:
        for 라벨 in 라벨리스트:
            f.write(라벨 + '\n')
            
라벨저장(label_list, result_folder)



dataset['train'][0]

import json

type(dataset['train'][0])

#text가 주어졌을때 ner를 자동으로 추출하는 모델 만들고
#entity를 가지고 s와 o의 모든 경우의 수를 만들 필요가 있음
#no_relation을 어떻게 구현하느냐? entity가 2개 이상 나온 문장에 대해서 train_set에 no_relation을 추가해야함
#entity와 relation을 모두 맞춘경우 맞은걸로 처리

#문장이 주어졌을때 subject와 object를 예측하는 코드도 만들어야함
def read_klue_re(dataset): #텍스트와 엔티티로 subject, object을 만들고 관계를 각각 만들어내는 코드 / 리스트로 반환
  sentences = []
  labels  = []
  num_rows=dataset.num_rows
  for i in range(num_rows):
    data=dataset[i]
    텍스트 = data["text"] #"해군 함정중에 충무공이순신급이 있는데 길이가 130m이다"
    관계 = data["relations"]
    엔티티 = data["entities"]
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
                        sentences.append(텍스트1)
                        labels.append(label_dict['0']) #label_dict={"0":0, "탑재":1, ~~~}
                else:
                    밀기=len(인스턴스1)
                    텍스트1=텍스트.replace(텍스트[target_offset[인스턴스1_idx][0]:target_offset[인스턴스1_idx][1]], "<subject>" + 인스턴스1 + "</subject>")
                    텍스트1=텍스트1.replace(텍스트[target_offset[인스턴스1_idx][0]+밀기:target_offset[인스턴스1_idx][1]+밀기], "<object>" + 인스턴스2 + "</object>")
                    sentences.append(텍스트1)
                    labels.append(label_dict['0']) #labels={"0"}
        
                           
    for 관계_item in 관계:
        entity_ids = [관계_item["from_id"], 관계_item["to_id"]]
        target_txt = []

        for entity_id in entity_ids:
            for entity_item in 엔티티:
                if entity_item["id"] == entity_id:
                    start_offset = entity_item["start_offset"]
                    end_offset = entity_item["end_offset"]
                    target_txt.append(텍스트[start_offset:end_offset])

        텍스트2 = 텍스트.replace(target_txt[0], "<subject>" + target_txt[0] + "</subject>")
        텍스트2 = 텍스트2.replace(target_txt[1], "<object>" + target_txt[1] + "</object>")
        
        for i_sentence, 전처리 in enumerate(sentences):
            if 텍스트2==전처리:
                labels[i_sentence]=label_dict[관계_item["type"]]
            
  return sentences, labels


train_sentences, train_labels=read_klue_re(dataset["train"])
val_sentences, val_labels=read_klue_re(dataset["test"])

model_name = 'klue/bert-base'

tokenizer = AutoTokenizer.from_pretrained(model_name)

entity_special_tokens = {'additional_special_tokens': ['<obj>', '</obj>', '<subj>', '</subj>']}
num_additional_special_tokens = tokenizer.add_special_tokens(entity_special_tokens)

# For Dataloader
batch_size = 8

# For model
num_labels = 20

# For train
learning_rate = 1e-5
weight_decay = 0.0
epochs = 3

class KlueReDataset(torch.utils.data.Dataset):
    def __init__(self, tokenizer, sentences, labels, max_length=128):
        self.encodings = tokenizer(sentences,
                                   max_length=max_length,
                                   padding='max_length',
                                   truncation=True)
        self.labels = labels

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item['labels'] = self.labels[idx]

        return item

    def __len__(self):
        return len(self.labels)

train_dataset = KlueReDataset(tokenizer, train_sentences, train_labels)
val_dataset = KlueReDataset(tokenizer, val_sentences, val_labels)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=True)

model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels).to(device)

model

class AverageMeter():
    def __init__(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

def train_epoch(data_loader, model, criterion, optimizer, train=True):
    loss_save = AverageMeter()
    acc_save = AverageMeter()

    loop = tqdm(enumerate(data_loader), total=len(data_loader))
    for _, batch in loop:
        inputs = {
            'input_ids': batch['input_ids'].to(device),
            'token_type_ids': batch['token_type_ids'].to(device),
            'attention_mask': batch['attention_mask'].to(device),
        }

        labels = torch.Tensor(batch['labels']).to(device)

        optimizer.zero_grad()
        outputs = model(**inputs)
        logits = outputs['logits']

        loss = criterion(logits, labels)

        if train:
            loss.backward()
            optimizer.step()

        preds = torch.argmax(logits, dim=1)
        acc = ((preds == labels).sum().item() / labels.shape[0])

        loss_save.update(loss, labels.shape[0])
        acc_save.update(acc, labels.shape[0])

    results = {
        'loss': loss_save.avg,
        'acc': acc_save.avg,
    }

    return results


# loss function, optimizer 설정
criterion = nn.CrossEntropyLoss()
optimizer = AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)

for epoch in range(epochs):
    print(f'< Epoch {epoch+1} / {epochs} >')

    # Train
    model.train()

    train_results = train_epoch(train_loader, model, criterion, optimizer)
    train_loss, train_acc = train_results['loss'], train_results['acc']

    # Validation
    with torch.no_grad():
        model.eval()

        val_results = train_epoch(val_loader, model, criterion, optimizer, False)
        val_loss, val_acc = val_results['loss'], val_results['acc']


    print(f'train_loss: {train_loss:.4f}, train_acc: {train_acc:.4f}, val_loss: {val_loss:.4f}, val_acc: {val_acc:.4f}')
    print('=' * 100)

tokenizer.save_pretrained(result_folder)#'/home/rlatmddus159/re/결과물'
model.save_pretrained(result_folder)

def 변환과정(val_sentence):
  val_encoding = tokenizer(val_sentence,
                         max_length=128,
                         padding='max_length',
                         truncation=True,
                         return_tensors='pt')
  val_input = {
    'input_ids': val_encoding['input_ids'].to(device),
    'token_type_ids': val_encoding['token_type_ids'].to(device),
    'attention_mask': val_encoding['attention_mask'].to(device),
    }

  model.eval()
  output = model(**val_input)
  label = torch.argmax(output['logits'], dim=1)
  return label_dict2[label.item()]

import re
for val_sentence in val_sentences:
  주어 = re.search('\<subject>.*\</subject>', val_sentence)
  목적어 = re.search('\<object>.*\</object>', val_sentence)
  if 주어:
    주어 = 주어.group()
  else:
      주어 = ''

  if 목적어:
      목적어 = 목적어.group()
  else:
      목적어 = ''
  #print(주어, 목적어, "▶", 변환과정(val_sentence))



def calc_f1_score(preds, labels):
    """
    label이 0(관계 없음)이 아닌 예측 값에 대해서만 f1 score 계산.
    """
    preds_relation = []
    labels_relation = []

    for pred, label in zip(preds, labels):
        if label != 0:
            preds_relation.append(pred)
            labels_relation.append(label)

    f1_score = sklearn.metrics.f1_score(labels_relation, preds_relation, average='micro', zero_division=1)

    return f1_score * 100

with torch.no_grad():
    model.eval()

    label_all = []
    pred_all = []
    for batch in tqdm(val_loader):
        inputs = {
            'input_ids': batch['input_ids'].to(device),
            'token_type_ids': batch['token_type_ids'].to(device),
            'attention_mask': batch['attention_mask'].to(device),
        }
        labels = batch['labels'].to(device)

        outputs = model(**inputs)
        logits = outputs['logits']

        preds = torch.argmax(logits, dim=1)

        label_all.extend(labels.detach().cpu().numpy().tolist())
        pred_all.extend(preds.detach().cpu().numpy().tolist())

    f1_score = calc_f1_score(label_all, pred_all)

print(f1_score)
