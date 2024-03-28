from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo
from question_selector import question_list
from models.response_validation import response_evaluator

app = Flask(__name__)

# Initialize data dictionary to store responses
data = {
    'name': '',
    'responses': [],
    'questions': question_list(),
    'evaluations': [],
}

# Function to extract response and its count from the dictionary
def extract_response_count(dic_list):
    response = dic_list[0][list(dic_list[0].keys())[0]]
    return response

# Convert list of dictionaries into separate pandas DataFrames
def get_graph_df(response):
    response_clarity_df = pd.DataFrame([extract_response_count(item['response_clarity']) for item in response], columns=['response']).groupby('response').size().reset_index(name='response_count')
    technical_accuracy_df = pd.DataFrame([extract_response_count(item['technical_accuracy']) for item in response], columns=['response']).groupby('response').size().reset_index(name='response_count')
    answer_completeness_df = pd.DataFrame([extract_response_count(item['answer_completeness']) for item in response], columns=['response']).groupby('response').size().reset_index(name='response_count')
    return response_clarity_df,technical_accuracy_df,answer_completeness_df

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Store user's name
        data['name'] = request.form['name']
        return redirect(url_for('question', index=0))
    return render_template('index.html')

@app.route('/question/<int:index>', methods=['GET', 'POST'])
def question(index):
    if request.method == 'POST':
        # Store user's response
        response = request.form['response']
        data['responses'].append(response)
        # If there are more questions, redirect to the next question
        if index + 1 < len(data['questions']):
            evaluation=response_evaluator(data['questions'][index],data['responses'][index])
            data['evaluations'].append(evaluation)            
            return redirect(url_for('question', index=index + 1))

        else:
            return redirect(url_for('result'))

    return render_template('question.html', question=data['questions'][index], index=index)

@app.route('/result')
def result():
    # Calculate scores (for demonstration purpose)

    response_clarity, technical_accuracy,answer_completeness=get_graph_df(data['responses'])
    # Create pie chart traces
    trace1 = go.Pie(labels=response_clarity['response'], values=response_clarity['response_count'], name='Response Clarity')
    trace2 = go.Pie(labels=technical_accuracy['response'], values=technical_accuracy['response_count'], name='Technical Accuracy')
    trace3 = go.Pie(labels=answer_completeness['response'], values=answer_completeness['response_count'], name='Answer Completeness')

    # Embed pie charts into HTML using plotly.offline.plot
    div1 = pyo.plot([trace1], output_type='div', include_plotlyjs=False)
    div2 = pyo.plot([trace2], output_type='div', include_plotlyjs=False)
    div3 = pyo.plot([trace3], output_type='div', include_plotlyjs=False)

    return render_template('index.html', div1=div1, div2=div2, div3=div3)

if __name__ == '__main__':
    app.run(debug=True)
