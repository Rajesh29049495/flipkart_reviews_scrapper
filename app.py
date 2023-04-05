from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})   ##it will extract all the products that will be mentioned after the search
            del bigboxes[0:3]                                                         ##as initial 'div' tags w.r.t. the mentioned class does not related to products
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']      ##it will extract the link to open the particular product at index value 0 in the box list that contain all the products
            prodRes = requests.get(productLink)                     ##using python "requests" library sent a GET request to the URL specified, and the source code of the webpage of the particular product is assigned to "prodRes" variable
            prodRes.encoding='utf-8'                                ##a good standard practice so that the data obtained from the response object is correctly decoded and displayed and that any non-ASCII characters in the text are properly handled
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            fw.close()
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text


                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text

                except Exception as e:
                    print('Exception while creating dictionary: {}'.format(e))

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
                fw = open(filename, "a", encoding= "utf-8")                   ##it is important as if going to write the data extracted/scrapped from web without encoding then there will be error as there are some non ascii characters in the data, writing that in csv file will give error, as when we try to write into file, the writing will be doen after using default encode 'cp1252' on windows, which weill not be able to encode all the non ascii characters properly
                fw.write(searchString + ", " + name + ", " + rating + ", " + commentHead + ", " + custComment + " \n")
                fw.close()
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: {}'.format(e))
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)