import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        response = requests.get(url, headers={'Content-Type':'application/json'}, params = kwargs)
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print(json_payload)
    print("POST to {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    print(json_data)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url):
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result["body"]
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"]
            )
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_by_id_from_cf(url, dealer_id):
    json_result = get_request(url, id=dealer_id)
    if json_result:
        dealer_doc = json_result["body"][0]
        dealer_obj = CarDealer(
            address=dealer_doc["address"],
            city=dealer_doc["city"],
            full_name=dealer_doc["full_name"],
            id=dealer_doc["id"],
            lat=dealer_doc["lat"],
            long=dealer_doc["long"],
            short_name=dealer_doc["short_name"],
            st=dealer_doc["st"],
            zip=dealer_doc["zip"]
        )
    return dealer_obj

def get_dealers_by_st_from_cf(url, state):
    results = []
    json_result = get_request(url, st=state)
    if json_result:
        dealers = json_result["body"]
        for dealer_doc in dealers:
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"]
            )
            results.append(dealer_obj)
    return results

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    json_result = get_request(url, dealership=dealer_id)
    if json_result:
        reviews = json_result["body"]["data"]["docs"]
        print(reviews)
        for review_doc in reviews:
            if(review_doc["purchase"]):
                review_obj = DealerReview(
                    name=review_doc["name"],
                    dealership=review_doc["dealership"],
                    review=review_doc["review"],
                    # sentiment=analyze_review_sentiments(review_doc["review"]),
                    sentiment="neutral",
                    purchase=review_doc["purchase"],
                    purchase_date=review_doc["purchase_date"],
                    car_make=review_doc["car_make"],
                    car_model=review_doc["car_model"],
                    car_year=review_doc["car_year"]
                )
                # review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            else:
                review_obj = DealerReview(
                    name=review_doc["name"],
                    dealership=review_doc["dealership"],
                    review=review_doc["review"],
                    # sentiment=analyze_review_sentiments(review_doc["review"]),
                    sentiment="neutral",
                    purchase=review_doc["purchase"]
                )
                # review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def analyze_review_sentiments(text):
    print(text)
    authenticator = IAMAuthenticator(apikey="yyPbC2hV3ecOQYsxY1jKvGEOtu9r3UVOH0-NplGr2ae-")
    version = "2022-04-07"
    nlu = NaturalLanguageUnderstandingV1(version=version, authenticator=authenticator)
    print("NLU instance created")
    nlu.set_service_url(url="https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/de6e5cce-07a5-4632-a401-1032a72d651b")
    nlu.set_disable_ssl_verification(True)
    # print("Disabled")
    try:
        response = nlu.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions(targets=[text]))
        ).get_result()
        label =  json.dumps(response, indent=2)
        print(label)
        label = response['sentiment']['document']['label']
    except:
        label = "neutral"
    print(label)
    return label

