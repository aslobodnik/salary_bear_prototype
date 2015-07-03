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
    return render_template('search_results.html', person=search_results)

def search_by_name(search_string):
    results = df[df.full_name.str.contains(search_string.upper())]
    return results

def generate_url(person_id):
    person = df.iloc[person_id]
    url = '/' + slugify(person.state) + '/'
    url += slugify(person.organization) + '/'
    url += slugify(person.full_name) + '-'
    url += str(person_id)
    return url

if __name__ == "__main__":
    app.run(debug=True)
