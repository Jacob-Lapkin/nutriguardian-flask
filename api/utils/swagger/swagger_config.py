# swagger_config.py

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Nutriguardian API",
"description": """Welcome to the Nutriguardian API, a result of our collaborative effort at the Google x Square Hackathon. 
                  Our API empowers sellers by providing an advanced mechanism to detect potential allergens in their products, ensuring consumers are better informed and safe. 
                  Dive into our comprehensive set of endpoints designed to enhance transparency and trust between sellers and their customers.""",
        "version": "1.0.0"
    },
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ],
    "schemes": [
        "http", "https"
    ],
    "securityDefinitions": {
    "JWT": {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "description": "JWT used for authentication. Format: Bearer <your_token>"
    }
}

}

