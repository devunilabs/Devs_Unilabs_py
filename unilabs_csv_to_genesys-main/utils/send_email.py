import smtplib
from aiosmtplib import SMTP
from email.message import EmailMessage
from logging import Logger


def send_mail(mail_config: dict, subject: str, body: str, logger: Logger) -> None:
    """
    Function to send an email via an SMTP service
    :param mail_config: Dict with the SMTP attributes tu send the mail
    :param subject: Email's subject
    :param body: Email's message
    :param logger: Logger object
    :return: None
    """
    if not mail_config['enable']:
        logger.debug('El envío de email no está habilitado')
        return None

    port = mail_config['port']
    smtp_server = mail_config['smtp_server']
    sender_email = mail_config['sender_email']
    receiver_email = mail_config['receiver_email']
    password = mail_config['password']
    message = f'Subject: {subject}\n\n{body}'

    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.encode("ISO-8859-1"))
            logger.debug('Email enviado')
    except Exception as error:
        print(error)
        logger.error(f'Error enviando email: {str(error)}')


async def async_send_email(mail_config: dict, subject: str, body: str, logger: Logger):
    try:
        message = EmailMessage()
        message["From"] = mail_config['sender_email']
        message["To"] = mail_config['receiver_email']
        message["Subject"] = subject
        message.set_content(str(body))

        smtp_client = SMTP(hostname=mail_config['smtp_server'], port=mail_config['port'],
                           username=mail_config['sender_email'], password=mail_config['password'])
        async with smtp_client:
            await smtp_client.send_message(message)
            logger.debug('Email enviado')
    except Exception as error:
        logger.error(f'Error enviando email: {str(error)}')
