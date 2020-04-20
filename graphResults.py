import plotly.graph_objects as go
import json
import argparse

def mainBar(files):
    resultsToGraph = len(files)
    fig = go.Figure()
    for i in range(resultsToGraph):
        results = open(files[i],"r")
        toDict = json.load(results)
        results.close()
        x = [value[0] for value in toDict["timeExecution"]]
        y = [value[1] + 1 for value in toDict["timeExecution"]]
        if('prob' in toDict.keys()):
            literal = toDict["prob"][0]
            l = "{0:.4f}".format(toDict["prob"][1])
            u = "{0:.4f}".format(toDict["prob"][2])
            name = toDict["experiment"] + ' Pr('+ literal +')=[' + l +',' + u + ']'
        else:
            name='Training'
        fig.add_trace(
            go.Scatter(
                x= x,
                y= y,
                name= name
            ))

    fig.update_layout(
        title="Sampling results",
        xaxis_title="Worlds",
        yaxis_title="Seconds",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        ),
        legend=dict(orientation='h',yanchor='top',xanchor='center',y=1.1,x=0.5)
    )

    fig.show()
    
def stackedBarChar(files):
    resultsToGraph = len(files)
    scenarios = [] #X Axis
    times = [] #Y Axis
    probs = []
    fig = go.Figure()
    for i in range(resultsToGraph):
        results = open(files[i],"r")
        data = json.load(results)
        results.close()
        scenarios.append(data['experiment'])
        times.append(data['timeExecution'])
        literal = data["prob"][0]
        l = "{0:.4f}".format(data["prob"][1])
        u = "{0:.4f}".format(data["prob"][2])
        name = ' Pr('+ literal +')=[' + l +',' + u + ']'
        probs.append(name)
    layout = go.Layout(
            title=go.layout.Title(
                text='Experiment A (80K Worlds - 10 atoms)'
            ),
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text='Scenarios',
                    font=dict(
                        family='Courier New, monospace',
                        size=18,
                        color='#7f7f7f'
                    )
                )
            ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text='Seconds',
                    font=dict(
                        family='Courier New, monospace',
                        size=18,
                        color='#7f7f7f'
                    )
                )
            )
        )
    myText = dict(
        family='Courier New, monospace',
        size=20,
        color='#000000'
    )
    fig = go.Figure(data=[
        go.Bar(name='Random', 
                x = scenarios,  
                text = ['',probs[1]],
                textposition = 'outside',
                textfont = myText, 
                y = [times[0][0], times[1][0]]),
        go.Bar(name='Training and Generate', 
                x = scenarios, 
                y = [times[0][1], 0]),
        go.Bar(name='Guided', 
                x = scenarios,  
                text = [probs[0],''], 
                textposition = 'outside',
                textfont = myText, 
                y = [times[0][2], 0])
    ], layout = layout)

    fig.update_layout(barmode='stack')
    
    fig.show()


parser = argparse.ArgumentParser(description='The script to graph the results')

parser.add_argument('-files',
                    action='store',
                    dest='pathFiles',
                    nargs='+',
                    required=True)

arguments = parser.parse_args()


stackedBarChar(arguments.pathFiles)



#mainBar(arguments.pathFiles)
