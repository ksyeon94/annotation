import requests
from bs4 import BeautifulSoup
import json
import urllib3



base_url = ['https://www.gukbangnews.com/news/articleList.html?sc_section_code=S1N5&view_type=sm']
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
base_url_head = 'https://www.gukbangnews.com/news/articleView.html?idxno='
#base_url_tail = '/ATCE_CTGR_0010040000/view.do'
urllib3.disable_warnings()
끝난숫자='/home/rlatmddus159/크롤링/끝난숫자.txt'
def read_file(input_path):
  with open(input_path, "r", encoding='utf-8') as f:
      labels = []
      for line in f:
        if line=='\n' or line.startswith('<'):
          continue
        else:
          split_line = line.strip()
          labels.append(split_line)
      return labels
  
  
with open('/home/rlatmddus159/annotation/함급.json', mode='r') as f:
    word_list=[]
    함급_dict=json.load(f)
    for 클래스 in 함급_dict.keys():
        for 인스턴스 in 함급_dict[클래스]:
            word_list.append(인스턴스)
            
print(word_list)

file_name = '/home/rlatmddus159/크롤링/gukbang.txt'

g = open(끝난숫자, 'r', encoding='UTF-8')
number = int(g.readline().strip())  # 파일에서 첫 번째 줄의 숫자를 읽어와서 숫자로 변환하여 저장
g.close()

g = open(끝난숫자, 'r', encoding='UTF-8')
number = int(g.readline().strip())  # 파일에서 첫 번째 줄의 숫자를 읽어와서 숫자로 변환하여 저장
g.close()

f = open(file_name, 'a', encoding='UTF-8')
예외 = []
for i in range(number+1, number+1001):
    g = open(끝난숫자, 'w', encoding='UTF-8')
    news = []
    url = base_url_head + str(i)
    response = requests.get(url, headers=header, timeout=10000, verify=False)

    html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    title_temp = soup.select_one('#articleViewCon > article > header > h3')
    body_temp = soup.select('#article-view-content-div > p')

    combined_text = ""
    try:
      for tag in title_temp:
          head = tag.text
          combined_text = head

      for tag in body_temp:
          body = tag.text
          combined_text += "\n" + body

      flag = False

      for word in word_list:
          if word in combined_text:
              print(combined_text)
              f.write(combined_text + '\n')
              flag = True
              break
          else:
              continue

      if flag == True:
          print(str(i)+"성공")
      else :
        print(str(i)+"없음")


    except:
      print(str(i) + "예외처리")
      예외.append(i)
    g.write(str(i))
    g.close()


f.close()
'''
d = open('/content/drive/MyDrive/국방/예외.txt', 'a', encoding='UTF-8')

for i in 예외:
  d.write(str(i) + '\n')
d.close()
'''
