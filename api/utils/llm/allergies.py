from langchain.prompts import PromptTemplate
from langchain.llms import VertexAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
import google.auth
from pydantic import BaseModel, Field
from typing import List
import logging

# logging.basicConfig(level=logging.DEBUG)


credentials, projectid = google.auth.default()


class AllergyAssessment(BaseModel):
    """
    A model assessing potential allergens in food products based on a customer's listed allergies.

    Attributes:
    confirmed_allergens (List[str]): Ingredients that are explicitly mentioned in the customer's list of allergies.
    possible_allergens (List[str]): Ingredients not explicitly listed as allergies for the customer but might cause allergic reactions based on known information.
    risk_rating (int): A rating from 0 to 10 indicating the overall risk for the customer when consuming the product. A higher number indicates a higher risk.
    recommendation (str): A general recommendation for the customer based on the assessment.
    """

    confirmed_allergens: List[str] = Field(
        description="Ingredients that are directly recognized from the customer's list of allergies."
    )
    possible_allergens: List[str] = Field(
        description="Ingredients that, while not directly listed, may pose an allergy risk based on contextual knowledge."
    )
    risk_rating: int = Field(
        description="A rating between 0 (minimal risk) and 10 (highest risk) indicating the potential risk for the customer upon consuming the product.",
        ge=0, le=10  # Ensures the risk rating is between 0 and 10
    )
    recommendation: str = Field(
        description="A general suggestion or advice for the customer considering the identified allergens and the risk assessment."
    )
parser = PydanticOutputParser(pydantic_object=AllergyAssessment)


_prompt = """
        You are a sophisticated system designed to identify potential allergens in a list of food products, based on a customer's documented allergies.

        Please ensure your responses adhere to the following format: {format_instructions}

        When identifying allergens, please consider the subsequent guidelines:
        1. Direct Matches: The allergen may be explicitly mentioned in the customer's allergy list.
        2. Implicit Allergens: Even if not directly mentioned, deduce potential allergens using informed judgement, considering common derivatives and related allergens.
        3. Safety First: When in doubt, lean on the side of caution and flag the potential allergen for review.

        Your primary goal is to ensure the safety of the customer by accurately identifying any and all potential allergens.

        Customer allergy list: {customer_allergies}
        Food items and potentially documented ingredients: {food_items}
        """

class Allergies:
    """
    A class to identify and manage potential conflicting allergies from a list of food products.
    
    Attributes:
    - model (str): Specifies the model to be used for allergy detection. Default is 'vertex'.
    - _prompt (str): The prompt template to be used for the underlying language model.
    
    Methods:
    - set_prompt(): Updates the prompt template.
    - find_allergies(): Identifies potential allergies based on given food items.
    """
    
    def __init__(self, model="vertex"):
        """
        Initializes the Allergies class with a specific model.
        
        Parameters:
        - model (str): Specifies the model to be used for allergy detection. Default is 'vertex'.
        """
        self.model = model
        self._prompt = _prompt

    def set_prompt(self, prompt):
        """
        Updates the prompt template used for allergy detection.
        
        Parameters:
        - prompt (str): The new prompt template to be set.
        
        Returns:
        - str: The updated prompt template.
        """
        self._prompt = prompt
        return prompt
        
    def find_allergies(self, allergies, food_items):
        """
        Identifies potential conflicting allergies based on the provided list of allergies and food items.
        
        Parameters:
        - allergies (list): List of known allergies of the customer.
        - food_items (list): List of food items to check against the known allergies.
        
        Returns:
        - dict: Parsed output containing potential allergens and other relevant information.
        """
        # get prompt template
        prompt = PromptTemplate(template=self._prompt, input_variables=["customer_allergies", "food_items"],
                                partial_variables={
                                    "format_instructions": parser.get_format_instructions()})
        
        _input = prompt.format_prompt(
            customer_allergies=allergies, food_items=food_items)

        # set llm 
        llm_model = VertexAI(project=projectid, model_name='text-bison', temperature=0.2, verbose=False)
        
        output = llm_model(_input.to_string())

        parsed_output = parser.parse(output)
        return parsed_output



        
