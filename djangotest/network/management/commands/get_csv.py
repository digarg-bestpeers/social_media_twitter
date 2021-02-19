from django.core.management.base import BaseCommand
import csv
from io import StringIO
from social.settings import EMAIL_HOST_USER
from django.core.mail import send_mail, EmailMessage
from network.models import User


class Command(BaseCommand):
  help = 'send csv report in email'

  def add_arguments(self, parser):
    parser.add_argument('emailid', type=str, help='Indicates email on which report send')

  def handle(self, *args, **kwargs):
    emailid = kwargs['emailid']
    subject = 'Social Media User Report'
    content = 'hi...please find attached.'
    email = EmailMessage(subject,content,EMAIL_HOST_USER,[emailid])
    attachment_csv_file = StringIO()
    writer = csv.writer(attachment_csv_file)
    writer.writerow(['Username', 'Email', 'Total Posts', 'Total Likes', 'Total Followers'])
    for user in User.objects.all():
      writer.writerow([user.username, user.email, user.total_posts_per_user, user.post_likes.count(), user.user_profile.total_followers])
    email.attach('summary.csv', attachment_csv_file.getvalue(), 'text/csv')
    email.send(fail_silently=False)
