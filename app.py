from flask import Flask, render_template,request, url_for
import pandas as pd

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
df['id'] = df.index

@app.route("/")
def home():
    person = df.iloc[0]
    return render_template('home.html', person=person)

@app.route('/<state>/<organization>/<name>-<int:person_id>')
def profile(state,organization,name,person_id):
    person = df.iloc[person_id]
    return render_template('profile.html',person=person)

@app.route('/search/', methods=['POST'])
def search():
    search_text = request.form['search_box']
    search_results = df.iloc[int(search_text)]
    return render_template('search_results.html',person=search_results)

if __name__ == "__main__":
    app.run(debug=True)
