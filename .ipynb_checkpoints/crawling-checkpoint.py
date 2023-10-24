from datetime import datetime, timedelta
import time
import random
from tqdm import tqdm
from typing import Final
from bs4 import BeautifulSoup as bs
from selenium import webdriver as wd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  

options = wd.ChromeOptions()
# options.add_argument("headless")
options.add_argument('window-size=1920x1080')
options.add_argument('disable-gup')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36')
options.add_argument('lang=ko_KR')

class url_crawling(object):
    def __init__(self):
        self.keyword = '고혈압'
        self.start = None
        self.end = None
        
        self.href = []
        self.check_expert = []
        
        self.url = f'https://kin.naver.com/search/list.nhn?sort=none&query={self.keyword}&period={self.end}%7C{self.start}&section=qna&page=1'
        self.driver = wd.Chrome()
    # 현재 url 출력하는 함수
    def __str__(self, idx):
        return f'https://kin.naver.com/search/list.nhn?sort=none&query={self.keyword}&period={self.end}%7C{self.start}&section=qna&page={idx}'
    
    # 날짜를 문자열로 변환하는 함수
    def datetimeToStr(self, dtime : datetime):
        time_month = format(dtime.month, '02')
        time_day = format(dtime.day, '02')
        
        # 날짜 형식 지정 : '20XX.XX.XX'
        return f'{dtime.year}.{time_month}.{time_day}.'
    
    # 수집할 qna의 기간을 30일 단위로 설정하여 함수 호출하는 함수
    def scraping(self, period_start : datetime):
        self.start = self.datetimeToStr(period_start)
        self.end = self.datetimeToStr(period_start - timedelta(days=30)) # 종료 일자는 시작 일자로부터 30일 전으로 설정

        print(self.__str__(1))
        for page_idx in range(1,21):
            self.url = self.__str__(page_idx)

            self.driver.get(self.url)
            time.sleep(random.uniform(2,4))

            html = self.driver.page_source
            soup = bs(html, 'html.parser')
            div_chuncks = soup.select('div.section > ul > li')

            self.get_href(div_chuncks)
        return
    
    # 페이지 내의 각 URL 정보 수집하는 함수
    def get_href(self, div_chuncks : str):
        for idx in range(len(div_chuncks)):
            href = div_chuncks[idx].select('dl > dt > a')[0]['href']
            check_expert = None
            try:
                check_expert = div_chuncks[idx].select('dl > dt > img')[0]['alt']
            except:
                pass

            if check_expert:
                self.href.append(href)
                self.check_expert.append(check_expert)
            
        return

    
    
# URL 
class qna_crawling(object):
    def __init__(self):
        self.driver = wd.Chrome()
        self.url = ''
        
        self.q_title = []     # 질문 제목
        self.q_content = []   # 질문 내용
        self.q_tag = []       # 질문 태그
        self.q_date = []      # 질문 날짜
        
        self.a_name = []      # 답변 작성자 이름
        self.a_cat = []       # 답변 작성자 분야
        self.a_content = []   # 답변 내용
        
    # 출력 함수
    def __str__(self):
        return self.q_title
    
    # URL 내의 QnA 콘텐츠 정보 수집
    def scraping(self, url : str):
        self.url = url
        self.driver.get(self.url)
        time.sleep(random.uniform(2,4))
        
        html = self.driver.page_source
        soup = bs(html, 'html.parser')
        
        self.question_info(soup)
        self.answer_info(soup)
        # self.__str__()
    
    def question_info(self, soup):
        # 질문 제목
        try:
            title = soup.select('div.question-content > div > div:nth-child(1)')[0].select('.title')[0].text.strip()
        except:
            title = ''
        
        # 질문 내용
        try:
            content = soup.select('div.question-content > div > div:nth-child(1)')[0].select('.c-heading__content')[0].text.strip()
        except:
            content = ''
        
        # 질문 태그
        try:
            tag = soup.select('div.question-content > div > div:nth-child(2)')[0].text.strip().replace('태그 디렉터리Ξ ', '')
        except:
            tag = ''
        
        # 질문 날짜
        try:
            date = soup.select('div.question-content > div > div:nth-child(3)')[0].select('.c-userinfo__info')[0].text.replace('작성일', '')
        except:
            date = ''
            
        self.q_title.append(title)
        self.q_content.append(content)
        self.q_tag.append(tag)
        self.q_date.append(date)
            
    def answer_info(self, soup):
        
        answer_div = soup.select('.answer-content__list._answerList > div')
        
        # 답변 전체
        nm_tmp, cat_tmp, content_tmp = [], [], []
        for i in range(len(answer_div)):
            try:
                ans_nm = answer_div[i].select('.profile_card')[0].select('.name')[0].text.strip()
            except:
                ans_nm = answer_div[i].select('.profile_card')[0].select('.etc_text')[0].text.strip()

            try:
                ans_cat = answer_div[i].select('.career_list')[0].text.strip()
            except:
                ans_cat = ''
            try:
                try:
                    ans_content = answer_div[i].select('.se-component-content')[0].text.strip()
                except:
                    ans_content = answer_div[i].select('._endContentsText.c-heading-answer__content-user')[0].text.strip()
            except:
                ans_content = ''
            nm_tmp.append(ans_nm)
            cat_tmp.append(ans_cat)
            content_tmp.append(ans_content)
            
        self.a_name.append(nm_tmp)
        self.a_cat.append(cat_tmp)
        self.a_content.append(content_tmp)