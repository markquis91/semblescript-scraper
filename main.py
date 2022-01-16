import argparse
from environs import Env

import crawler
import database


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--prospect', '-p', type=int)
    # parser.add_argument('--keywords', '-k')
    # parser.add_argument('--first_name', '-f')
    # parser.add_argument('--last_name', '-l')
    # parser.add_argument('--company', '-c')
    #
    # args = parser.parse_args()
    # company = args.company
    # first_name = args.first_name
    # last_name = args.last_name
    # keywords = args.keywords
    # prospect_id = args.prospect

    env = Env()
    env.read_env()

    host = env.str('DB_HOST', "127.0.0.1")
    port = env.int('DB_PORT', 3306)
    user = env.str('DB_USERNAME', "root")
    password = env.str('DB_PASSWORD', "")
    db_name = env.str('DB_DATABASE', "semble")

    semble_schema = database.SembleSchema(host, port, user, password, db_name)

    tasks = semble_schema.get_crawl_tasks()
    for task in tasks:
        prospect_id = task['prospect_id']
        company = task['company']
        first_name = task['first_name']
        last_name = task['last_name']

        last_id = semble_schema.get_last_post_id(prospect_id)

        crawl = crawler.Crawler()

        email = env("LINKEDIN_USER")
        password = env("LINKEDIN_PASSWORD")

        crawl.login(email, password)

        base_url = 'https://www.linkedin.com/search/results/people/'
        url = base_url + '?company={}&firstName={}&lastName={}&origin=FACETED_SEARCH&sid=_5C'.format(company, first_name,
                                                                                                     last_name)

        profile_url = crawl.get_profile(url)

        title = crawl.get_title(profile_url)
        about = crawl.get_about(profile_url)
        experiences = crawl.get_experiences(profile_url)
        educations = crawl.get_educations(profile_url)
        skills = crawl.get_skills(profile_url)
        posts = crawl.get_posts(profile_url, last_id)

        profile_id = semble_schema.insert_profile(title, about, prospect_id)
        semble_schema.insert_experiences(profile_id, experiences)
        semble_schema.insert_educations(profile_id, educations)
        semble_schema.insert_skills(profile_id, skills)
        semble_schema.insert_posts(profile_id, posts)
