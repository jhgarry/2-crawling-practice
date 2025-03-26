from selenium import webdriver
from collections import Counter
import re
import pandas as pd
import time


driver = webdriver.Chrome()

url = 'https://www.yanolja.com/reviews/domestic/10054600'
driver.get(url)

time.sleep(3)

scroll_count = 25
for _ in range(scroll_count):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)

    from bs4 import BeautifulSoup

page_source = driver.page_source

soup = BeautifulSoup(page_source, 'html.parser')

reviews_class = soup.select('.css-1kpa3g')

reviews = []

for review in reviews_class:
    cleaned_text = review.get_text(strip=True).replace('\r', '').replace('\n', '')
    reviews.append(cleaned_text)

ratings = []

rating_containers = soup.select('.css-1js0bc8 > .review-item-container')

for container in rating_containers:
    minus = 0
    stars = container.select_one('.css-rz7kwu')
    star = stars.find_all('path')

    for path in star:
        blank = path.get('fill-rule')
        if blank == 'evenodd': minus += 1

    rating = 5 - minus
    ratings.append(rating)

data = list(zip(ratings, reviews))

df_reviews = pd.DataFrame(data, columns=['Rating', 'Review'])

average_rating = sum(ratings) / len(ratings)

korean_stopwords = set(['이', '그', '저', '것', '들', '다', '을', '를', '에', '의', '가', '이', '는', '해', '한', '하', '하고', '에서', '에게', '과', '와', '너무', '잘', '또','좀', '호텔', '아주', '진짜', '정말'])

all_reviews_text = ''.join(reviews)

words = re.findall(r'\w+', all_reviews_text)

filtered_words = [word.strip(''.join(korean_stopwords)) for word in words]
filtered_words = ' '.join(filtered_words).split() # ''을 없앨만한 다른 방법은???

word_counts = Counter(filtered_words)

common_words = word_counts.most_common(15)

summary_df = pd.DataFrame({
    'Average Rating': [average_rating],
    'Common Words': [', '.join([f"{word}({count})" for word, count in common_words])]
})

final_df = pd.concat([df_reviews, summary_df], ignore_index=True)
final_df.to_excel('yanolja_data.xlsx', index=False)

driver.quit()