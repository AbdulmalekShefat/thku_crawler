import dryscrape
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import datetime

# ------------------------------------------------------------------------------------------------#

cred = credentials.Certificate('/home/msl/PycharmProjects/thku_crawler/UTAA STU-d3238d5cd8fa.json')
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://utaa-stu.firebaseio.com/'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('notifications')

# ------------------------------------------------------------------------------------------------#

last_ref = ref.child('last')
last = last_ref.get()

# ------------------------------------------------------------------------------------------------#

url = 'http://thk.edu.tr/'
dates = []
titles = []
contents = []
links = []

data = []


# ------------------------------------------------------------------------------------------------#


def beautify(link):
    dryscrape.start_xvfb()
    session = dryscrape.Session()
    session.visit(link)
    response = session.body()
    return BeautifulSoup(response, "html.parser")


def main_crawler():
    soup = beautify(url)
    needed = soup.find("div", {'id': 'DuyuruWidgetContent'})

    for link in needed.findAll('a', {'class': 'widgetContentDetails'}):
        href = url + link.get('href')
        title = link.text.lstrip()
        if title == last:
            break
        titles.append(title)
        links.append(href)
        inner_crawler(href)
    for link in needed.findAll('div', {'class': 'widgetDate'}):
        date = str(link.string).replace(".", "/")
        dates.append(date)


def inner_crawler(link):
    soup = beautify(link)
    for content in soup.findAll('p', {'id': 'realContent'}):
        for tag in content.find_all():
            if 'style' in tag.attrs:
                del tag.attrs['style']
        contents.append(content.prettify())


def array_to_dict():
    for i in range(0, len(titles)):
        datum = {
            'title': titles[i],
            'date': datetime.datetime.strptime(dates[i], '%d/%m/%Y').strftime('%Y/%m/%d'),
            'body': contents[i],
            'link': links[i],
            'topic': 'General'
        }
        data.append(datum)


main_crawler()
array_to_dict()


def update_notifications():
    if len(titles) == 0:
        return
    last_not = {
        'last': titles[0]
    }
    ref.update(last_not)
    for datum in data:
        ref.child('items').push(datum)
    print(titles)


update_notifications()
print("updated")
