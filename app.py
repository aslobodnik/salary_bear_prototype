from flask import Flask, render_template,request, url_for
import pandas as pd
from slugify import slugify
from pagination import *
from re import sub
from decimal import Decimal

app = Flask(__name__)

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    args['q'] = request.args.get('q')
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page #pagination macro
#Global Defaults
PER_PAGE = 10

df = pd.DataFrame.from_csv('full_data_1.csv',index_col=False)
df.columns = ['organization'
                ,'department'
                ,'last_name'
                ,'first_name'
                ,'middle_name'
                ,'title'
                ,'salary'
                ,'state']

df['full_name'] = df['first_name'] + ' ' + df['middle_name'] + ' '\
                    + df['last_name']

df['id'] = df.index

#data cleaning
#df = df[~df['title'].isnull()]
df['salary'] = df['salary'].fillna('$0.00')
#df['salary'] = df['salary'].apply(lambda x: Decimal(sub(r'[^\d.]','',x)))


@app.template_filter('commas')
def commas(s):
    return '{:,.0f}'.format(s)

def create_person(df_row):
    person = {}
    person['organization'] = df_row.organization
    person['department'] = df_row.department
    person['last_name'] = df_row.last_name
    person['first_name'] = df_row.first_name
    person['middle_name'] = df_row.middle_name
    person['title'] = df_row.title
    person['salary'] = df_row.salary
    person['state'] = df_row.state
    person['full_name'] = df_row['first_name'] + ' ' + df_row['middle_name'] +\
            ' ' + df_row['last_name']
    person['person_id'] = df_row['id']
    person['url'] = generate_url(df_row['id'])
    return person

def create_people(df):
    people = []
    for index, row in df.iterrows():
        people.append(create_person(row))
    return people

@app.route("/")
def home():
    person = df.iloc[0]
    return render_template('home.html', person=person)

@app.route('/<state>/<organization>/<name>-<int:person_id>')
def profile(state,organization,name,person_id):
    person = create_person(df.iloc[person_id])
    high,low = find_others(person_id)
    return render_template('profile.html',person=person,high=high,low=low)


@app.route('/search', defaults={'page': 1})
@app.route('/search/page/<int:page>')
def search(page):
    search_text = request.args.get('q')
    search_results = search_by_name(search_text)
    people = create_people(search_results)
    if people:
        result_pages = [people[x:x+PER_PAGE] for x in range(0,len(people)
            ,PER_PAGE)]
        result_page = result_pages[page - 1]
    else:
        result_page = []
    pagination = Pagination(page, PER_PAGE, len(people))
    return render_template('search_results.html', people=result_page,
            pagination=pagination,results=len(people), search_text=search_text)


def search_by_name(search_string):
    search_string = search_string.upper().split()
    results = df.last_name != None
    for word in search_string:
        results &= df.full_name.str.contains(word)
    return df[results]

def generate_url(person_id):
    person = df.iloc[person_id]
    url = '/' + slugify(person.state) + '/'
    url += slugify(person.organization) + '/'
    url += slugify(person.full_name) + '-'
    url += str(person_id)
    return url

def find_others(person_id):
    person = df.iloc[person_id]
    coworkers = df[df.department == person.department]
    coworkers.sort('salary',inplace=True)
    highest_salary = coworkers.iloc[-1] 
    lowest_salary = coworkers.iloc[0] 
    
    if highest_salary['salary'] == person['salary']:
        high_coworker = create_person(highest_salary)
        low_coworker = create_person(lowest_salary)
    elif lowest_salary['salary']== person['salary']:
        high_coworker = create_person(highest_salary)
        low_coworker = create_person(lowest_salary)
    else:
        high_coworker = coworkers[coworkers['salary'] > person['salary']].sort('salary').iloc[0] 
        low_coworker = coworkers[coworkers['salary'] < person['salary']].sort('salary').iloc[-1] 
        high_coworker= create_person(high_coworker)
        low_coworker = create_person(low_coworker)
    
    return high_coworker,low_coworker


if __name__ == "__main__":
    app.run(debug=True,port=5001)
