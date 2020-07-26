from flask import Flask, request, jsonify
import boto3
from urllib.parse import urlparse
from wand.image import Image as wi
import re

app = Flask(__name__)
pdf_pages_threshold_limit = 50


# Sorting the list for the Directories
def sorted_nicely(l):
    """ Sort the given iterable in the way numerical decimal order rather than binary."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


# Downloads the file

def download_file(s3_url, filename):
    s3 = boto3.client('s3', region_name='us-east-1')
    o = urlparse(s3_url)
    bucket = o.netloc
    key = o.path[1:]
    print(bucket, key, filename)
    try:
        s3.download_file(bucket, key, filename)
        return True
    except Exception as e:
        print("Error Occured during download", e)
        return False


# Pdf number of pages
def pdf_number_of_pages(pdf_file_location):
    """
    A Function responsible for the page based threshold returning page numbers in the pdf file!
    @params:
        pdf_file_location : Complete path of the specific PDF : str (required)

    @return
        Boolean : State Reference whether the pdf files should be processed or not: bool

    """
    pdf = wi(filename=pdf_file_location, resolution=5)
    num_pages = len(pdf.sequence)
    return num_pages


def pdf_state(pdf_number_of_pages):
    """
    Function responsible for the state check of the pdf,
    @ params:
        pdf_number_of_pages: length of the pdf file : Integer
    @ return
        State : True or False : Boolean
    """

    return int(pdf_number_of_pages) < pdf_pages_threshold_limit  # Returns the boolean condigion !


@app.route('/get-page-count', methods=['POST'])
def predict():
    # Get the data from the POST request.
    response = {}
    print("Inside the function")
    print(request)
    data = request.get_json(force=True)
    print(data)
    s3_url = data['s3url']
    filename = "doc52.pdf"
    if download_file(s3_url, filename):
        response['no_of_pages'] = pdf_number_of_pages(filename)
        response['pdf_state'] = pdf_state(response['no_of_pages'])

    return jsonify(response)


if __name__ == '__main__':
    try:
        app.run(port=5000, debug=True)
    except:
        print("Server is exited unexpectedly. Please contact server admin.")
