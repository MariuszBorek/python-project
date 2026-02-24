import yagmail

yag = yagmail.SMTP(user='maniek10@gmail.com', password=r"TEST")

contents = [
    "This is the body, and here is just text http://somedomain/image.png",
    "You can find an audio file attached.", '/local/path/to/song.mp3'
]

# yag.send(
#     to='maniek10@gmail.com',
#     subject='Dostępne sloty',
#     contents=str("test body")
# )

yag.send('maniek10@gmail.com', 'subject', contents)

# # Alternatively, with a simple one-liner:
# yagmail.SMTP('maniek10@gmail.com').send('maniek10@gmail.com', 'subject', contents)