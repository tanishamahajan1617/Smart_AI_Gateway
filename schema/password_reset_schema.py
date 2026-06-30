from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    """
    Request to initiate password reset.
    """

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """
    Request to reset password using a valid reset token.
    """

    token: str = Field(
        ...,
        min_length=32,
        description="Password reset token received via email"
    )

    new_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="New account password"
    )


class ForgotPasswordResponse(BaseModel):
    """
    Generic response for forgot password endpoint.
    """

    message: str


class ResetPasswordResponse(BaseModel):
    """
    Response after successful password reset.
    """

    message: str