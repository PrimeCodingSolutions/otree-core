import logging



from django.core.management.base import BaseCommand

from otree.session import create_session
from otree.room import get_room_dict


logger = logging.getLogger('otree')


class Command(BaseCommand):
    help = "oTree: Create a session."

    def add_arguments(self, parser):
        parser.add_argument(
            'session_config_name', help="Vælg type spil"
        )
        parser.add_argument(
            'num_participants',
            type=int,
            help="Antal spillere for spillet",
        )
        parser.add_argument(
            "--room",
            action="store",
            dest="room_name",
            default=None,
            help="Name of room to create the session in",
        )

    def handle(self, session_config_name, num_participants, room_name, **kwargs):

        session = create_session(
            session_config_name=session_config_name,
            num_participants=num_participants,
        )

        if room_name:
            room = get_room_dict()[room_name]
            room.set_session(session)
            logger.info(
                "Created session with code {} in room '{}'\n".format(
                    session.code, room_name
                )
            )
        else:
            logger.info("Created session with code {}\n".format(session.code))
