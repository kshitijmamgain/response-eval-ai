import guardrails as gd
from guardrails.validators import ValidRange, ValidChoices
from pydantic import BaseModel, Field
from rich import print
from typing import List

class ResponseClarity(BaseModel):
    response_clarity: str = Field(..., description="Is user answer clear and coherent",
        validators=[ValidChoices(["Yes", "Somewhat", "No"], on_fail="reask")]
    )
    # clarity_explanation: str = Field(..., description="what is the reason that question got rated")

class TechnicalAccuracy(BaseModel):
    technical_accuracy: str = Field(..., description="Is user answer technically accurate",
        validators=[ValidChoices(["Yes", "Somewhat", "No"], on_fail="reask")]
    )

class AnswerCompleteness(BaseModel):
    answer_completeness: str = Field(..., description="Are all parts of questions answered by user",
        validators=[ValidChoices(["Yes", "Somewhat", "No"], on_fail="reask")]
    )

class ResponseValidation(BaseModel):
    response_clarity: List[ResponseClarity] = Field(..., description="Clarity in user's answer")
    technical_accuracy: List[TechnicalAccuracy] = Field(..., description="Technical accuracy")
    answer_completeness: List[AnswerCompleteness] = Field(..., description="Coherence")


PROMPT = """For the below question there is an expected answer, however user has answered based on their understanding
please extract a dictionary that contains the assessment of the answer.

Question: ${question}
Expected Answer: ${expected_answer}
User Answer: ${answer}

assess the user's answer based on the expected answer im a dictionary format based on assessment criteria 

${gr.complete_json_suffix_v2}
"""

guard = gd.Guard.from_pydantic(ResponseValidation, prompt=PROMPT, num_reasks=3)
