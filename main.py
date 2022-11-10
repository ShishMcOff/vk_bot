import praw
import requests
import shutil
import json
import os
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkUpload
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


with open('/Users/Home/PycharmProjects/reddit_bot/reddit_credentials.json') as file:
    reddit_parameters = json.load(file)

reddit = praw.Reddit(
    client_id=reddit_parameters['client_id'],
    client_secret=reddit_parameters['api_key'],
    password=reddit_parameters['password'],
    user_agent=reddit_parameters['user_agent'],
    username=reddit_parameters['username']
)

reddit_url = 'https://www.reddit.com'
subreddit = reddit.subreddit('dankmemes')


with open('/Users/Home/PycharmProjects/reddit_bot/vk_credentials.json') as file:
    vk_parameters = json.load(file)

authorize = vk_api.VkApi(token=vk_parameters['open_group_token'])
longpoll = VkLongPoll(authorize)
upload = VkUpload(authorize)


image_path = '/Users/Home/PycharmProjects/reddit_bot/memes/8.jpg'
memes_directory_path = '/Users/Home/PycharmProjects/reddit_bot/memes/'
project_directory_path = '/Users/Home/PycharmProjects/reddit_bot/'

generated_file_path = []

keyboard = VkKeyboard()
keyboard.add_button('post', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('next', color=VkKeyboardColor.PRIMARY)


def find_memes():
    # The following four-five lines are my first ever copy/paste from stackoverflow
    # It deletes all previous files (memes) in the folder, keeping it nice and clean
    if len(os.listdir(memes_directory_path)):
        for file in os.listdir(memes_directory_path):
            file_path = os.path.join(memes_directory_path, file)
            os.unlink(file_path)

    # count_file_name = 0

    for submission in subreddit.hot(limit=10):
        # count_file_name += 1
        # file_name = str(count_file_name)
        file_name = 'meme'

        submission_url = submission.url
        if submission_url.endswith('.jpg'):
            file_name += '.jpg'
            found = True
        elif submission_url.endswith('.png'):
            file_name += '.png'
            found = True
        else:
            found = False

        if found:
            request = requests.get(submission_url)
            with open(file_name, 'wb') as file:
                file.write(request.content)

            shutil.move(project_directory_path + file_name, memes_directory_path)
            generated_file_path.append(memes_directory_path + file_name)

            # post_info_file = str(count_file_name) + '.txt'
            post_info_file = 'meme.txt'

            try:
                with open(post_info_file, 'wt') as c:
                    c.write('Post title: ' + submission.title + '\n')
                    c.write('Permalink: ' + reddit_url + submission.permalink + '\n')
                    c.close()
            except:
                print(post_info_file, 'Error has occurred')

            shutil.move(project_directory_path + post_info_file, memes_directory_path)
            print(file_name, 'was generated')

            break


# The main loop
for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        received_message = event.text
        user_id = event.user_id

        if received_message == 'post':
            # Posting process to be implemented
            continue

        elif received_message == 'next':
            find_memes()
            upload_image = upload.photo_messages(photos=generated_file_path)[0]
            attachment = 'photo{}_{}'.format(upload_image['owner_id'], upload_image['id'])

            authorize.method('messages.send', {'user_id': user_id, 'random_id': get_random_id(),
                                               'attachment': attachment, 'keyboard': keyboard.get_keyboard()})

        else:
            message = 'There is no such option'
            authorize.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': get_random_id(),
                                               'keyboard': keyboard.get_keyboard()})
