from flask import Flask, render_template, request, redirect, url_for
import plotly.graph_objs as go

app = Flask(__name__)

# Initialize data dictionary to store responses
data = {
    'name': '',
    'responses': [],
    'questions': ['What is your favorite color?', 'What is your favorite food?', 'What is your favorite animal?'],
}

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
            return redirect(url_for('question', index=index + 1))
        else:
            return redirect(url_for('result'))

    return render_template('question.html', question=data['questions'][index], index=index)

@app.route('/result')
def result():
    # Calculate scores (for demonstration purpose)
    scores = [len(response) for response in data['responses']]

    # Create pie chart
    labels = [f'Question {i+1}' for i in range(len(data['questions']))]
    values = scores
    pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values)])

    return render_template('result.html', name=data['name'], pie_chart=pie_chart)

if __name__ == '__main__':
    app.run(debug=True)
