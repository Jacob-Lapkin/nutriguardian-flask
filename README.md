# NutriGuardian: Flask API

NutriGuardian is an intuitive Flask API designed for health-conscious consumers, streamlining their shopping experience by identifying potential allergens in the products they wish to purchase. It integrates seamlessly with Square's product database, leveraging advanced language models to inform users of any dietary concerns.

## 🌟 Features

- **Personalized Allergen Warnings**: At the heart of NutriGuardian is its ability to provide tailored allergen alerts based on a user's profile.
- **Real-time Inventory Management**: Sellers are equipped with tools to seamlessly update and monitor product inventory.
- **User Profile Management**: A user-centric design that allows easy management of allergen profiles for tailored advice.
- **Intuitive Product Catalog Browsing**: Integrated with Square's database, allowing users to comfortably browse and receive real-time allergen insights.

## 🔗 API Endpoints

### **1. Customer Attributes**

- **Add Allergies**:
  - Method: `POST`
  - Description: Appends allergies to a user's profile.
  
- **Retrieve Allergies**:
  - Method: `GET`
  - Description: Fetches allergies associated with a user.
  
- **Remove Allergies**:
  - Method: `DELETE`
  - Description: Removes specific allergies from a user's profile.

### **2. Inventory Management**

- **Update Inventory**:
  - Method: `PUT`
  - Description: Allows sellers to update product inventory counts.
  
- **Fetch Inventory**:
  - Method: `GET`
  - Description: Retrieves inventory count for a specific product.

### **3. Catalog and Cart Management**

- **Browse Catalog**:
  - Method: `GET`
  - Description: Users can view products and their allergen information.
  
- **Cart Operations**:
  - Method: `POST`, `GET`, `DELETE`
  - Description: Facilitates adding, viewing, and removing products from a user's cart with real-time allergen alerts.

## 🛠 Dependencies

- **Flask**: Our main web framework.
    
- **Google Auth**: For authentication and credentials.
  
- **PyMongo**: A bridge between MongoDB and Python.

- **And Many More**...

## 🚀 Getting Started

### **Installation**

1. Clone the project:

    ```bash
    git clone https://github.com/Jacob-Lapkin/nutriguardian-flask.git
    ```

Navigate to the directory:

    ```bash
    cd nutriguardian-flask
    ```

Install required packages:

    ```bash 
    pip install -r requirements.txt
    ```

Setup & Running

- Set your environment variables (e.g., database string, JWT secret).

- Launch the application:

    ```bash
    python3 app.py
    ```

🙌 Contributing

We appreciate community contributions! Fork this repository, make your enhancements, and initiate a pull request.

🎉 Acknowledgments

Special shoutout to everyone involved in this Google + Square Hackathon event. Your dedication and hard work made these projects a reality.

## 📚 OpenAPI Specifications

For detailed API documentation, including endpoints, request/response formats, and more, please refer to our OpenAPI (Swagger) documentation the endpoint /apidocs.