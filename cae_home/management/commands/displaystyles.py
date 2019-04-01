"""
Info command that shows output of all possible Django built-in text styles.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Show Django\'s built-in text styles. Used for easy color reference when building new manage.py commands.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.stdout.write('')
        self.stdout.write('Available styles to use for text formatting.')
        self.stdout.write('These come built into Django, and are how django manage.py commands output with color.')
        self.stdout.write('For syntax, consult the "displaystyles.py" file located at "/cae_home/management/commands/"')
        self.stdout.write('')
        self.stdout.write(self.style.ERROR('Style ERROR'))
        self.stdout.write(self.style.NOTICE('Style NOTICE'))
        self.stdout.write(self.style.SUCCESS('Style SUCCESS'))
        self.stdout.write(self.style.WARNING('Style WARNING'))
        self.stdout.write(self.style.SQL_FIELD('Style SQL_FIELD'))
        self.stdout.write(self.style.SQL_COLTYPE('Style SQL_COLTYPE'))
        self.stdout.write(self.style.SQL_KEYWORD('Style SQL_KEYWORD'))
        self.stdout.write(self.style.SQL_TABLE('Style SQL_TABLE'))
        self.stdout.write(self.style.HTTP_INFO('Style HTTP_INFO'))
        self.stdout.write(self.style.HTTP_SUCCESS('Style HTTP_SUCCESS'))
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('Style HTTP_NOT_MODIFIED'))
        self.stdout.write(self.style.HTTP_REDIRECT('Style HTTP_REDIRECT'))
        self.stdout.write(self.style.HTTP_BAD_REQUEST('Style HTTP_BAD_REQUEST'))
        self.stdout.write(self.style.HTTP_SERVER_ERROR('Style HTTP_SERVER_ERROR'))
        self.stdout.write(self.style.MIGRATE_HEADING('Style MIGRATE_HEADING'))
        self.stdout.write(self.style.MIGRATE_LABEL('Style MIGRATE_LABEL'))
        self.stdout.write('')
        self.stdout.write('Note that commands should use "self.stdout.write" instead of the standard "print" call.')
        self.stdout.write('Stdout makes it easier to capture and compare output, such as during a unittest.')
        self.stdout.write('')
