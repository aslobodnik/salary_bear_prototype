from flask import Flask, render_template,request, url_for
import pandas as pd
from slugify import slugify

app = Flask(__name__)

df = pd.DataFrame.from_csv('data.csv')
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
    person = df.iloc[person_id]
    url = generate_url(person_id)
    return render_template('profile.html',person=person, url=url)

@app.route('/search/', methods=['POST'])
def search():
    search_text = request.form['search_box']
    search_results = search_by_name(search_text)
    people = create_people(search_results)
    return render_template('search_results.html', people=people,
            search_text=search_text)

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

if __name__ == "__main__":
    app.run(debug=True)
