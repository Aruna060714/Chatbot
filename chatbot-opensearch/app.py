from flask import Flask, request, jsonify, render_template
from opensearchpy import OpenSearch
import requests
import re
import json
app = Flask(__name__)
with open("context.txt", "r", encoding="utf-8") as f:
    context = f.read()
with open("cleaned_products.json", "r", encoding="utf-8") as f:
    product_data = json.load(f)
client = OpenSearch(
    hosts=[{'host': 'superbotics-search-8731633774.eu-central-1.bonsaisearch.net', 'port': 443}],
    http_auth=('JC8YvqRN74', 'T8JEbusxGFN5VXZ'),
    use_ssl=True,
    verify_certs=True
)
LM_STUDIO_API = "http://127.0.0.1:1234/v1/chat/completions"
keyword_category_map = {
    "men": "men's clothing",
    "women": "women's clothing",
    "jewelery": "jewelery",
    "electronics": "electronics"
}
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    user_input_lower = user_input.lower()
    category_filter = None
    for keyword, category in keyword_category_map.items():
        if keyword in user_input_lower:
            category_filter = category
            break
    known_types = ["monitor", "jacket", "jersey", "ring", "bracelet", "ssd", "shirt", "coat", "backpack"]
    type_match = next((t for t in known_types if t in user_input_lower), None)
    price_filter = None
    price_match = re.search(r"(under|below|less than)\s*\$?(\d+)", user_input_lower)
    if price_match:
        price_filter = int(price_match.group(2))
    query_filters = []
    if category_filter:
        query_filters.append({"term": {"category.keyword": category_filter}})
    if type_match:
        query_filters.append({"term": {"type.keyword": type_match}})
    if price_filter is not None:
        query_filters.append({"range": {"price": {"lte": price_filter}}})
    search_query = {
        "bool": {
            "must": [{
                "multi_match": {
                    "query": user_input,
                    "fields": ["title^3", "description", "type", "category"],
                    "fuzziness": "AUTO"
                }
            }],
            "filter": query_filters
        }
    }
    try:
        response = client.search(index="products", body={"query": search_query})
        hits = response.get("hits", {}).get("hits", [])
    except Exception as e:
        return jsonify({"reply": f"OpenSearch error: {str(e)}"})
    if not hits:
        opensearch_context = "No exact matches. Showing local fallback products:\n"
        for product in product_data:
            if category_filter and product.get("category") != category_filter:
                continue
            if type_match and product.get("type") != type_match:
                continue
            if price_filter is not None and product.get("price", 0) > price_filter:
                continue
            if user_input_lower not in product["title"].lower() and user_input_lower not in product["description"].lower():
                continue
            hits.append({"_source": product})
            if len(hits) == 3:
                break
    else:
        opensearch_context = "Matching products:\n"
    products_summary = []
    for hit in hits[:3]:
        p = hit["_source"]
        products_summary.append({
            "product_name": p["title"],
            "price": f"${p['price']}",
            "description": p["description"],
            "image_url": p["image"]
        })
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": f"User query: {user_input}"},
        {"role": "user", "content": f"Product list:\n{json.dumps(products_summary, indent=2)}\n\nReturn only one best match as JSON."}
    ]
    payload = {
        "model": "tinyllama-1.1b-chat-v1.0",
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 512
    }
    try:
        lm_response = requests.post(LM_STUDIO_API, json=payload)
        reply = lm_response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f"LM Studio error: {str(e)}"
    return jsonify({"reply": reply})
if __name__ == "__main__":
    app.run(debug=True)