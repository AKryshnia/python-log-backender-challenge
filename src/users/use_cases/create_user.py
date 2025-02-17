from typing import Any

import structlog
from django.conf import settings

from core.base_model import Model
from event_log.services import EventService
from core.use_case import UseCase, UseCaseRequest, UseCaseResponse
from users.models import User

logger = structlog.get_logger(__name__)


class UserCreated(Model):
    email: str
    first_name: str
    last_name: str


class CreateUserRequest(UseCaseRequest):
    email: str
    first_name: str = ''
    last_name: str = ''


class CreateUserResponse(UseCaseResponse):
    result: User | None = None
    error: str = ''


class CreateUser(UseCase):
    def _get_context_vars(self, request: UseCaseRequest) -> dict:
        return {
            'email': request.email,
            'first_name': request.first_name,
            'last_name': request.last_name,
        }

    def _execute(self, request: CreateUserRequest) -> CreateUserResponse:
        logger.info('creating a new user')
        user, created = User.objects.get_or_create(
            email=request.email,
            defaults={
                'first_name': request.first_name,
                'last_name': request.last_name,
            },
        )
        if created:
            logger.info('user has been created')
            self._log(user)
            return CreateUserResponse(result=user)
        logger.error('unable to create a new user')
        return CreateUserResponse(error='User with this email already exists')

    def _log(self, user: User) -> None:
        event = UserCreated(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        EventService.log_event(
            event_type="user_created",
            event_context=event.model_dump(),
            environment=settings.ENVIRONMENT,
        )
