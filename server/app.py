import re
import requests
import nltk
from nltk.corpus import cmudict
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import json
from collections import defaultdict
import string
import pronouncing
from flask import Flask, request, Response
from flask_cors import CORS
import random
from collections import OrderedDict
import concurrent.futures
import aiohttp
import asyncio

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        res = Response()
        res.headers['X-Content-Type-Options'] = '*'
        return res


async def async_get_related_words_from_website(session, input_word):
    url = f"https://relatedwords.io/{input_word}"
    headers = {
        'User-Agent': UserAgent().random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            main_column = soup.find('div', {'class': 'main-column'})
            term_list = main_column.find('ul', {'id': 'terms-list'})
            return [li.text.strip() for li in term_list.find_all('li')]
        else:
            print(
                f"Error: Unable to fetch data. Status code: {response.status}")
            return []


async def fetch_related_words(input_word):
    async with aiohttp.ClientSession() as session:
        return await async_get_related_words_from_website(session, input_word)


def get_song_lines(input_file_path):
    song_lines = []
    with open(input_file_path, 'r') as input_file:
        for line in input_file:
            # Append each line to the song_lines list (remove newline characters)
            song_lines.append(line.strip().lower())
    return song_lines

# get lines containing an input word


def get_lines(input_word, song_lines):
    # lines_with_input_word = [line for line in song_lines if input_word in line]
    regex_pattern = r'\b' + re.escape(input_word) + r'\b'
    lines_with_input_word = [
        line for line in song_lines if re.search(regex_pattern, line)]
    return lines_with_input_word


def get_related_words_from_website(input_word):
    url = f"https://relatedwords.io/{input_word}"

    user_agent = UserAgent()

    headers = {'User-Agent': user_agent.random}

    time.sleep(5)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the div with class "main-column"
        main_column = soup.find('div', {'class': 'main-column'})

        if main_column:
            # Find the ul with id "term-list" within the main column
            term_list = main_column.find('ul', {'id': 'terms-list'})

            if term_list:
                # Find all li tags within the term list
                related_words = [li.text.strip()
                                 for li in term_list.find_all('li')]
                return related_words
            else:
                print("Error: Unable to find the term list on the page.")
                return []
        else:
            print("Error: Unable to find the main column on the page.")
            return []

    else:
        print(
            f"Error: Unable to fetch data. Status code: {response.status_code}")
        return []

# Function to extract the first word from each line in a text file


def extract_first_words_from_file(file_path):
    first_words = []
    with open(file_path, 'r') as file:
        for line in file:
            words = line.lower().strip().split()

            if words:
                first_words.append(words[0])

    return first_words


def extract_last_word(line):
    words = line.split()
    if words:
        return words[-1]
    else:
        return None


def word_to_lines(input_file_path):
    word_to_lines_dict = {}

    with open(input_file_path, 'r') as input_file:
        for line in input_file:
            parts = line.strip().split(':')
            if len(parts) == 2:
                word, line_numbers = parts
                word = word.strip().lower()
                line_numbers = [int(num.strip())
                                for num in line_numbers.split(',')]

                if word in word_to_lines_dict:
                    word_to_lines_dict[word].extend(line_numbers)
                else:
                    word_to_lines_dict[word] = line_numbers

    return word_to_lines_dict


def get_phonetic_ending(word):
    d = cmudict.dict()

    word_lower = word.lower()

    pronunciation = d.get(word_lower)

    if pronunciation:
        # Return the last phoneme in the pronunciation
        return pronunciation[0][-1]
    else:
        return None

# TODO: define metric function. rhymability should be big factor


def metric_function_rhymability(line):
    print()

# returns line with best metric score


def get_best_line_tuple1(rap_lines, song_lines):
    best_line = None
    best_score = float('-inf')  # Initialize with negative infinity

    rap_line_lyrics = []
    for line_num in rap_lines:
        line = song_lines[line_num - 1]

        rap_line_lyrics.append(line)

        # score = metric_function_rhymability(line)
        score = 0
        if score > best_score:
            best_score = score
            best_line = line

    return random.choice(rap_line_lyrics)
    # return best_line


# TODO: returns the best line, considering the line before as well
def get_best_line_tuple2(previous_rhyme, rap_lines, song_lines):
    lines = []
    for line_num in rap_lines:
        line = song_lines[line_num - 1]
        lines.append(line)

    return random.choice(lines)


def compare_lines(line1, line2):
    last_word1 = extract_last_word(line1)
    last_word2 = extract_last_word(line2)

    last_word1.translate(str.maketrans('', '', string.punctuation))
    last_word2.translate(str.maketrans('', '', string.punctuation))

    # Get phonetic representations of the last words
    phones1 = pronouncing.phones_for_word(last_word1)
    phones2 = pronouncing.phones_for_word(last_word2)
    # Check for rhymes
    if phones1 and phones2:
        for phone1 in phones1:
            for phone2 in phones2:
                if pronouncing.rhyming_part(phone1) == pronouncing.rhyming_part(phone2):
                    return True
        if len(last_word1) < 3 or len(last_word2) < 3:
            return False
        return last_word1[-3:] == last_word2[-3:]
    else:
        return False


def get_first_tuple_line(related_word, word_to_lines_dict, song_lines):
    related_lines = word_to_lines_dict[related_word]

    lines = []
    for line_num in related_lines:
        line = song_lines[line_num - 1]
        lines.append(line)

    return get_best_line_tuple1(related_lines, song_lines)

# def get_second_tuple_line(previous_rhyme, related_lines, song_lines):
#     rhyme_compatible_lines = []

#     for line_num in related_lines:
#         line = song_lines[line_num]

#         if compare_lines(previous_rhyme, line):
#             rhyme_compatible_lines.append(line)

#     if rhyme_compatible_lines == []:
#         return []

#    return get_best_line_tuple2(previous_rhyme, rhyme_compatible_lines, song_lines)


def get_random_line_tuple1(related_lines_nums, song_lines, first_words):
    lines = []

    for line_num in related_lines_nums:
        line = song_lines[line_num - 1]
        last_word = extract_last_word(line)
        if last_word in first_words:
            lines.append(line)
    if lines == []:
        return ""

    return random.choice(lines)


def get_second_tuple_line(previous_rhyme, related_line_nums, song_lines):
    lines = []

    total_lines = []

    for line_num in related_line_nums:
        line = song_lines[line_num - 1]
        total_lines.append(line)

        if compare_lines(previous_rhyme, line):
            lines.append(line)
    if lines == []:
        return ""
    return random.choice(lines)


@app.route('/<input_word>', methods=['POST'])
def main(input_word):
    print("New request:", input_word)
    # Specify the path to the song_lines.txt file
    input_file_path = 'song_lines_processed_FINAL.txt'

    # List to store the lines from the file
    song_lines = get_song_lines(input_file_path)
    num_related_words = 80

    # related_words = get_related_words_from_website("beach")[:num_related_words]
    # split_words = [word for words in related_words for word in words.split()]
    # related_words = list(set(word for word in split_words if len(word.split()) == 1))

    file_path = 'cmudict-0.7b'
    first_word_list = extract_first_words_from_file(file_path)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    related_words = loop.run_until_complete(fetch_related_words(input_word))[
        :num_related_words]

    flattened_words = [
        word for words in related_words for word in words.split()]
    ordered_dict = OrderedDict.fromkeys(flattened_words)
    related_words = list(ordered_dict.keys())

    word_to_lines_dict = word_to_lines('word_to_lines_combined.txt')

    output_rap = []
    # generating rap
    # first_line = get_first_tuple_line(related_words[0], word_to_lines_dict, song_lines)
    # output_rap.append(first_line)

    # prev_rhyme = extract_last_word(first_line)

    prev_rhyme = ""
    i = 0
    print("Generating Rap")
    while len(output_rap) < 16 and i < len(related_words):
        curr_related_word = related_words[i]
        if len(curr_related_word) <= 2:
            i += 1
            continue
        if curr_related_word.lower() in word_to_lines_dict:
            related_line_nums = word_to_lines_dict[curr_related_word.lower()]
        else:
            i += 1
            continue

        if len(output_rap) % 2 == 0:  # first tuple
            line_retrieved = get_random_line_tuple1(
                related_line_nums, song_lines, first_word_list)

            if line_retrieved != "" and len(line_retrieved) < 80:
                output_rap.append(line_retrieved)
        else:  # second tuple
            line_retrieved = get_second_tuple_line(
                prev_rhyme, related_line_nums, song_lines)
            if line_retrieved != "" and len(line_retrieved) < 80:
                output_rap.append(line_retrieved)
        if line_retrieved != "":
            prev_rhyme = extract_last_word(line_retrieved)
        i += 1
    for line in output_rap:
        print(line)

    return json.dumps(output_rap)


if __name__ == "__main__":
    app.run(port=5001)
